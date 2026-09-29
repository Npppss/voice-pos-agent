"""
Payment service — interfaces with payment gateway (Midtrans / Xendit / Stripe).
"""


async def process_payment(amount: float, method: str, reference: str) -> dict:
    """
    Process a payment transaction.

    Args:
        amount: Payment amount in IDR
        method: Payment method (qris, cash, card, ewallet)
        reference: Transaction reference ID

    Returns:
        Dict with 'success' (bool) and 'transaction_id'.
    """
    # TODO: Integrate with actual payment gateway (Midtrans / Xendit)
    # For now, simulate a successful payment
    return {
        "success": True,
        "transaction_id": reference,
        "method": method,
        "amount": amount,
    }
