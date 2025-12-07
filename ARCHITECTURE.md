# BHK-Format DOCX Generator - Systemarchitektur

> **Version:** 2.0.0  
> **Letzte Aktualisierung:** 07.12.2025  
> **Status:** Production

---

## 🎯 Überblick

Microservice-Architektur zur Generierung von BHK-formatierten Word-Dokumenten mit Mistral Chat Integration über Model Context Protocol (MCP).

**Kernkomponenten:**
- **DOCX Backend** (Flask, Port 5000) - REST API für DOCX-Generierung
- **MCP Server** (FastMCP, Port 7860) - SSE Transport für Mistral Integration
- **BHK Formatter** - Markdown → DOCX Konvertierung mit BHK-Styles
- **Nginx Reverse Proxy** - External Routing & SSL Termination

---

## 🏗️ Systemarchitektur

```
┌──────────────────────────────────────────────────────────────┐
│              Mistral Chat (chat.mistral.ai)                   │
│              MCP Client (SSE Transport)                       │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS/SSE
                         │ mcp.eunomialegal.de/sse
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                 Nginx Reverse Proxy                           │
│                 (mcp.eunomialegal.de)                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Routing Rules:                                         │  │
│  │  • /sse → localhost:7860 (MCP Server SSE)             │  │
│  │  • /download/* → localhost:5000 (DOCX Downloads)      │  │
│  │  • /health → Health Checks                            │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
         ┌───────────────┴──────────────┐
         │                              │
         ▼                              ▼
┌─────────────────────┐      ┌─────────────────────┐
│  MCP Server         │      │  DOCX Backend       │
│  (mcp-docx-server)  │◄────►│  (docx-generator)   │
│                     │ HTTP │                     │
│  Port: 7860         │      │  Port: 5000         │
│  Transport: SSE     │      │  API: REST          │
│                     │      │                     │
│  mcp_server_v2.py   │      │  app.py             │
│  (FastMCP)          │      │  (Flask)            │
└──────────┬──────────┘      └──────────┬──────────┘
           │                            │
           ├────────────────────────────┤
           │   Shared Volumes:          │
           │   • docx_files/            │
           │   • archive/               │
           │   • templates/             │
           └────────────────────────────┘
```

---

## 📦 Komponenten-Details

### 1. MCP Server (Port 7860)

**Datei:** `mcp_server_v2.py`  
**Framework:** FastMCP (Server-Sent Events)  
**Container:** `mcp-docx-server`

#### Verantwortlichkeiten
- MCP Tool Endpoint für Mistral Chat
- SSE Transport (/sse)
- Orchestrierung der DOCX-Generierung
- Health Check (/health)

#### MCP Tools
```python
@mcp.tool()
def generate_docx_document(text: str) -> str:
    """
    Generiert DOCX aus Text und gibt Download-Link zurück.
    Wird von Mistral Chat aufgerufen.
    """
    
@mcp.tool()
def check_service_health() -> str:
    """
    Prüft Service-Status und Upload-Folder.
    """
```

#### Endpoints
```
GET  /sse     → SSE Stream für MCP Messages
GET  /health  → Health Check
POST /        → MCP Tool Invocation
```

---

### 2. DOCX Backend (Port 5000)

**Datei:** `app.py`  
**Framework:** Flask  
**Container:** `docx-generator`

#### Verantwortlichkeiten
- REST API für DOCX-Generierung
- File Downloads via /download/
- Archivierung (24h Delay)
- Statistics & Monitoring

#### API Endpoints
```python
POST /generate_docx
  → Input:  {"text": "...", "filename": "...", "format_mode": "bhk"}
  → Output: {"download_url": "...", "filename": "...", "expires_at": "..."}
  
GET  /download/<filename>
  → Serves DOCX files from docx_files/
  
GET  /health
  → {"status": "healthy", "service": "docx-generator"}
  
GET  /stats (Auth required)
  → Service statistics (active files, archived files)
  
GET  /list_archives (Auth required)
  → Archive structure by date
```

---

### 3. DOCX Logic Layer

**Datei:** `docx_logic.py`  
**Verantwortlichkeit:** Business Logic für DOCX-Generierung

#### Funktionen
```python
def generate_docx_from_text(
    text: str,
    output_folder: str,
    template_path: str,
    custom_filename: str = None,
    use_bhk_format: bool = True
) -> tuple[str, str]:
    """
    Generiert DOCX-Dokument aus Text.
    
    Returns: (docx_filename, txt_filename)
    """
    
def archive_files_after_delay(
    docx_filename: str,
    txt_filename: str,
    upload_folder: str,
    archive_folder: str,
    delay: int = 86400
):
    """
    Archiviert Dateien nach Delay (Standard: 24h).
    Threading-basiert.
    """
```

---

### 4. BHK Formatter

**Datei:** `bhk_formatter.py`  
**Parser:** mistune (Markdown AST)  
**Output:** python-docx

