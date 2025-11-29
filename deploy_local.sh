#!/bin/bash
#
# Local Deployment Script (direkt auf IONOS Server)
# Ausführen auf: 217.160.216.231
#

set -e  # Exit on error

echo "=========================================="
echo "DOCX Generator - Local Deployment"
echo "=========================================="
echo ""

# Zielverzeichnis
TARGET_DIR="/opt/docx_service"

echo "📁 Schritt 1: Verzeichnis erstellen..."
mkdir -p $TARGET_DIR

echo "📋 Schritt 2: Dateien kopieren..."
cp -v app.py $TARGET_DIR/
cp -v mcp_server.py $TARGET_DIR/
cp -v requirements.txt $TARGET_DIR/
cp -v Dockerfile $TARGET_DIR/
cp -v Dockerfile.mcp $TARGET_DIR/
cp -v docker-compose.mcp.yml $TARGET_DIR/
cp -v .env $TARGET_DIR/

# Templates kopieren
if [ -d "templates" ]; then
    echo "📄 Templates kopieren..."
    cp -rv templates $TARGET_DIR/
fi

echo "✅ Dateien kopiert nach $TARGET_DIR"

echo ""
echo "🔍 Schritt 3: Docker prüfen..."

# Docker installieren falls nicht vorhanden
if ! command -v docker &> /dev/null; then
    echo "Docker wird installiert..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installiert"
else
    echo "✅ Docker bereits installiert ($(docker --version))"
fi

# Docker Compose prüfen
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose bereits installiert ($(docker compose version))"
elif command -v docker-compose &> /dev/null; then
    echo "✅ docker-compose bereits installiert ($(docker-compose --version))"
    # Erstelle Alias für 'docker compose'
    alias docker='docker-compose'
else
    echo "⚠️  Weder 'docker compose' noch 'docker-compose' gefunden"
    echo "Versuche docker-compose zu installieren..."
    apt-get update -qq
    apt-get install -y docker-compose || curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose
    echo "✅ docker-compose installiert"
fi

echo ""
echo "🐳 Schritt 4: Container bauen und starten..."

cd $TARGET_DIR

# Alte Container stoppen
echo "Stoppe alte Container..."
docker-compose -f docker-compose.mcp.yml down 2>/dev/null || true

# Neue Container bauen
echo "Baue Container..."
docker-compose -f docker-compose.mcp.yml build

# Container starten
echo "Starte Container..."
docker-compose -f docker-compose.mcp.yml up -d

# Warten
sleep 5

echo ""
echo "📊 Container Status:"
docker-compose -f docker-compose.mcp.yml ps

echo ""
echo "🔥 Schritt 5: Firewall konfigurieren..."

# UFW installieren falls nicht vorhanden
if ! command -v ufw &> /dev/null; then
    echo "UFW wird installiert..."
    apt-get install -y ufw
fi

# Firewall Regeln
echo "Konfiguriere Firewall..."
ufw allow 22/tcp 2>/dev/null || true   # SSH
ufw allow 5000/tcp 2>/dev/null || true # DOCX Generator
ufw allow 7860/tcp 2>/dev/null || true # MCP Server

# UFW aktivieren (mit Warnung)
if ! ufw status | grep -q "Status: active"; then
    echo ""
    echo "⚠️  UFW Firewall wird aktiviert!"
    echo "   Stelle sicher, dass SSH (Port 22) erlaubt ist!"
    echo ""
    read -p "Fortfahren? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "y" | ufw enable
    fi
fi

echo ""
echo "Firewall Status:"
ufw status

echo ""
echo "✅ Schritt 6: Services testen..."

sleep 2

# Health Checks
echo "Testing DOCX Generator..."
if curl -s -f http://localhost:5000/health > /dev/null; then
    echo "✅ DOCX Generator is healthy"
    curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:5000/health
else
    echo "⚠️  DOCX Generator health check failed"
    echo "Logs:"
    docker-compose -f docker-compose.mcp.yml logs --tail=20 docx-generator
fi

echo ""
echo "Testing MCP Server..."
if curl -s -f http://localhost:7860/health > /dev/null; then
    echo "✅ MCP Server is healthy"
else
    echo "⚠️  MCP Server health check failed"
    echo "Logs:"
    docker-compose -f docker-compose.mcp.yml logs --tail=20 mcp-server
fi

echo ""
echo "=========================================="
echo "✅ Deployment abgeschlossen!"
echo "=========================================="
echo ""
echo "📋 Service URLs:"
echo "   DOCX Generator: http://217.160.216.231:5000"
echo "   Health Check:   http://217.160.216.231:5000/health"
echo "   MCP Server:     http://217.160.216.231:7860/sse"
echo ""
echo "🔑 API Key:"
echo "   a08462e2e9a4ec542c91c55aa9c02e8840856d173dd306fbbdff60d0117e81d6"
echo ""
echo "📝 Nächste Schritte:"
echo ""
echo "1. Von außen testen:"
echo "   curl http://217.160.216.231:5000/health"
echo ""
echo "2. MCP Server in chat.mistral.ai verbinden:"
echo "   URL: http://217.160.216.231:7860/sse"
echo ""
echo "3. Logs anschauen:"
echo "   cd $TARGET_DIR"
echo "   docker-compose -f docker-compose.mcp.yml logs -f"
echo ""
