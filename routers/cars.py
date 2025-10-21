from bson import ObjectId
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from pymongo import ReturnDocument
import cloudinary
from cloudinary import uploader # noqa: F401
from carbackend.models.authentication import AuthHandler
from config import BaseConfig
from models import CarCollection, CarCollectionPagination, CarModel, UpdateCarModel

settings = BaseConfig()

CARS_PER_PAGE = 10

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_SECRET_KEY,
)


router = APIRouter()

@router.post(
    "/",
    response_description="Add new car with picture",
    response_model=CarModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_car_with_picture(
    request: Request,
    brand: str = Form(...),
    make: str = Form(...),
    year: int = Form(...),
    cm3: int = Form(...),
    km: int = Form(...),
    price: int = Form(...),
    picture: UploadFile = File(...),
    user: str = Depends(AuthHandler.auth_wrapper),
):
    
    cloudinary_image = cloudinary.uploader.upload(
        picture.file,
        folder="FARM2",
        crop="fill",
        width=800
    )
    picture_url = cloudinary_image["url"]

    car = CarModel(
        brand=brand,
        make=make,
        year=year,
        cm3=cm3,
        km=km,
        price=price,
        picture_url=picture_url,
        user_id=user["user_id"]
    )

    cars = request.app.db["cars"]
    document = car.model_dump(by_alias=True, exclude=["id"])
    inserted = await cars.insert_one(document)

    return await cars.find_one({"_id": inserted.inserted_id})

@router.get(
    "/",
    response_description="List all cars",
    response_model=CarCollection,
    response_model_by_alias=False,
)
async def list_cars(request: Request):
    cars = request.app.db["cars"]
    results = []
    cursor = cars.find()
    async for document in cursor:
        results.append(document)
    return CarCollection(cars=results)

@router.get(
        "/{id}",
        response_description="Get a single car by ID",
        response_model=CarModel,
        response_model_by_alias=False,
)

async def show_car(id: str, request: Request):
    cars = request.app.db["cars"]
    try:
        id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Car {id} not found")

    if (car := await cars.find_one({"_id": id})) is not None:
        return car

    raise HTTPException(status_code=404, detail=f"Car with {id} not found")
