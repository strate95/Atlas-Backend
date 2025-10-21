from typing import Optional, Annotated, List
from pydantic import BaseModel, ConfigDict, Field, BeforeValidator, field_validator
PyObjectId = Annotated[str, BeforeValidator(str)]

class CarModel(BaseModel):
    id: Optional[PyObjectId] = Field(
        alias="_id", default=None)
    brand: str = Field(...)
    make: str = Field(...)
    year: int = Field(..., gt=1970, lt=2025)
    cm3: int = Field(..., gt=0, lt=5000)
    km: int = Field(..., gt=0, lt=500000)
    price: int = Field(..., gt=0, lt=100000)
    user_id: str = Field(...)
    picture_url: Optional[str] = Field(None)

class UpdateCarModel(BaseModel):
    brand: Optional[str] = Field(...)
    make: Optional[str] = Field(...)
    year: Optional[int] = Field(..., gt=1970, lt=2025)
    cm3: Optional[int] = Field(..., gt=0, lt=5000)
    km: Optional[int] = Field(..., gt=0, lt=500 * 1000)
    price: Optional[int] = Field(..., gt=0, lt=100 * 1000)

class CarCollection(BaseModel):
    cars: List[CarModel]

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=15)
    password: str = Field(...)


class LoginModel(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class CurrentUserModel(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=15)

@field_validator("brand")
@classmethod
def check_brand_case(cls, v: str) -> str:
    return v.title()

@field_validator("make")
@classmethod
def check_make_case(cls, v: str) -> str:
    return v.title()

model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
    json_schema_extra={
        "example": {
            "brand": "Ford",
            "make": "Fiesta",
            "year": 2019,
            "cm3": 1500,
            "km": 120000,
            "price": 10000,
            "picture_url": "https://images.pexels.com/photos/2086676/pexels-photo-2086676.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260"
        }
    },
)
"""
test_car = CarModel(
    brand="ford", make="fiesta", year=2019, cm3=1500, km=120000, price=10000
)
print(test_car.model_dump())
"""