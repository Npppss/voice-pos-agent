"""
Kitchen printer service — sends ESC/POS commands to thermal printer.
"""

import socket
from config import settings


async def print_kitchen_receipt(order: dict) -> bool:
    """
    Print a kitchen receipt via ESC/POS over TCP.

    Args:
        order: Order data dict with items and total.

    Returns:
        True if print was successful, False otherwise.
    """
    try:
        receipt = _build_receipt(order)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((settings.PRINTER_IP, settings.PRINTER_PORT))
        sock.sendall(receipt.encode("utf-8"))
        sock.close()

        return True

    except (socket.error, OSError) as e:
        print(f"Kitchen printer error: {e}")
        return False


def _build_receipt(order: dict) -> str:
    """Build a plain-text receipt string for the kitchen."""
    lines = []
    lines.append("=" * 32)
    lines.append("    KITCHEN ORDER")
    lines.append("=" * 32)
    lines.append(f"Order: {order.get('order_id', 'N/A')}")
    lines.append("-" * 32)

    for item in order.get("items", []):
        qty = int(item.get("quantity", 1))
        name = item.get("name", "Unknown")
        lines.append(f"  {qty}x  {name}")

    lines.append("-" * 32)
    lines.append(f"Total: Rp {order.get('total', 0):,.0f}")
    lines.append("=" * 32)
    lines.append("\n\n\n")  # Feed paper

    return "\n".join(lines)
