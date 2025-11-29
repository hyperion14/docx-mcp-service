# Nginx Reverse Proxy Setup

Konfiguration von nginx als Reverse Proxy für den MCP Server.

## 🎯 Warum Nginx?

Nginx fungiert als Reverse Proxy und routet Requests von `mcp.eunomialegal.de`:
- `/sse` und `/` → MCP Server (Port 7860)
- `/health` → DOCX Backend (Port 5000)
- `/download/*` → DOCX Backend (Port 5000)

## 📋 Nginx Konfiguration

Die Konfiguration liegt in `/tmp/mcp_nginx.conf` und muss nach `/etc/nginx/sites-available/` kopiert werden.

### Installation

```bash
# 1. Konfiguration kopieren
sudo cp /tmp/mcp_nginx.conf /etc/nginx/sites-available/mcp.eunomialegal.de

# 2. Symlink erstellen
sudo ln -sf /etc/nginx/sites-available/mcp.eunomialegal.de /etc/nginx/sites-enabled/

# 3. Konfiguration testen
sudo nginx -t

# 4. Nginx neu laden
sudo systemctl reload nginx
```

### Konfiguration Details

Die Nginx Konfiguration beinhaltet:

**MCP Server Routing:**
```nginx
location / {
    proxy_pass http://127.0.0.1:7860;

    # SSE-spezifische Headers
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_cache off;

    # CORS für chat.mistral.ai
    add_header 'Access-Control-Allow-Origin' '*' always;
}
```

**Health Check Routing:**
```nginx
location /health {
    # Leitet zu DOCX Backend um
    proxy_pass http://127.0.0.1:5000/health;
}
```

**Wichtige Einstellungen:**
- `proxy_buffering off` - Kritisch für SSE
- `proxy_read_timeout 300s` - Lange Timeouts für SSE
- CORS Headers für Mistral Integration

## ✅ Testing

### 1. Nginx Status prüfen

```bash
sudo systemctl status nginx
```

### 2. MCP SSE Endpoint testen

```bash
curl -N http://mcp.eunomialegal.de/sse -H "Accept: text/event-stream"
```

Erwartete Response:
```
event: endpoint
data: /messages/?session_id=<session-id>
```

### 3. Health Check testen

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

### 4. Von extern testen

```bash
# Von deinem lokalen Rechner
curl -I http://mcp.eunomialegal.de/sse
```

## 🔐 SSL/HTTPS Setup (Optional)

### Let's Encrypt installieren

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx -y

# SSL-Zertifikat erhalten
sudo certbot --nginx -d mcp.eunomialegal.de

# Auto-Renewal testen
sudo certbot renew --dry-run
```

### HTTPS in Mistral nutzen

Nach SSL-Setup nutze:
```
URL: https://mcp.eunomialegal.de/sse
```

## 📊 Monitoring

### Nginx Logs

```bash
# Access Log
sudo tail -f /var/log/nginx/mcp.eunomialegal.de_access.log

# Error Log
sudo tail -f /var/log/nginx/mcp.eunomialegal.de_error.log
```

### Nginx Management

```bash
# Status prüfen
sudo systemctl status nginx

# Config testen
sudo nginx -t

# Reload (nach Config-Änderungen)
sudo systemctl reload nginx

# Restart (bei Problemen)
sudo systemctl restart nginx
```

## 🐛 Troubleshooting

### 502 Bad Gateway

**Ursache:** Backend Service läuft nicht

**Lösung:**
```bash
# Container Status prüfen
docker-compose ps

# Container starten
docker-compose up -d

# Logs prüfen
docker-compose logs mcp-server
```

### 404 Not Found

**Ursache:** Nginx Konfiguration nicht geladen

**Lösung:**
```bash
# Symlink prüfen
ls -la /etc/nginx/sites-enabled/mcp.eunomialegal.de

# Config neu laden
sudo nginx -t && sudo systemctl reload nginx
```

### Connection Timeout bei SSE

**Ursache:** Proxy Timeouts zu kurz

**Prüfen:** Die Konfiguration sollte diese Werte haben:
```nginx
proxy_read_timeout 300s;
proxy_connect_timeout 75s;
proxy_send_timeout 300s;
```

### CORS Fehler

**Prüfen:** CORS Headers sollten gesetzt sein:
```bash
curl -I http://mcp.eunomialegal.de/sse
```

Response sollte enthalten:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

## 🎯 Architektur Übersicht

```
Internet (chat.mistral.ai)
    ↓
mcp.eunomialegal.de:80
    ↓
nginx Reverse Proxy
    ├─→ /sse, / → localhost:7860 (MCP Server)
    └─→ /health → localhost:5000 (DOCX Backend)
```

## ✅ Checkliste

Nach dem Setup sollten alle Checks erfolgreich sein:

- [ ] Nginx läuft: `sudo systemctl status nginx`
- [ ] Config valid: `sudo nginx -t`
- [ ] SSE endpoint: `curl -I http://mcp.eunomialegal.de/sse` → 200 OK
- [ ] Health endpoint: `curl http://mcp.eunomialegal.de/health` → JSON response
- [ ] Von extern erreichbar
- [ ] Mistral kann sich verbinden

## 📚 Weitere Infos

- [Nginx Reverse Proxy Docs](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [SSE mit Nginx](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering)
- [Let's Encrypt](https://letsencrypt.org/)
