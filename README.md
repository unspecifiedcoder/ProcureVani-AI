# ProcureVani

Voice-First Agentic WhatsApp + Blockchain Co-Pilot for MSME GeM Compliance.

ProcureVani enables MSMEs with zero digital literacy to achieve PPP-MII compliance and generate GeM-ready submission packages in under 5 minutes, using WhatsApp voice notes in Telugu, Hindi, or English.

## Architecture

The system is composed of four main layers. The entry layer receives WhatsApp messages via the Meta Business Cloud API, transcribes voice notes and OCRs bill images using Google Gemini. The agent orchestration layer uses a LangGraph multi-agent pipeline to classify intents, extract structured data, run compliance checks, generate declaration documents, and flag fraud. The blockchain layer anchors compliance passports on the Polygon network via a Solidity smart contract, with declarations pinned to IPFS through Pinata. The data layer uses Supabase (Postgres) for structured records and Redis for session caching.

## Quick Start

### Prerequisites

Python 3.11 or later, Node.js 18 or later, and Git are required. Docker is optional but recommended for running Redis and Postgres locally.

### Backend Setup

```bash
git clone https://github.com/yourusername/procurevani
cd procurevani

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

copy .env.example .env
# Edit .env with your API keys
```

### Run the Backend

```bash
uvicorn apps.webhook.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. The interactive docs are at `http://localhost:8000/docs`.

### Test Without WhatsApp

You can simulate WhatsApp conversations using the built-in test endpoint:

```bash
curl -X POST http://localhost:8000/test/message \
  -H "Content-Type: application/json" \
  -d '{"wa_id": "test_user", "message": "hello"}'
```

This returns the bot reply and session state directly. No WhatsApp API credentials are needed for development.

### Run the Dashboard

```bash
cd apps/dashboard
npm install
npm run dev
```

The auditor dashboard will be available at `http://localhost:3000`.

### Configuration

Copy `.env.example` to `.env` and fill in the credentials you have. The system gracefully degrades when credentials are missing: without a Gemini key, intent classification falls back to keyword matching; without Polygon credentials, passport issuance returns mock responses; without Pinata, IPFS pinning is skipped.

Required for full functionality:
- `GEMINI_API_KEY` from https://ai.google.dev
- `WA_ACCESS_TOKEN` and `WA_PHONE_NUMBER_ID` from https://developers.facebook.com
- `POLYGON_RPC_URL`, `PRIVATE_KEY`, and `CONTRACT_ADDRESS` for blockchain anchoring
- `PINATA_JWT` from https://www.pinata.cloud for IPFS document storage

### Run with Docker

```bash
cd infra
docker-compose up -d
```

This starts Redis, Postgres (with schema auto-migration), and the FastAPI backend.

## Project Structure

```
procurevani/
  apps/
    webhook/              FastAPI server: WhatsApp webhook, test endpoints, verification API
      main.py             Application entry point, all route mounts
      config.py           Centralized settings from environment variables
      session.py          Session management (Redis with in-memory fallback)
      whatsapp.py         WhatsApp Business Cloud API client
      routers/
        inbound.py        Webhook handler and conversational state machine
    agents/               LangGraph multi-agent pipeline
      llm.py              Google Gemini wrapper (intent, extraction, generation)
      state.py            Typed state definition shared across all nodes
      graph.py            LangGraph StateGraph construction and compilation
      nodes/
        intent.py         Intent classification node
        extraction.py     Structured field extraction node
        compliance.py     PPP-MII compliance checking node
        document.py       Declaration PDF generation and IPFS pinning
        fraud.py          Heuristic fraud detection
        gem.py            GeM submission package assembly
      tools/
        ppp_mii.py        PPP-MII rule engine and LCV calculator
        document.py       HTML/PDF declaration generator
        ipfs.py           Pinata IPFS upload client
        stt.py            Audio transcription via Gemini
        ocr.py            Image OCR via Gemini Vision
    blockchain/
      contracts/
        CompliancePassport.sol    Solidity smart contract
      abi.json                    Contract ABI for web3 interaction
      handler.py                  Python blockchain interaction layer
    gem_adapter/
      submit.py           GeM declaration metadata and package builder
    dashboard/            Next.js 14 auditor dashboard
      app/
        page.tsx          Overview with stat cards and recent activity
        passports/        Searchable passport explorer
        audit/            Chronological audit trail
        fraud/            Fraud flag review queue
        verify/           Passport verification lookup
  data/
    ppp_mii_rules.json    PPP-MII LCV thresholds by HS code
    gem_categories.json   GeM product category mappings
    languages/            Multilingual UI strings (en, hi, te)
  infra/
    docker-compose.yml    Local dev stack (Redis + Postgres + backend)
    Dockerfile            Production container image
    init.sql              Database schema
  tests/
    test_compliance.py    PPP-MII rule engine tests
    test_webhook.py       API endpoint tests
    test_agents.py        Agent node and language detection tests
  scripts/
    seed_rules.py         Data validation and seeding script
```

## Running Tests

```bash
pip install pytest pytest-asyncio anyio
pytest tests/ -v
```

## WhatsApp Webhook Setup

Register a Meta Developer account and create a WhatsApp Business App. In the app settings, configure the webhook URL as `https://your-domain.com/webhook` (the verification GET and message POST are both on the same path). Set the `WA_VERIFY_TOKEN` in your `.env` to match what you enter in the Meta console.

For local development, use ngrok or a similar tool to expose your local port 8000 to the internet:

```bash
ngrok http 8000
```

## Smart Contract Deployment

The CompliancePassport contract is at `apps/blockchain/contracts/CompliancePassport.sol`. Deploy it to the Polygon Amoy testnet using Remix, Hardhat, or Foundry. Once deployed, set the `CONTRACT_ADDRESS` in your `.env`. The ABI at `apps/blockchain/abi.json` matches the contract interface.

## License

MIT
