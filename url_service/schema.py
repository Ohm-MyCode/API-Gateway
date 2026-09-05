from pydantic import BaseModel, ConfigDict, field_validator


class GetUrlModel(BaseModel):
    url:str
    @field_validator("url")
    @classmethod
    def add_scheme(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            return f"https://{value}"
        return value

class ReturnUrlModel(BaseModel):
    original_url:str
    shortcode:str
    model_config = ConfigDict(from_attributes=True)