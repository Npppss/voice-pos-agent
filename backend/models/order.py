"""
Data models for orders and products.
"""

from pydantic import BaseModel
from datetime import datetime


class OrderItem(BaseModel):
    product_id: int
    quantity: int = 1


class OrderLineResponse(BaseModel):
    product_id: int
    sku: str | None = None
    name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    order_id: str
    odoo_order_id: int
    status: str
    items: list[OrderLineResponse]
    total: float
    created_at: str | None = None


class PaymentRequest(BaseModel):
    payment_method: str
    payment_reference: str
    amount: float


class PaymentResponse(BaseModel):
    order_id: str
    status: str
    payment: dict
    post_payment: dict
