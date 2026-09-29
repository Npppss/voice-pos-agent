"""
REST endpoints for order management (CRUD + payment confirmation).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.order import OrderItem, OrderResponse, PaymentRequest, PaymentResponse
from services.odoo_client import OdooClient
from services.payment_service import process_payment
from services.printer_service import print_kitchen_receipt
from services.email_service import send_email_receipt

router = APIRouter()
odoo = OdooClient()


class CreateOrderRequest(BaseModel):
    session_id: str
    items: list[OrderItem]
    customer_email: str | None = None


class UpdateOrderRequest(BaseModel):
    items: list[OrderItem]


@router.post("/orders", status_code=201, response_model=OrderResponse)
async def create_order(request: CreateOrderRequest):
    """Create a draft sales order in Odoo."""
    try:
        order = await odoo.create_sale_order(
            session_id=request.session_id,
            items=request.items,
            customer_email=request.customer_email,
        )
        return order
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Odoo error: {str(e)}")


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """Retrieve order details by ID."""
    order = await odoo.get_sale_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/orders/{order_id}", response_model=OrderResponse)
async def update_order(order_id: str, request: UpdateOrderRequest):
    """Update a draft order's items."""
    order = await odoo.get_sale_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.get("status") != "draft":
        raise HTTPException(status_code=409, detail="Cannot modify a confirmed order")

    updated = await odoo.update_sale_order(order_id, request.items)
    return updated


@router.post("/orders/{order_id}/confirm", response_model=PaymentResponse)
async def confirm_order(order_id: str, request: PaymentRequest):
    """
    Validate payment and trigger post-payment workflows:
    1. Inventory stock deduction (stock.move)
    2. Accounting journal entry (account.move)
    3. Kitchen receipt printing (ESC/POS)
    4. Email receipt to customer
    """
    order = await odoo.get_sale_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.get("status") != "draft":
        raise HTTPException(status_code=409, detail="Order already confirmed")

    # Step 1: Process payment
    payment_result = await process_payment(
        amount=request.amount,
        method=request.payment_method,
        reference=request.payment_reference,
    )
    if not payment_result.get("success"):
        raise HTTPException(status_code=402, detail="Payment failed")

    # Step 2: Confirm order in Odoo (triggers inventory + accounting)
    await odoo.confirm_sale_order(order_id)

    # Step 3: Post-payment actions (parallel in production)
    kitchen_ok = await print_kitchen_receipt(order)
    email_ok = await send_email_receipt(order)

    return PaymentResponse(
        order_id=order_id,
        status="confirmed",
        payment={
            "method": request.payment_method,
            "reference": request.payment_reference,
            "status": "success",
        },
        post_payment={
            "inventory_deducted": True,
            "accounting_logged": True,
            "kitchen_printed": kitchen_ok,
            "email_sent": email_ok,
        },
    )


@router.get("/orders")
async def list_orders(
    status: str = "all",
    limit: int = 50,
    offset: int = 0,
):
    """List orders with optional status filter and pagination."""
    orders = await odoo.list_sale_orders(status=status, limit=limit, offset=offset)
    return {"orders": orders, "total": len(orders)}
