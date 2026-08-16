from pydantic import BaseModel,Field,ConfigDict

class GetUrlModel(BaseModel):
    url:str

class ReturnUrlModel(BaseModel):
    original_url:str
    shortcode:str
    model_config = ConfigDict(from_attributes=True)