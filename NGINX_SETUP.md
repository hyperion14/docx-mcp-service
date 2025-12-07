# Nginx Reverse Proxy Setup für MCP Server

> **Version:** 2.0.0  
> **Letzte Aktualisierung:** 2025-12-01  
> **Status:** Produktiv

## 🎯 Warum Nginx?

Nginx fungiert als **Reverse Proxy** und routet Requests von der öffentlichen Domain `mcp.eunomialegal.de` zu den internen Docker-Containern:

```
Internet → nginx:80 → Docker Containers
                 ├─→ /sse, / → MCP Server (localhost:7860)
                 ├─→ /health → MCP Health Check (localhost:7860)
                 └─→ /download/* → DOCX Backend (localhost:5000)
```

### Vorteile
- ✅ **SSL/TLS Terminierung** (HTTPS Support)
- ✅ **Load Balancing** (bei Bedarf)
- ✅ **CORS Handling** für Mistral Integration
- ✅ **Static File Serving** (DOCX Downloads)
- ✅ **Health Check Aggregation**

## 📋 Nginx Konfiguration

### Aktive Konfigurationsdatei

Die produktive Konfiguration liegt in:
```
/etc/nginx/sites-available/mcp.eunomialegal.de
```

Referenz-Template im Projekt:
```
docx_service/nginx_mcp.conf
```

## 🚀 Installation

### 1. Nginx installieren (falls nicht vorhanden)

```bash
sudo apt update
sudo apt install nginx -y
```

### 2. Konfiguration übertragen

```bash
# Vom Projekt-Verzeichnis aus
cd /home/developer/projects/production/docx_service

# Konfiguration kopieren
sudo cp nginx_mcp.conf /etc/nginx/sites-available/mcp.eunomialegal.de

# Symlink erstellen (aktivieren)
sudo ln -sf /etc/nginx/sites-available/mcp.eunomialegal.de /etc/nginx/sites-enabled/

# Standard-Konfiguration deaktivieren (optional)
sudo rm -f /etc/nginx/sites-enabled/default
```

### 3. Konfiguration testen

```bash
sudo nginx -t
```

**Erwartete Ausgabe:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 4. Nginx neu laden

```bash
sudo systemctl reload nginx

# Oder bei größeren Änderungen:
sudo systemctl restart nginx
```

### 5. Status prüfen

```bash
sudo systemctl status nginx
```

## 🔧 Konfiguration Details

### Vollständige Konfiguration

```nginx
server {
    listen 80;
    server_name mcp.eunomialegal.de;

    # Logging
    access_log /var/log/nginx/mcp.eunomialegal.de_access.log;
    error_log /var/log/nginx/mcp.eunomialegal.de_error.log;

    # Client body size (für größere Diktate)
    client_max_body_size 10M;

    # Timeouts für SSE/Long-Polling
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_send_timeout 300s;

    # MCP Server / SSE Endpoint
    location / {
        proxy_pass http://127.0.0.1:7860;

        # Standard Proxy Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # KRITISCH für SSE (Server-Sent Events)
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;

        # CORS Headers (für Mistral chat.mistral.ai)
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, Accept' always;

        # OPTIONS preflight für CORS
        if ($request_method = OPTIONS) {
            return 204;
        }
    }

    # Health Check Endpoint
    location /health {
        proxy_pass http://127.0.0.1:7860/health;
        access_log off;
    }

    # DOCX Download Endpoint
    location /download/ {
        proxy_pass http://127.0.0.1:5000/download/;
        
        # Headers für File Download
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Content-Disposition für Download
        add_header Content-Disposition 'attachment';
    }
}
```

### Wichtige Einstellungen erklärt

#### SSE-spezifische Headers
```nginx
proxy_set_header Connection '';
proxy_http_version 1.1;
proxy_buffering off;
proxy_cache off;
```
**Warum?**
- SSE (Server-Sent Events) benötigt persistente Connections
- Buffering würde Events verzögern
- HTTP/1.1 für keep-alive

#### Timeouts
```nginx
proxy_read_timeout 300s;
proxy_connect_timeout 75s;
proxy_send_timeout 300s;
```
**Warum?**
- MCP/SSE Connections sind langlebig
- 5 Minuten Read-Timeout für lange DOCX-Generierungen
- Verhindert vorzeitigen Connection-Abbruch

