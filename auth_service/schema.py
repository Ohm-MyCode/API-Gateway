from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    email:EmailStr
    password:str = Field(min_length = 4)

class CreateUser(BaseModel):
    email:EmailStr
    password:str = Field(min_length = 4)
    name:str = Field(min_length = 1)