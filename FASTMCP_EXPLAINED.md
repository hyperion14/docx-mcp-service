# FastMCP - Technische Erklärung

## 🎯 Was ist FastMCP?

FastMCP ist ein Python Framework das **automatisch** aus Python-Code MCP-konforme Server erstellt.

## 📦 Installation & Location

**Installiert in:** `/home/developer/.local/lib/python3.10/site-packages/mcp/server/fastmcp/`

**Version:** 2.13.1

**Installiert via Dockerfile.mcp:**
```dockerfile
RUN pip install --no-cache-dir fastmcp
```

## 🔧 Wie FastMCP funktioniert

### 1. Python Type Hints → JSON Schema

**Du schreibst Python:**
```python
@mcp.tool()
def generate_docx_document(text: str, filename: str = "diktat") -> dict:
    """Generiert ein DOCX-Dokument"""
    pass
```

**FastMCP generiert automatisch:**
```json
{
  "name": "generate_docx_document",
  "description": "Generiert ein DOCX-Dokument",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "title": "Text"
      },
      "filename": {
        "type": "string",
        "default": "diktat",
        "title": "Filename"
      }
    },
    "required": ["text"]
  }
}
```

### 2. MCP Protokoll Handling

FastMCP implementiert das **Model Context Protocol**:

```
Client (Mistral)          FastMCP Server
     │                         │
     ├─── initialize ────────→ │  Handshake
     │                         │
     ├─── tools/list ────────→ │  Gibt Tools als JSON
     │                         │
     ├─── tools/call ────────→ │  Führt Python Funktion aus
     │   {name, arguments}     │
     │                         │
     ├──────── result ────────┤  Gibt Ergebnis zurück
```

### 3. SSE Transport

FastMCP nutzt **Server-Sent Events** für Mistral:

```python
mcp.run(transport="sse")
```

Erstellt automatisch:
- `GET /sse` - SSE Endpoint für Mistral
- `POST /messages/` - Message handling
- JSON-RPC 2.0 Protocol handling

## 📁 FastMCP Package Struktur

```
/home/developer/.local/lib/python3.10/site-packages/
└── mcp/
    └── server/
        └── fastmcp/
            ├── server.py           # FastMCP Hauptklasse
            ├── tools/
            │   └── manager.py      # ToolManager (Type Hints → JSON)
            ├── prompts/
            │   └── manager.py      # Prompt Management
            ├── resources/
            │   └── manager.py      # Resource Management
            └── utilities/
                └── context_injection.py  # Context handling
```

## 🔍 Wichtige Klassen

### FastMCP Class (server.py)

```python
class FastMCP:
    def __init__(self, name: str, host: str, port: int):
        self._tools = ToolManager()
        self._prompts = PromptManager()
        self._resources = ResourceManager()

    def tool(self, ...):
        """Decorator um Python Funktion als MCP Tool zu registrieren"""

    async def list_tools(self) -> list[MCPTool]:
        """Gibt alle Tools mit inputSchema zurück"""

    async def call_tool(self, name: str, arguments: dict):
        """Führt Tool aus"""

    def run(self, transport="sse"):
        """Startet Server (uvicorn)"""
```

### ToolManager (tools/manager.py)

Konvertiert Python → JSON Schema:
- Liest Type Hints (`str`, `int`, `dict`, etc.)
- Erkennt Required vs Optional (via default values)
- Generiert Pydantic Models
- Exportiert als JSON Schema

## 🌐 Offizielle Dokumentation

1. **Website:** https://gofastmcp.com
2. **GitHub:** https://github.com/jlowin/fastmcp
3. **MCP Spec:** https://modelcontextprotocol.io/
4. **PyPI:** https://pypi.org/project/fastmcp/

## 📊 FastMCP in unserem Projekt

### Verwendung in mcp_server.py

```python
from mcp.server.fastmcp import FastMCP

# Initialisierung
mcp = FastMCP(
    name="DOCXGenerator",  # Kein Leerzeichen!
    host="0.0.0.0",
    port=7860
)

# Tool Registration (Decorator)
@mcp.tool()
def generate_docx_document(text: str, filename: str = "diktat") -> dict:
    """Description wird automatisch extrahiert"""
    # Implementation...
    return {"status": "success", ...}

# Server starten
mcp.run(transport="sse")
```

### Was passiert zur Laufzeit?

1. **Container startet:**
   ```bash
   docker-compose up -d mcp-server
   # Führt aus: python3 mcp_server.py
   ```

2. **FastMCP startet uvicorn:**
   ```
   INFO: Uvicorn running on http://0.0.0.0:7860
   ```

3. **Mistral verbindet sich:**
   ```
   GET http://mcp.eunomialegal.de/sse
   ```

4. **FastMCP handelt Requests:**
   - `initialize` - Handshake
   - `tools/list` - Sendet Tool-Definitionen als JSON
   - `tools/call` - Führt Python Funktion aus
   - Sendet Ergebnis zurück über SSE

## ✅ Vorteile von FastMCP

1. **Automatische Schema Generierung**
   - Keine manuelle JSON Schema Definition nötig
   - Type Hints reichen aus

2. **MCP Protokoll inklusive**
   - JSON-RPC 2.0 handling
   - SSE transport
   - Automatische Serialisierung

3. **Pythonic API**
   - Decorators (`@mcp.tool()`)
   - Type Hints
   - Async support

4. **Mistral kompatibel**
   - Implementiert offizielle MCP Spec
   - SSE transport für chat.mistral.ai
   - Tool calling wie dokumentiert

## 🔗 Kommunikationsfluss

```
chat.mistral.ai
    ↓
nginx (mcp.eunomialegal.de/sse)
    ↓
FastMCP Server (Port 7860)
    ↓
ToolManager (konvertiert JSON → Python call)
    ↓
generate_docx_document() - Deine Funktion
    ↓
requests.post() zum DOCX Backend
    ↓
Ergebnis zurück über SSE zu Mistral
```

## 🎓 Zusammenfassung

**FastMCP macht aus diesem Python Code:**
```python
@mcp.tool()
def my_func(text: str, count: int = 5) -> dict:
    """Does something"""
    return {"result": text * count}
```

**Automatisch einen MCP Server der:**
1. JSON Schema generiert
2. MCP Protokoll implementiert
3. SSE transport bereitstellt
4. Mit Mistral kommuniziert
5. Python Funktion ausführt
6. Ergebnis zurückgibt

**Keine manuelle Konfiguration nötig!**