#### CORS Headers
```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
```
**Warum?**
- Mistral Chat (`chat.mistral.ai`) muss auf MCP Server zugreifen
- Cross-Origin Requests erlauben
- In Produktion: Auf `https://chat.mistral.ai` einschränken

## ✅ Testing

### 1. Nginx Status prüfen

```bash
sudo systemctl status nginx
```

**Erwartete Ausgabe:**
```
● nginx.service - A high performance web server
   Loaded: loaded (/lib/systemd/system/nginx.service; enabled)
   Active: active (running)
```

### 2. MCP SSE Endpoint testen

```bash
curl -N http://mcp.eunomialegal.de/sse \
  -H "Accept: text/event-stream"
```

**Erwartete Response:**
```
event: endpoint
data: /messages/?session_id=<session-id>
```

### 3. Health Check testen

```bash
curl http://mcp.eunomialegal.de/health
```

**Erwartete Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-01T16:00:00Z"
}
```

### 4. Von extern testen

```bash
# Von deinem lokalen Rechner (nicht vom Server)
curl -I http://mcp.eunomialegal.de/sse
```

**Erwartete Headers:**
```
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/event-stream
Access-Control-Allow-Origin: *
```

### 5. DOCX Download testen

```bash
# Erst eine DOCX generieren, dann:
curl -I http://mcp.eunomialegal.de/download/251201_1600_test.docx
```

**Erwartete Headers:**
```
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment
```

## 🔐 SSL/HTTPS Setup (Empfohlen für Produktion)

### Let's Encrypt installieren

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx -y

# SSL-Zertifikat automatisch konfigurieren
sudo certbot --nginx -d mcp.eunomialegal.de

# Folge den Prompts:
# 1. Email eingeben
# 2. Terms of Service akzeptieren
# 3. Redirect HTTP → HTTPS wählen (empfohlen)
```

### Auto-Renewal testen

```bash
# Dry-run Test
sudo certbot renew --dry-run
```

**Certbot** fügt automatisch einen Cron-Job hinzu:
```
/etc/cron.d/certbot
→ Erneuert Zertifikate automatisch alle 12 Stunden
```

### Nach SSL-Setup

Die nginx-Konfiguration wird automatisch erweitert:

```nginx
server {
    listen 443 ssl http2;
    server_name mcp.eunomialegal.de;

    # SSL Certificates (automatisch von Certbot hinzugefügt)
    ssl_certificate /etc/letsencrypt/live/mcp.eunomialegal.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.eunomialegal.de/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest der Konfiguration
}

# HTTP → HTTPS Redirect
server {
    listen 80;
    server_name mcp.eunomialegal.de;
    return 301 https://$server_name$request_uri;
}
```

### HTTPS in Mistral nutzen

Nach SSL-Setup verwende in Mistral:
```
URL: https://mcp.eunomialegal.de/sse
```

## 📊 Monitoring & Logs

### Nginx Logs

```bash
# Access Log (alle Requests)
sudo tail -f /var/log/nginx/mcp.eunomialegal.de_access.log

# Error Log (nur Fehler)
sudo tail -f /var/log/nginx/mcp.eunomialegal.de_error.log

# Beide gleichzeitig
sudo tail -f /var/log/nginx/mcp.eunomialegal.de_*.log
```

### Log Analysen

```bash
# Anzahl Requests heute
sudo grep "$(date +%d/%b/%Y)" /var/log/nginx/mcp.eunomialegal.de_access.log | wc -l

# Top 10 IPs
sudo awk '{print $1}' /var/log/nginx/mcp.eunomialegal.de_access.log | sort | uniq -c | sort -rn | head -10

# 4xx/5xx Errors
sudo grep " 4[0-9][0-9] \| 5[0-9][0-9] " /var/log/nginx/mcp.eunomialegal.de_error.log
```

### Nginx Management Commands

```bash
# Status prüfen
sudo systemctl status nginx

# Config testen (vor Reload!)
sudo nginx -t

# Reload (sanft, keine Downtime)
sudo systemctl reload nginx

# Restart (bei Problemen)
sudo systemctl restart nginx

# Stoppen
sudo systemctl stop nginx

# Starten
sudo systemctl start nginx

# Auto-Start aktivieren
sudo systemctl enable nginx
```

## 🐛 Troubleshooting

### Problem: 502 Bad Gateway

**Symptom:**
```
curl http://mcp.eunomialegal.de
→ 502 Bad Gateway
```

