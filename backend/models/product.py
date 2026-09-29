"""
Data models for products and SKUs.
"""

from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    sku: str
    price: float
    category: str | None = None
    aliases: str | None = None
    description_ai: str | None = None
    active: bool = True
