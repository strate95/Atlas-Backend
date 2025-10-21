from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from authentication import AuthHandler
from models import CurrentUserModel, LoginModel, UserModel

router = APIRouter()
auth_handler = AuthHandler()


@router.post("/register", response_description="Register user")
async def register(request: Request, newUser: LoginModel = Body(...)) -> UserModel:
    users = request.app.db["users"]

    # hash the password before inserting it into MongoDB
    newUser.password = auth_handler.get_password_hash(newUser.password)
    newUser = newUser.model_dump()

    # check existing username — 409 Conflict
    existing_username = await users.find_one({"username": newUser["username"]})
    if existing_username is not None:
        raise HTTPException(
            status_code=409,
            detail=f"User with username {newUser['username']} already exists",
        )

    new_user = await users.insert_one(newUser)
    created_user = await users.find_one({"_id": new_user.inserted_id})
    return created_user


@router.post("/login", response_description="Login user")
async def login(request: Request, loginUser: LoginModel = Body(...)) -> JSONResponse:
    users = request.app.db["users"]
    user = await users.find_one({"username": loginUser.username})

    if (user is None) or (
        not auth_handler.verify_password(loginUser.password, user["password"])
    ):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")

    token = auth_handler.encode_token(str(user["_id"]), user["username"])

    response = JSONResponse(
        content={
            "token": token,
            "username": user["username"]
        }
    )
    return response

@router.get(
    "/me",
    response_description="Logged in user data",
    response_model=CurrentUserModel
)
async def me(
    request: Request,
    response: Response,
    user_data=Depends(auth_handler.auth_wrapper)
):
    users = request.app.db["users"]
    current_user = await users.find_one(
        {"_id": ObjectId(user_data["user_id"])}
    )

    return current_user