**Ursache:** Backend Service (Docker Container) läuft nicht

**Lösung:**
```bash
# 1. Container Status prüfen
docker-compose ps

# 2. Container Logs prüfen
docker-compose logs mcp-server
docker-compose logs docx-generator

# 3. Container starten
docker-compose up -d

# 4. Health Check
curl http://localhost:7860/health
curl http://localhost:5000/health
```

### Problem: 404 Not Found

**Symptom:**
```
curl http://mcp.eunomialegal.de/sse
→ 404 Not Found
```

**Ursache:** Nginx Konfiguration nicht aktiv

**Lösung:**
```bash
# 1. Symlink prüfen
ls -la /etc/nginx/sites-enabled/ | grep mcp

# 2. Wenn fehlt, erstellen:
sudo ln -sf /etc/nginx/sites-available/mcp.eunomialegal.de \
            /etc/nginx/sites-enabled/

# 3. Config testen und reload
sudo nginx -t && sudo systemctl reload nginx
```

### Problem: Connection Timeout bei SSE

**Symptom:**
```
SSE Connection bricht nach 60 Sekunden ab
```

**Ursache:** Proxy Timeouts zu kurz

**Lösung:**
Prüfe in `/etc/nginx/sites-available/mcp.eunomialegal.de`:
```nginx
proxy_read_timeout 300s;
proxy_connect_timeout 75s;
proxy_send_timeout 300s;
```

Falls nicht gesetzt, hinzufügen und reload:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Problem: CORS Fehler in Browser

**Symptom:**
```
Access to ... has been blocked by CORS policy
```

**Ursache:** CORS Headers fehlen

**Lösung:**
Prüfe in nginx config:
```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, Accept' always;
```

**Wichtig:** Das `always` Flag ist kritisch - setzt Header auch bei Errors!

### Problem: nginx startet nicht

**Symptom:**
```bash
sudo systemctl start nginx
→ Job failed
```

**Lösung:**
```bash
# 1. Detailed error logs
sudo journalctl -xeu nginx.service

# 2. Config testen
sudo nginx -t

# 3. Port bereits belegt?
sudo netstat -tulpn | grep :80
sudo lsof -i :80

# 4. Syntax-Fehler in Config
# → Prüfe highlighted Zeile in nginx -t Output
```

## 🎯 Architektur Übersicht

```
┌─────────────────────────────────────────┐
│  Internet (Mistral, Nutzer)             │
└───────────────┬─────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│  mcp.eunomialegal.de:80 (HTTP)                │
│  mcp.eunomialegal.de:443 (HTTPS nach SSL)     │
└───────────────┬───────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│  Nginx Reverse Proxy                          │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │ Location Routing:                       │ │
│  │                                         │ │
│  │ /sse, /        → 127.0.0.1:7860        │ │
│  │ /health        → 127.0.0.1:7860/health │ │
│  │ /download/*    → 127.0.0.1:5000/...    │ │
│  └─────────────────────────────────────────┘ │
└───────────┬────────────────────┬──────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────┐  ┌────────────────────┐
│ MCP Server          │  │ DOCX Backend       │
│ localhost:7860      │  │ localhost:5000     │
│ (Docker Container)  │  │ (Docker Container) │
└─────────────────────┘  └────────────────────┘
```

## ✅ Checkliste

Nach dem Setup sollten alle Checks grün sein:

- [ ] **Nginx läuft:** `sudo systemctl status nginx` → active (running)
- [ ] **Config valid:** `sudo nginx -t` → test is successful
- [ ] **SSE Endpoint:** `curl -I http://mcp.eunomialegal.de/sse` → 200 OK
- [ ] **Health Endpoint:** `curl http://mcp.eunomialegal.de/health` → JSON
- [ ] **Von extern erreichbar:** Test von lokalem Rechner
- [ ] **Mistral Connection:** In chat.mistral.ai Agent getestet
- [ ] **SSL aktiv (optional):** `https://mcp.eunomialegal.de/sse` → 200 OK
- [ ] **Auto-Renewal:** `sudo certbot renew --dry-run` → Successful

## 🔗 Weiterführende Links

- [Nginx Reverse Proxy Dokumentation](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [SSE mit Nginx](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering)
- [Let's Encrypt](https://letsencrypt.org/)
- [Certbot Nginx Plugin](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)

---

**Version:** 2.0.0  
**Erstellt:** 2025-12-01  
**Status:** Produktiv
