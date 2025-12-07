# BHK-Format DOCX Generator Service

> **Professionelle Word-Dokument-Generierung mit BHK-Formatierung**  
> **Version:** 2.0.0 | **Status:** Production | **Letzte Aktualisierung:** 07.12.2025

Microservice-basiertes System zur Generierung von BHK-formatierten Word-Dokumenten 
aus Markdown-Text, optimiert für die Integration mit Mistral Chat über das Model 
Context Protocol (MCP).

---

## 🎯 Überblick

Dieser Service besteht aus zwei Docker-Containern:

1. **DOCX Generator Backend** - Flask-basierte REST API zur DOCX-Generierung
2. **MCP Server** - Model Context Protocol Server mit SSE Transport für Mistral Chat Integration

### Features

✅ **BHK-Formatierung** - Automatische Anwendung von BHK-Formatvorlagen  
✅ **Markdown → DOCX** - Konvertierung von Markdown-Syntax zu formatierten Word-Dokumenten  
✅ **MCP Integration** - Direkte Integration in Mistral Chat über SSE Transport  
✅ **Template-basiert** - Verwendung von BHK-Template für konsistente Formatierung  
✅ **Auto-Archivierung** - Automatische Archivierung nach 24 Stunden  
✅ **Health Monitoring** - Integrierte Health Checks für beide Services

---

## 📁 Projektstruktur

```
docx_service/
├── app.py                    # Flask Backend (Port 5000)
├── mcp_server_v2.py         # MCP Server mit SSE (Port 7860)
├── docx_logic.py            # DOCX-Generierungs-Logik
├── bhk_formatter.py         # BHK-Formatierungs-Engine
├── requirements.txt         # Python Dependencies
│
├── Dockerfile               # Backend Container
├── Dockerfile.mcp          # MCP Server Container
├── docker-compose.yml      # Orchestrierung
│
├── templates/              # BHK Template
│   └── bhk-base.docx
│
├── .env.example           # Environment Template
├── README.md              # Diese Datei
├── ARCHITECTURE.md        # Technische Architektur
└── NGINX_SETUP.md        # Nginx Reverse Proxy Setup
```

---

## 🚀 Quick Start

### 1. Voraussetzungen

- Docker & Docker Compose
- Nginx (für Production Deployment)
- Optional: Mistral Chat Account (für MCP Integration)

### 2. Installation

```bash
# Repository klonen
cd /path/to/docx_service

# Environment konfigurieren
cp .env.example .env
nano .env  # API Keys eintragen

# Container starten
docker-compose up -d

# Status prüfen
docker-compose ps
```

### 3. Environment Variablen (.env)

```bash
# API Authentifizierung
DOCKER_API_KEY=your_secure_api_key_here

# Public URL (für Download-Links)
PUBLIC_URL=https://mcp.eunomialegal.de

# Mistral Integration (optional)
MISTRAL_API_KEY=your_mistral_api_key
MISTRAL_AGENT_ID=your_agent_id
```

### 4. Service URLs

```
Backend API:     http://localhost:5000
MCP Server:      http://localhost:7860
MCP SSE:         http://localhost:7860/sse
Health Checks:   http://localhost:5000/health
                 http://localhost:7860/health
```

---

## 🔧 API Endpoints

### DOCX Backend (Port 5000)

#### `POST /generate_docx`

Generiert ein DOCX-Dokument aus Text.

**Request:**
```json
{
  "text": "### Überschrift\n\n- Liste\n- Punkt 2\n\nAbsatz",
  "filename": "optional_name",
  "format_mode": "bhk"
}
```

**Response:**
```json
{
  "download_url": "https://mcp.eunomialegal.de/download/251207_1200_dokument.docx",
  "filename": "251207_1200_dokument.docx",
  "format_mode": "bhk",
  "expires_at": "2025-12-08T12:00:00",
  "message": "DOCX generated successfully in BHK format."
}
```

**Auth:** `Authorization: Bearer YOUR_API_KEY`

#### `GET /download/<filename>`

Lädt generierte DOCX-Datei herunter.

#### `GET /health`

Health Check Endpoint.

#### `GET /stats` (Auth required)

Service-Statistiken.

---

### MCP Server (Port 7860)

#### MCP Tools

**1. `generate_docx_document(text: str) -> str`**

Generiert DOCX-Dokument und gibt Download-Link zurück.

**Verwendung in Mistral Chat:**
```
Erstelle ein Word-Dokument aus diesem Text:
[Ihr Text hier]
```

**2. `check_service_health() -> str`**

Prüft Service-Status.

#### SSE Endpoint: `/sse`

Für Mistral Chat MCP Integration (siehe NGINX_SETUP.md).

---

## 🎨 BHK-Formatierung

### Markdown → DOCX Konvertierung

| Markdown | DOCX Output |
|----------|-------------|
| `### Überschrift` | **Fetter Text** mit BHK_Standard Style |
| `- Liste` | Bullet-Liste (•) mit BHK_Standard |
| `**fett**` | Fettdruck im Text |
| `*kursiv*` | Kursiv im Text |
| Normaler Absatz | BHK_Standard Paragraph |

### Template

Das System verwendet `templates/bhk-base.docx` als Basis-Template mit folgenden Styles:

- **BHK_Standard** - Haupt-Absatzformat (primär)
- **BHK_Struktur** - Strukturelemente
- **BHKVertrag** - Vertragsformat (optional)

Eigene Templates können durch Ersetzen von `bhk-base.docx` eingebunden werden.

---

## 🐳 Docker Container

### 1. DOCX Generator Backend

```yaml
Container: docx-generator
Port: 5000
Image: Python 3.11 Slim
Dependencies: flask, python-docx, mistune
```

### 2. MCP Server

```yaml
Container: mcp-docx-server
Port: 7860
Image: Python 3.11 Slim
Dependencies: fastmcp, mcp, uvicorn
Transport: SSE (Server-Sent Events)
```

### Shared Volumes

```
docx_files/     - Generierte DOCX-Dateien
archive/        - Archivierte Dateien (>24h)
templates/      - BHK Template (read-only)
```

---

## 🔒 Production Deployment

### Nginx Reverse Proxy

Für Production Deployment mit externer URL siehe:
- **NGINX_SETUP.md** - Vollständige Nginx Konfiguration
- **ARCHITECTURE.md** - System-Architektur Details

**Empfohlene Nginx Routing:**
```nginx
location /sse {
    proxy_pass http://localhost:7860;
}

location /download/ {
    proxy_pass http://localhost:5000/download/;
}
```

### SSL/TLS

Certbot für Let's Encrypt Zertifikate empfohlen:
```bash
sudo certbot --nginx -d mcp.eunomialegal.de
```

---

## 📊 Monitoring

### Health Checks

```bash
# Backend
curl http://localhost:5000/health

# MCP Server
curl http://localhost:7860/health
```

### Docker Logs

```bash
# Backend Logs
docker logs -f docx-generator

# MCP Server Logs
docker logs -f mcp-docx-server

# Beide Container
docker-compose logs -f
```

### Service Statistics

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:5000/stats
```

---

## 🛠️ Development

### Lokales Testing

```bash
# Container neu bauen
docker-compose up -d --build

# Test DOCX Generation
curl -X POST http://localhost:5000/generate_docx \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "### Test\n\n- Punkt 1\n- Punkt 2",
    "filename": "test"
  }'
```

### Logs & Debugging

```bash
# Live Logs
docker-compose logs -f

# Einzelner Container
docker logs -f docx-generator

# Container Shell
docker exec -it docx-generator bash
docker exec -it mcp-docx-server bash
```

### Requirements aktualisieren

```bash
# Neue Dependencies hinzufügen
echo "new-package>=1.0.0" >> requirements.txt

# Container neu bauen
docker-compose up -d --build
```

---

## 🔄 Wartung

### Archiv-Cleanup

Archivierte Dateien in `archive/` werden **nicht automatisch gelöscht**.

```bash
# Alte Archive löschen (älter als 30 Tage)
find archive/ -type f -mtime +30 -delete

# Archive nach Datum löschen
rm -rf archive/YYMMDD/
```

### Container Updates

```bash
# Services neustarten
docker-compose restart

# Kompletter Rebuild
docker-compose down
docker-compose up -d --build

# Volumes behalten
docker-compose down --volumes=false
```

---

## 🐛 Troubleshooting

### Problem: DOCX ohne BHK-Formatierung

**Lösung:** Template Volume prüfen
```bash
docker exec mcp-docx-server ls -la /app/templates/
# Sollte bhk-base.docx zeigen
```

### Problem: MCP Server nicht erreichbar

**Lösung:** SSE Transport verifizieren
```bash
curl http://localhost:7860/health
# Sollte {"status":"healthy"} zurückgeben
```

### Problem: Downloads nicht verfügbar

**Lösung:** Nginx Routing und Volume Mounts prüfen
```bash
docker exec docx-generator ls -la /app/docx_files/
# Sollte generierte DOCX zeigen
```

### Problem: Template nicht gefunden

**Lösung:** Volume Mount in docker-compose.yml prüfen
```yaml
volumes:
  - ./templates:/app/templates:ro  # Read-only mount
```

---

## 📚 Weitere Dokumentation

- **ARCHITECTURE.md** - Detaillierte System-Architektur, Datenfluss, Komponenten
- **NGINX_SETUP.md** - Nginx Reverse Proxy Konfiguration für Production
- **PROJECT_STRUCTURE.md** - Projekt-Übersicht und Clean Architecture
- **.env.example** - Environment Template mit allen Optionen

---

## 📝 Version History

| Version | Datum | Änderungen |
|---------|-------|------------|
| 2.0.0 | 07.12.2025 | ✅ SSE Transport, Volume Mounts, BHK-Formatierung produktiv |
| 1.5.0 | 01.12.2025 | MCP Server Integration, FastMCP Framework |
| 1.0.0 | Nov 2025 | Initial Release mit Flask Backend |

---

## 🤝 Support

Bei Fragen oder Problemen:
1. Logs prüfen: `docker-compose logs -f`
2. Health Status: `curl http://localhost:5000/health`
3. ARCHITECTURE.md konsultieren

---

**Entwickelt für professionelle juristische Dokumenten-Erstellung mit BHK-Standard.**
