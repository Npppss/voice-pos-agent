"""
Odoo XML-RPC client for sales order management.
"""

import xmlrpc.client
from config import settings
from models.order import OrderItem


class OdooClient:
    """Client for communicating with Odoo via XML-RPC."""

    def __init__(self):
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.username = settings.ODOO_USER
        self.password = settings.ODOO_PASSWORD
        self._uid = None

    @property
    def uid(self) -> int:
        """Authenticate and cache the user ID."""
        if self._uid is None:
            common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self._uid = common.authenticate(self.db, self.username, self.password, {})
            if not self._uid:
                raise ConnectionError("Odoo authentication failed")
        return self._uid

    @property
    def models(self):
        """Get the models endpoint proxy."""
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def _execute(self, model: str, method: str, *args, **kwargs):
        """Execute an Odoo RPC call."""
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, *args, **kwargs,
        )

    async def create_sale_order(
        self,
        session_id: str,
        items: list[OrderItem],
        customer_email: str | None = None,
    ) -> dict:
        """Create a draft sale.order in Odoo."""
        order_lines = []
        for item in items:
            order_lines.append((0, 0, {
                "product_id": item.product_id,
                "product_uom_qty": item.quantity,
            }))

        order_id = self._execute(
            "sale.order", "create",
            [{
                "order_line": order_lines,
                "x_session_id": session_id,
            }],
        )

        return await self.get_sale_order(str(order_id))

    async def get_sale_order(self, order_id: str) -> dict | None:
        """Fetch a sale.order by ID."""
        try:
            oid = int(order_id)
        except ValueError:
            return None

        orders = self._execute(
            "sale.order", "read",
            [[oid]],
            {"fields": ["name", "state", "amount_total", "order_line",
                        "date_order", "x_session_id"]},
        )
        if not orders:
            return None

        order = orders[0]
        lines = self._execute(
            "sale.order.line", "read",
            [order["order_line"]],
            {"fields": ["product_id", "product_uom_qty", "price_unit",
                        "price_subtotal"]},
        )

        return {
            "order_id": order["name"],
            "odoo_order_id": oid,
            "status": "draft" if order["state"] == "draft" else order["state"],
            "items": [
                {
                    "product_id": line["product_id"][0],
                    "name": line["product_id"][1],
                    "quantity": line["product_uom_qty"],
                    "unit_price": line["price_unit"],
                    "subtotal": line["price_subtotal"],
                }
                for line in lines
            ],
            "total": order["amount_total"],
            "created_at": order.get("date_order"),
        }

    async def update_sale_order(self, order_id: str, items: list[OrderItem]) -> dict:
        """Update order lines on a draft sale.order."""
        oid = int(order_id)

        # Remove existing lines
        existing = self._execute(
            "sale.order", "read", [[oid]], {"fields": ["order_line"]},
        )
        if existing and existing[0].get("order_line"):
            for line_id in existing[0]["order_line"]:
                self._execute("sale.order.line", "unlink", [[line_id]])

        # Add new lines
        new_lines = [(0, 0, {
            "product_id": item.product_id,
            "product_uom_qty": item.quantity,
        }) for item in items]

        self._execute("sale.order", "write", [[oid], {"order_line": new_lines}])
        return await self.get_sale_order(order_id)

    async def confirm_sale_order(self, order_id: str):
        """
        Confirm a sale.order in Odoo.
        This triggers Odoo's built-in workflows:
        - stock.move creation (inventory deduction)
        - account.move creation (accounting journal entry)
        """
        oid = int(order_id)
        self._execute("sale.order", "action_confirm", [[oid]])

    async def list_sale_orders(
        self,
        status: str = "all",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List sale.orders with optional filtering."""
        domain = []
        if status != "all":
            domain.append(["state", "=", status])

        order_ids = self._execute(
            "sale.order", "search",
            [domain],
            {"limit": limit, "offset": offset, "order": "id desc"},
        )

        if not order_ids:
            return []

        orders = self._execute(
            "sale.order", "read",
            [order_ids],
            {"fields": ["name", "state", "amount_total", "date_order"]},
        )

        return [
            {
                "order_id": o["name"],
                "status": o["state"],
                "total": o["amount_total"],
                "created_at": o.get("date_order"),
            }
            for o in orders
        ]
