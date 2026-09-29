"""
AI Agent — LLM orchestrator that parses transcriptions and builds orders.
"""

from config import settings
from services.rag_librarian import match_menu_items


async def process_transcription(text: str, session_id: str) -> dict:
    """
    Process transcribed speech through the AI Agent pipeline:
    1. Parse the transcription to extract item names and quantities
    2. Use RAG Librarian to resolve items to Odoo product SKUs
    3. Return structured order data

    Args:
        text: Transcribed speech text
        session_id: Session identifier for tracking

    Returns:
        Structured order dict with resolved product SKUs and quantities.
    """
    # Step 1: Parse intent — extract items and quantities from natural language
    # In production, this calls the LLM to parse structured data from free text.
    # Example input:  "satu nasi goreng spesial sama dua es teh manis"
    # Example output: [{"name": "nasi goreng spesial", "qty": 1},
    #                  {"name": "es teh manis", "qty": 2}]
    parsed_items = await _parse_order_intent(text)

    # Step 2: Resolve each item via RAG Librarian
    resolved_items = []
    for item in parsed_items:
        matches = await match_menu_items(item["name"])
        if matches:
            best = matches[0]
            resolved_items.append({
                "product_id": best["product_id"],
                "sku": best["sku"],
                "name": best["name"],
                "quantity": item["qty"],
                "unit_price": best["price"],
                "subtotal": best["price"] * item["qty"],
            })

    total = sum(item["subtotal"] for item in resolved_items)

    return {
        "session_id": session_id,
        "items": resolved_items,
        "total": total,
        "odoo_order_id": None,
        "status": "draft",
    }


async def _parse_order_intent(text: str) -> list[dict]:
    """
    Use LLM to extract structured item+quantity pairs from free-form speech.

    In production, this sends a prompt to the configured LLM (Gemini/GPT)
    with instructions to parse Indonesian food order speech.

    Returns:
        List of dicts with 'name' (str) and 'qty' (int).
    """
    # TODO: Replace with actual LLM call
    # Placeholder: returns the raw text as a single item
    return [{"name": text.strip(), "qty": 1}]