#### Architektur
```
Markdown Input
     ↓
mistune.parse() → AST (Abstract Syntax Tree)
     ↓
BHKFormatter._process_nodes()
     ↓
DOCX Paragraphs mit BHK_Standard Style
     ↓
Document.save()
```

#### Markdown → DOCX Mapping
| Markdown Node | DOCX Output |
|---------------|-------------|
| `heading` (###) | Bold Text + BHK_Standard |
| `list` (-) | "• " Prefix + BHK_Standard |
| `paragraph` | BHK_Standard |
| `strong` (**) | Bold Run |
| `emphasis` (*) | Italic Run |
| `codespan` (`) | Monospace Font |

#### Methoden
```python
class BHKFormatter:
    def convert_to_docx(self, doc: Document, markdown_text: str):
        """Main entry point für Konvertierung"""
        
    def _process_nodes(self, doc: Document, nodes: List[Dict]):
        """Dispatcher für AST Node Types"""
        
    def _process_heading(self, doc: Document, node: Dict):
        """Überschrift → Bold + BHK_Standard"""
        
    def _process_list(self, doc: Document, node: Dict):
        """Liste → • Prefix + BHK_Standard"""
        
    def _apply_bhk_style(self, para):
        """Anwendung von BHK_Standard Style (Fallback: Normal)"""
```

---

## 🔄 Datenfluss

### Request Flow: Mistral Chat → DOCX Download

```
┌─────────────────────────────────────────────────────────┐
│ 1. User Input (Mistral Chat)                            │
│    "Erstelle ein Word-Dokument aus diesem Text: ..."   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Mistral Agent → MCP Tool Call                        │
│    Tool: generate_docx_document                         │
│    Args: { text: "..." }                                │
└────────────────────────┬────────────────────────────────┘
                         │ SSE Transport
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. MCP Server (mcp_server_v2.py)                        │
│    • Empfängt Tool-Call via SSE                         │
│    • Validiert Parameter                                │
│    • Generiert Timestamp-Dateinamen                     │
└────────────────────────┬────────────────────────────────┘
                         │ Internal HTTP (docx-generator:5000)
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 4. DOCX Backend → docx_logic.py                         │
│    • generate_docx_from_text()                          │
│    • Template laden (bhk-base.docx)                     │
│    • BHKFormatter initialisieren                        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 5. BHK Formatter (bhk_formatter.py)                     │
│    • Markdown → AST (mistune Parser)                    │
│    • AST Nodes verarbeiten                              │
│    • Styles anwenden (BHK_Standard)                     │
│    • DOCX speichern (docx_files/)                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Response Chain                                       │
│    DOCX Backend → MCP Server → Mistral Chat            │
│    Download URL: https://mcp.../download/FILENAME.docx  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 7. User Download                                        │
│    Nginx → docx-generator:5000/download/FILENAME.docx  │
└─────────────────────────────────────────────────────────┘
```

---

## 🐳 Docker Container

### Container 1: DOCX Generator

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Dependencies
RUN pip install flask python-docx mistune requests

# Application Files
COPY app.py docx_logic.py bhk_formatter.py ./

# Volumes
VOLUME /app/docx_files
VOLUME /app/archive
VOLUME /app/templates

EXPOSE 5000
CMD ["python", "app.py"]
```

**Health Check:**
```bash
curl -f http://localhost:5000/health
```

---

### Container 2: MCP Server

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Dependencies
RUN pip install fastmcp mcp uvicorn python-docx mistune

# Application Files
COPY mcp_server_v2.py docx_logic.py bhk_formatter.py ./

# Volumes (shared)
VOLUME /app/docx_files
VOLUME /app/archive
VOLUME /app/templates

EXPOSE 7860
CMD ["python3", "mcp_server_v2.py"]
```

**Health Check:**
```bash
curl -f http://localhost:7860/health
```

---

### Docker Compose Orchestrierung

```yaml
services:
  docx-generator:
    build: 
      dockerfile: Dockerfile
    ports: ["5000:5000"]
    volumes:
      - docx_files:/app/docx_files
      - archive:/app/archive
      - ./templates:/app/templates:ro
    networks: [docx-network]
    
  mcp-server:
    build:
      dockerfile: Dockerfile.mcp
    ports: ["7860:7860"]
    volumes:
      - docx_files:/app/docx_files
      - archive:/app/archive
      - ./templates:/app/templates:ro
    depends_on: [docx-generator]
    networks: [docx-network]

volumes:
  docx_files:
  archive:

networks:
  docx-network:
```

---

## 🎨 BHK Template & Styles

### Template Struktur

**Datei:** `templates/bhk-base.docx`

**Verfügbare Styles:**
- `BHK_Standard` ← **Primär verwendet**
- `BHK_Struktur`
- `BHKVertrag`
- `BHKVertrag_Liste`
- `Normal` ← Fallback

### Style Anwendung

```python
# In bhk_formatter.py
def _apply_bhk_style(self, para):
    try:
        para.style = 'BHK_Standard'  # Primary
    except KeyError:
        para.style = 'Normal'  # Fallback
```

**Wichtig:** Template muss im Container verfügbar sein:
```yaml
volumes:
  - ./templates:/app/templates:ro  # Read-only
```

---

## 🔒 Security & Authentication

### API Key Authentication (DOCX Backend)

```python
# In app.py
def verify_api_key(request):
    auth_header = request.headers.get('Authorization', '')
    expected_auth = f"Bearer {API_KEY}"
    return auth_header == expected_auth
```

**Protected Endpoints:**
- `POST /generate_docx`
- `GET /stats`
- `GET /list_archives`

**Environment:**
```bash
DOCKER_API_KEY=your_secure_key_here
```

---

## 📊 Performance & Metriken

### Durchsatz

| Operation | Zeit (avg) | Komplexität |
|-----------|------------|-------------|
| Markdown Parsing (mistune) | 10-20ms | O(n) |
| BHK Formatting | 50-100ms | O(n) |
| DOCX Generation | 100-200ms | O(n) |
| **Total (klein, <1KB)** | **200-400ms** | O(n) |
| **Total (groß, 10KB)** | **500ms-1s** | O(n) |

### Memory Footprint

| Komponente | Memory (avg) |
|------------|--------------|
| Flask App | 30-50 MB |
| FastMCP Server | 40-60 MB |
| python-docx | 10-20 MB |
| mistune Parser | 2-5 MB |
| **Total System** | **~100-150 MB** |

---

## 🔄 File Lifecycle

```
1. Generation
   └─ docx_files/YYMMDD_HHMM_<name>.docx
   └─ docx_files/YYMMDD_HHMM_<name>.txt (Source)

2. Availability
   └─ 24 hours via /download/<filename>

3. Archival (threading.Timer)
   └─ archive/YYMMDD/<filename>.docx
   └─ archive/YYMMDD/<filename>.txt

4. Manual Cleanup
   └─ find archive/ -mtime +30 -delete
```

---

## 🌐 Network Architecture

```
Internet (HTTPS/443)
    ↓
Nginx (mcp.eunomialegal.de)
    ├─ /sse → localhost:7860 (MCP Server)
    │   └─ SSE Stream, MCP Protocol
    │
    └─ /download/* → localhost:5000 (DOCX Backend)
        └─ Static File Serving

Docker Network (docx-network)
    ├─ docx-generator (5000)
    └─ mcp-docx-server (7860)
        └─ Internal: http://docx-generator:5000
```

### Nginx Configuration

```nginx
location /sse {
    proxy_pass http://localhost:7860;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;
}

location /download/ {
    proxy_pass http://localhost:5000/download/;
}
```

Siehe **NGINX_SETUP.md** für vollständige Konfiguration.

---

## 🐛 Fehlerbehandlung

### Fallback-Mechanismen

```
1. BHK_Standard nicht gefunden
   → Fallback: Normal Style
   → Warning in Logs

2. mistune nicht installiert
   → Fallback: Regex-basierte Konvertierung
   → Limitierte Markdown-Unterstützung

3. Template nicht verfügbar
   → Neues leeres Document()
   → Styles manuell anwenden

4. DOCX Backend nicht erreichbar
   → Exception mit Fehlermeldung
   → User erhält Error in Mistral Chat
```

---

## 📝 Logging

### MCP Server
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Output:** Docker stdout

### DOCX Backend
```python
logger = logging.getLogger(__name__)
logger.info("Generated DOCX: filename.docx")
```

**Output:** Docker stdout

### Monitoring
```bash
# Live Logs
docker-compose logs -f

# Specific Container
docker logs -f mcp-docx-server
docker logs -f docx-generator
```

---

## 🚀 Deployment Checklist

- ✅ Docker & Docker Compose installiert
- ✅ `.env` konfiguriert (API Keys)
- ✅ Nginx Reverse Proxy konfiguriert
- ✅ SSL/TLS Zertifikate (Let's Encrypt)
- ✅ Template vorhanden (`templates/bhk-base.docx`)
- ✅ Health Checks aktiv
- ✅ Volume Mounts korrekt
- ✅ Firewall-Regeln (Ports 80, 443)

---

## 📚 Referenzen

### Abhängigkeiten

**Python Packages:**
- `flask` - REST API Framework
- `fastmcp` - MCP Server Framework
- `python-docx` - DOCX Manipulation
- `mistune` - Markdown Parser
- `uvicorn` - ASGI Server (für FastMCP)

**System:**
- Docker Engine ≥ 20.10
- Docker Compose ≥ 2.0
- Nginx ≥ 1.18

### Externe Dokumentation

- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [mistune Documentation](https://mistune.lepture.com/)

---

**Version:** 2.0.0  
**Erstellt:** 01.12.2025  
**Aktualisiert:** 07.12.2025  
**Status:** Production
