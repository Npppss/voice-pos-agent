# AI-Powered Cashier — Odoo Integration

An intelligent voice-driven Point-of-Sale system that converts spoken food orders into structured Odoo sales orders using Speech-to-Text and RAG-based menu matching.

---

## Features

- **Voice-first ordering** — Cashiers speak naturally, no manual menu browsing
- **RAG menu matching** — Handles colloquial, regional, and abbreviated food names
- **Odoo-native** — Sales orders, inventory, and accounting managed entirely in Odoo
- **Real-time processing** — Audio streaming via WebSocket for low-latency transcription
- **Parallel post-payment** — Inventory deduction, accounting logs, and receipt delivery run concurrently
- **Multi-channel receipts** — Kitchen thermal printer + customer email receipt

---

## Architecture Overview

```
Mobile App → Backend API → STT Engine → AI Agent → RAG Librarian → Odoo ERP
                                                                      ↓
                                                              Payment Gateway
                                                                      ↓
                                                    ┌─────────────────┼─────────────────┐
                                                    │                 │                 │
                                              Inventory         Accounting        Delivery
                                             (stock.move)     (account.move)   (Printer + Email)
```

See [`docs/Architecture.md`](docs/Architecture.md) for full diagrams and details.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile | Flutter / React Native |
| Backend | FastAPI (Python) |
| STT | OpenAI Whisper |
| AI | LangChain + Gemini/GPT |
| Vector DB | ChromaDB |
| ERP | Odoo 17+ Community |
| Database | PostgreSQL |
| Payment | Midtrans / Xendit |
| Deployment | Docker Compose |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Odoo 17+ instance (local or remote)
- Node.js 18+ (for mobile app development)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd AMD-Lomba
cp .env.example .env
# Edit .env with your Odoo credentials, API keys, etc.
```

### 2. Start Services

```bash
docker-compose up -d
```

This starts:
- Backend API (port 8000)
- Whisper STT service
- ChromaDB vector store
- Odoo + PostgreSQL (if using local Odoo)

### 3. Seed Menu Data

```bash
python scripts/seed_menu_embeddings.py
```

Pulls products from Odoo and indexes them into the vector database.

### 4. Run Mobile App

```bash
cd mobile
flutter pub get
flutter run
```

---

## Project Structure

```
AMD-Lomba/
├── README.md
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── Architecture.md          # System architecture & diagrams
│   ├── API.md                   # API endpoint specification
│   ├── Database-Schema.md       # Data models & schema
│   ├── RAG-Pipeline.md          # RAG embedding & retrieval strategy
│   └── Deployment.md            # Deployment & infrastructure guide
├── backend/
│   ├── main.py                  # FastAPI entrypoint
│   ├── requirements.txt         # Python dependencies
│   ├── config.py                # Environment & app configuration
│   ├── routers/
│   │   ├── audio.py             # WebSocket audio streaming endpoint
│   │   └── orders.py            # Order management REST endpoints
│   ├── services/
│   │   ├── stt_service.py       # Speech-to-Text integration
│   │   ├── ai_agent.py          # AI Agent (LLM orchestrator)
│   │   ├── rag_librarian.py     # RAG menu matcher
│   │   ├── odoo_client.py       # Odoo XML-RPC / JSON-RPC client
│   │   ├── payment_service.py   # Payment gateway integration
│   │   ├── printer_service.py   # ESC/POS kitchen printer
│   │   └── email_service.py     # Email receipt delivery
│   └── models/
│       ├── order.py             # Order data models
│       └── product.py           # Product / SKU models
├── mobile/                      # Flutter / React Native mobile app
├── scripts/
│   └── seed_menu_embeddings.py  # Seed vector DB with Odoo products
└── tests/
    ├── test_stt.py
    ├── test_rag.py
    ├── test_odoo.py
    └── test_orders.py
```

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](docs/Architecture.md) | System diagrams, layer breakdown, deployment topology |
| [API Spec](docs/API.md) | REST & WebSocket endpoint contracts |
| [Database Schema](docs/Database-Schema.md) | Odoo models, vector DB collections |
| [RAG Pipeline](docs/RAG-Pipeline.md) | Embedding strategy, retrieval tuning |
| [Deployment](docs/Deployment.md) | Docker Compose, environment variables, production setup |

---

## License

This project is developed for the AMD Lomba competition.
