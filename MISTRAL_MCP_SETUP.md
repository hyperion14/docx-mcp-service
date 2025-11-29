# MCP Server Integration mit chat.mistral.ai

Anleitung zur Integration des DOCX Generator MCP Servers mit Mistral Chat.

## 🎯 Überblick

Der MCP Server nutzt:
- **Protocol:** Model Context Protocol (MCP) mit SSE Transport
- **Framework:** FastMCP (Mistral spec-compliant)
- **URL:** `http://mcp.eunomialegal.de/sse`
- **Tools:** 2 MCP Tools für DOCX Generierung

## 🚀 MCP Server in chat.mistral.ai einbinden

### Schritt 1: Settings öffnen

1. Gehe zu [chat.mistral.ai](https://chat.mistral.ai/)
2. Klicke auf **Settings** (⚙️)
3. Wähle **Connectors** oder **MCP Servers**

### Schritt 2: MCP Connector hinzufügen

Klicke auf **Add Connector** oder **Add MCP Server**

### Schritt 3: Server-Details eingeben

```
Name:        DOCX Generator
Description: Generiert DOCX Dokumente aus Diktat-Texten
URL:         http://mcp.eunomialegal.de/sse
Type:        SSE (Server-Sent Events)
```

**Wichtig:** Die URL MUSS `/sse` am Ende haben!

### Schritt 4: Connector aktivieren

- Aktiviere den Connector
- Warte auf "Connected" Status
- Die Tools sollten jetzt verfügbar sein

## 🛠️ Verfügbare MCP Tools

### 1. generate_docx_document

Generiert ein DOCX-Dokument aus Text.

**Parameter:**
- `text` (required): Der Diktat-Text
- `filename` (optional): Dateiname ohne .docx

**Response:**
```json
{
  "status": "success",
  "download_url": "http://mcp.eunomialegal.de/download/251129_1530_diktat.docx",
  "filename": "251129_1530_diktat.docx",
  "expires_at": "2025-11-30T15:30:00",
  "message": "Dokument erfolgreich erstellt!"
}
```

### 2. check_service_health

Prüft ob der DOCX Generator Service erreichbar ist.

**Parameter:** keine

**Response:**
```json
{
  "status": "healthy",
  "service": "docx-generator",
  "version": "1.0.0",
  "message": "Service ist betriebsbereit"
}
```

## 💬 Agent Prompts

### Beispiel Agent Instructions

```markdown
Du bist ein juristischer Assistent für Vergaberecht und Diktate.

**Workflow:**
1. Empfange Diktat-Text oder Audio vom Nutzer
2. Bereinige den Text (entferne Formatierung, Seitenzahlen, etc.)
3. Zeige dem Nutzer den bereinigten Text zur Bestätigung
4. Nach Bestätigung: Rufe generate_docx_document(text, filename) auf
5. Zeige den Download-Link prominent an

**Wichtig:**
- Rufe generate_docx_document erst nach Nutzerbestätigung auf
- Der Download-Link ist 24h gültig
- Sei präzise und professionell
```

### Beispiel Chat-Ablauf

```
👤 User: Ich möchte ein Diktat erstellen:

Vergaberechtliches Gutachten
§ 97 GWB Transparenzpflicht
Die Auftraggeberin hat eine Ausschreibung durchgeführt...

🤖 Agent: Ich habe den Text bereinigt. Möchten Sie das DOCX generieren?

👤 User: Ja, bitte.

🤖 Agent: [Ruft generate_docx_document auf]

Ihr Dokument wurde erstellt:
📄 http://mcp.eunomialegal.de/download/251129_1530_gutachten.docx

Das Dokument ist 24 Stunden verfügbar.
```

## 🧪 Testing

### 1. SSE Verbindung testen

```bash
curl -N http://mcp.eunomialegal.de/sse -H "Accept: text/event-stream"
```

Erwartete Response:
```
event: endpoint
data: /messages/?session_id=<session-id>
```

### 2. Health Check

```bash
curl http://mcp.eunomialegal.de/health
```

Erwartete Response:
```json
{
  "status": "healthy",
  "service": "docx-generator",
  "version": "1.0.0"
}
```

## 🐛 Troubleshooting

### MCP Server nicht erreichbar

**Symptom:** Connector zeigt "Disconnected"

**Lösung:**
```bash
# Status prüfen
docker-compose ps

# Logs ansehen
docker-compose logs mcp-server

# Server neu starten
docker-compose restart mcp-server
```

### Tools werden nicht angezeigt

**Symptom:** Connector connected, aber keine Tools sichtbar

**Lösung:**
1. Prüfe dass `/sse` in der URL ist
2. Prüfe Server Logs: `docker-compose logs mcp-server`
3. Teste SSE endpoint manuell (siehe Testing)
4. Reconnect den Connector in Mistral

### DOCX Generierung schlägt fehl

**Symptom:** Tool call gibt Error zurück

**Lösung:**
```bash
# Backend Status prüfen
curl http://mcp.eunomialegal.de/health

# Backend Logs
docker-compose logs docx-generator

# API Key prüfen
docker-compose exec docx-generator env | grep DOCKER_API_KEY
```

## 📊 Monitoring

### Container Status

```bash
docker-compose ps
```

### Live Logs

```bash
# Beide Services
docker-compose logs -f

# Nur MCP Server
docker-compose logs -f mcp-server

# Nur DOCX Backend
docker-compose logs -f docx-generator
```

### Health Checks

```bash
# MCP Server SSE
curl -I http://mcp.eunomialegal.de/sse

# DOCX Backend
curl http://mcp.eunomialegal.de/health
```

## 🔐 Security Notes

- MCP Server läuft ohne zusätzliche Auth (über nginx)
- DOCX Backend nutzt API Key Authentication
- Download-Links sind 24h gültig
- Dateien werden automatisch archiviert

## 📚 Weitere Ressourcen

- [Mistral MCP Docs](https://docs.mistral.ai/capabilities/agents/)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## ✅ Zusammenfassung

**MCP Endpoint:** `http://mcp.eunomialegal.de/sse`

**Tools:**
- `generate_docx_document(text, filename?)`
- `check_service_health()`

**Health Check:** `http://mcp.eunomialegal.de/health`

Viel Erfolg! 🚀
