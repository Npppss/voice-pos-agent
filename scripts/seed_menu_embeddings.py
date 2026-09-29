"""
Seed script — pulls products from Odoo and indexes them into ChromaDB.

Usage:
    python scripts/seed_menu_embeddings.py
"""

import xmlrpc.client
import chromadb
from sentence_transformers import SentenceTransformer

# --- Configuration (reads from env or uses defaults) ---
import os

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo_cashier")
ODOO_USER = os.getenv("ODOO_USER", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8100"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")


def build_document(product: dict) -> str:
    """Build a searchable text document from product fields."""
    parts = [
        product.get("name", ""),
        product.get("x_aliases", "") or "",
        product["categ_id"][1] if product.get("categ_id") else "",
        product.get("x_description_ai", "") or "",
    ]
    return " | ".join(filter(None, parts))


def main():
    print("Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        print("Odoo authentication failed!")
        return

    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    print("Fetching products from Odoo...")
    products = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "product.product", "search_read",
        [[["active", "=", True], ["sale_ok", "=", True]]],
        {"fields": ["name", "default_code", "list_price", "categ_id",
                     "x_aliases", "x_description_ai"]},
    )
    print(f"Found {len(products)} products")

    if not products:
        print("No products found. Add products in Odoo first.")
        return

    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = chroma_client.get_or_create_collection("menu_items")

    print("Indexing products...")
    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for product in products:
        doc = build_document(product)
        embedding = model.encode(f"passage: {doc}").tolist()

        product_id = product["id"]
        ids.append(f"product_{product_id}")
        embeddings.append(embedding)
        documents.append(doc)
        metadatas.append({
            "product_id": product_id,
            "sku": product.get("default_code", ""),
            "name": product["name"],
            "price": product.get("list_price", 0),
            "category": product["categ_id"][1] if product.get("categ_id") else "",
        })

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Indexed {len(ids)} products into ChromaDB collection 'menu_items'")
    print("Done.")


if __name__ == "__main__":
    main()
