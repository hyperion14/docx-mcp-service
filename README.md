# DOCX Generator Service mit MCP Integration

Mistral-kompatibler MCP Server für DOCX Generierung aus Diktat-Texten.

## 🎯 Überblick

Dieser Service besteht aus zwei Komponenten:
- **DOCX Generator Backend** (Flask, Port 5000) - Generiert Word-Dokumente
- **MCP Server** (FastMCP, Port 7860) - Mistral-konformes MCP Interface

## 🚀 Quick Start

### Voraussetzungen
- Docker & Docker Compose
- API Keys in `.env` Datei

### Installation

```bash
# 1. Repository klonen
cd docx_service

# 2. Environment konfigurieren
cp .env.example .env
# Editiere .env und füge deine API Keys ein:
# - DOCKER_API_KEY
# - MISTRAL_API_KEY

# 3. Services starten
docker-compose up -d

# 4. Health Check
curl http://localhost:5000/health
curl http://localhost:7860/sse
```

## 📦 Service Architektur

```
┌─────────────────────────────────────────────┐
│  chat.mistral.ai (Mistral Chat Interface)  │
└────────────────┬────────────────────────────┘
                 │ SSE/MCP Protocol
                 ↓
┌─────────────────────────────────────────────┐
│  nginx (mcp.eunomialegal.de)                │
│  - /sse → MCP Server (7860)                 │
│  - /health → DOCX Backend (5000)            │
└────────────┬────────────────┬───────────────┘
             │                │
             ↓                ↓
┌────────────────────┐  ┌──────────────────┐
│  MCP Server        │  │  DOCX Backend    │
│  (FastMCP + SSE)   │→→│  (Flask)         │
│  Port: 7860        │  │  Port: 5000      │
└────────────────────┘  └──────────────────┘
```

## 🔧 Konfiguration

### docker-compose.yml

Zwei Services:
- `docx-generator` - DOCX Backend
- `mcp-server` - MCP Server (Mistral spec-compliant)

### Environment Variables

```bash
# API Authentication
DOCKER_API_KEY=<your-secret-key>

# Mistral Integration (optional)
MISTRAL_API_KEY=<your-mistral-key>
MISTRAL_AGENT_ID=<your-agent-id>
```

## 🌐 Endpoints

### DOCX Backend (Port 5000)
- `GET /health` - Service health check
- `POST /generate_docx` - DOCX Generierung (Auth required)
- `GET /download/<filename>` - DOCX Download
- `GET /stats` - Service Statistiken (Auth required)

### MCP Server (Port 7860)
- `GET /sse` - SSE endpoint für Mistral MCP
- MCP Tools:
  - `generate_docx_document(text, filename)`
  - `check_service_health()`

## 📚 Weitere Dokumentation

- [MCP Setup für Mistral](MISTRAL_MCP_SETUP.md) - Integration mit chat.mistral.ai
- [Nginx Setup](NGINX_SETUP.md) - Reverse Proxy Konfiguration

## 🛠️ Development

### Container neu bauen
```bash
docker-compose build
docker-compose up -d
```

### Logs ansehen
```bash
docker-compose logs -f
docker-compose logs docx-generator
docker-compose logs mcp-server
```

### Tests
```bash
# DOCX Backend
curl -X POST http://localhost:5000/generate_docx \
  -H "Authorization: Bearer $DOCKER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test Diktat", "filename": "test"}'

# MCP Server SSE
curl http://localhost:7860/sse -H "Accept: text/event-stream"
```

## 🔒 Security

- API Key Authentication für DOCX Backend
- Nginx Reverse Proxy mit CORS
- Automatische Archivierung nach 24h
- Keine sensiblen Daten in Repository

## 📝 License

MIT
