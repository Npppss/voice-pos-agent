"""
Email service — sends receipt emails to customers via SMTP.
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import settings


async def send_email_receipt(order: dict) -> bool:
    """
    Send an HTML receipt email to the customer.

    Args:
        order: Order data dict with items, total, and customer email.

    Returns:
        True if email was sent successfully, False otherwise.
    """
    customer_email = order.get("customer_email")
    if not customer_email or not settings.SMTP_USER:
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Receipt — Order {order.get('order_id', '')}"
        msg["From"] = settings.SMTP_USER
        msg["To"] = customer_email

        html_body = _build_html_receipt(order)
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )
        return True

    except Exception as e:
        print(f"Email send failed: {e}")
        return False


def _build_html_receipt(order: dict) -> str:
    """Build an HTML receipt email body."""
    items_html = ""
    for item in order.get("items", []):
        qty = int(item.get("quantity", 1))
        name = item.get("name", "Unknown")
        subtotal = item.get("subtotal", 0)
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{name}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{qty}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">Rp {subtotal:,.0f}</td>
        </tr>"""

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Order Receipt</h2>
        <p>Order ID: <strong>{order.get('order_id', 'N/A')}</strong></p>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f5f5f5;">
                    <th style="padding: 8px; text-align: left;">Item</th>
                    <th style="padding: 8px; text-align: center;">Qty</th>
                    <th style="padding: 8px; text-align: right;">Subtotal</th>
                </tr>
            </thead>
            <tbody>{items_html}</tbody>
        </table>
        <p style="font-size: 18px; font-weight: bold; text-align: right; margin-top: 16px;">
            Total: Rp {order.get('total', 0):,.0f}
        </p>
        <p style="color: #888; font-size: 12px;">Thank you for your order.</p>
    </body>
    </html>
    """
