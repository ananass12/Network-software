from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


Quality = Literal["новый", "потрепанный", "использованный", "сломанный"]

SAFE_TEXT_PATTERN = r"^[\w\s\-\.,!?:;()\"'«»]+$"


class ProductBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80, pattern=SAFE_TEXT_PATTERN)
    description: Optional[str] = Field(default=None, max_length=500, pattern=SAFE_TEXT_PATTERN)
    quality: Quality
    quantity: int = Field(ge=0, le=1_000_000)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True