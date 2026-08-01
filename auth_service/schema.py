from pydantic import BaseModel,EmailStr

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class CreateUser(BaseModel):
    email:EmailStr
    password:str
    name:str