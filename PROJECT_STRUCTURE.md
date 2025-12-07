# BHK DOCX Service - Projekt Struktur

> Saubere, produktionsbereite Struktur nach Cleanup (07.12.2025)

## �� Verzeichnisstruktur

```
docx_service/
├── 📄 Core Application Files
│   ├── app.py                    # Flask Backend (Port 5000)
│   ├── mcp_server_v2.py         # MCP Server mit SSE (Port 7860)
│   ├── docx_logic.py            # Business Logic
│   └── bhk_formatter.py         # Markdown → DOCX Konvertierung
│
├── 🐳 Docker & Deployment
│   ├── Dockerfile               # DOCX Backend Container
│   ├── Dockerfile.mcp          # MCP Server Container
│   ├── docker-compose.yml      # Orchestrierung
│   └── requirements.txt        # Python Dependencies
│
├── 📚 Documentation
│   ├── README.md               # Hauptdokumentation & Quick Start
│   ├── ARCHITECTURE.md         # Technische Architektur
│   └── NGINX_SETUP.md         # Nginx Konfiguration
│
├── ⚙️ Configuration
│   ├── .env                    # Environment Variables (gitignored)
│   ├── .env.example           # Environment Template
│   └── .gitignore
│
├── 📂 Runtime Directories
│   ├── templates/             # BHK Template (bhk-base.docx)
│   ├── docx_files/            # Generierte DOCX (Volume)
│   └── archive/               # Archivierte Files (Volume)
│
└── 🔧 Development
    └── __pycache__/           # Python Cache (gitignored)
```

## 🎯 Python Module

| Datei | Lines | Verantwortlichkeit |
|-------|-------|-------------------|
| `app.py` | ~180 | Flask REST API, /generate_docx, /download, /health |
| `mcp_server_v2.py` | ~165 | FastMCP Server, SSE Transport, MCP Tools |
| `docx_logic.py` | ~185 | DOCX Generation Logic, Archivierung |
| `bhk_formatter.py` | ~435 | Markdown Parser, BHK Style Application |

**Total Lines of Code:** ~965 LOC

## 🐳 Docker Files

| Datei | Base Image | Purpose |
|-------|------------|---------|
| `Dockerfile` | python:3.11-slim | DOCX Generator Backend |
| `Dockerfile.mcp` | python:3.11-slim | MCP Server (SSE) |
| `docker-compose.yml` | - | 2 Services + Volumes + Network |

## 📦 Dependencies (requirements.txt)

```txt
flask
flask-cors
python-docx
python-dotenv
requests
mistune>=3.0.0
fastmcp>=2.13.0
mcp>=1.22.0
uvicorn
```

## 🌐 Network Ports

| Port | Service | Protocol | Public |
|------|---------|----------|--------|
| 5000 | DOCX Backend | HTTP | No (internal) |
| 7860 | MCP Server | HTTP/SSE | Yes (via Nginx) |

## 📊 File Sizes (Approx.)

```
app.py              ~6 KB
mcp_server_v2.py    ~6 KB
docx_logic.py       ~7 KB
bhk_formatter.py    ~16 KB
templates/bhk-base.docx  ~14 KB

Total Source:       ~35 KB
```

## 🔄 Data Flow

```
User (Mistral Chat)
    ↓ SSE
MCP Server (mcp_server_v2.py)
    ↓ HTTP
DOCX Backend (app.py)
    ↓ Function Call
DOCX Logic (docx_logic.py)
    ↓ Format
BHK Formatter (bhk_formatter.py)
    ↓ Save
docx_files/ Volume
    ↓ Serve
Nginx → User Download
```

## ✨ Clean Architecture Principles

✅ **Separation of Concerns**
- MCP Server ≠ DOCX Backend
- Business Logic isoliert in docx_logic.py
- Formatting Engine eigenständig (bhk_formatter.py)

✅ **Single Responsibility**
- app.py: REST API
- mcp_server_v2.py: MCP Protocol
- docx_logic.py: Document Generation
- bhk_formatter.py: Markdown Conversion

✅ **Dependency Inversion**
- MCP Server nutzt DOCX Backend via HTTP (loose coupling)
- BHK Formatter injizierbar via template_path

✅ **Containerization**
- Services isoliert in separaten Containern
- Shared Volumes für Daten
- Health Checks für Monitoring

---

**Status:** Production Ready ✅  
**Last Cleanup:** 07.12.2025
