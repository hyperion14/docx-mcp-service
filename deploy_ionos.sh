#!/bin/bash
#
# IONOS Deployment Script for DOCX Generator + MCP Server
# Server IP: 217.160.216.231
#

set -e  # Exit on error

echo "=========================================="
echo "IONOS Deployment - DOCX Generator Service"
echo "=========================================="
echo ""

# Configuration
IONOS_IP="217.160.216.231"
IONOS_USER="root"  # Ändern Sie dies, falls Sie einen anderen User verwenden
PROJECT_DIR="/opt/docx_service"

echo "📋 Configuration:"
echo "   Server IP: $IONOS_IP"
echo "   User: $IONOS_USER"
echo "   Target Directory: $PROJECT_DIR"
echo ""

# Check if we have SSH access
echo "🔍 Checking SSH access to IONOS server..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes $IONOS_USER@$IONOS_IP exit 2>/dev/null; then
    echo "✅ SSH access confirmed"
else
    echo "⚠️  SSH access check failed. You may need to configure SSH keys."
    echo ""
    echo "To set up SSH access:"
    echo "1. Generate SSH key: ssh-keygen -t ed25519"
    echo "2. Copy to server: ssh-copy-id $IONOS_USER@$IONOS_IP"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📦 Step 1: Creating deployment package..."

# Create temporary deployment directory
DEPLOY_DIR="/tmp/docx_service_deploy"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy necessary files
cp -r \
    app.py \
    mcp_server.py \
    requirements.txt \
    Dockerfile \
    Dockerfile.mcp \
    docker-compose.mcp.yml \
    .env \
    templates \
    $DEPLOY_DIR/

echo "✅ Package created"

echo ""
echo "📤 Step 2: Uploading to IONOS server..."

# Create directory on server
ssh $IONOS_USER@$IONOS_IP "mkdir -p $PROJECT_DIR"

# Upload files
scp -r $DEPLOY_DIR/* $IONOS_USER@$IONOS_IP:$PROJECT_DIR/

echo "✅ Files uploaded"

echo ""
echo "🔧 Step 3: Installing Docker on IONOS (if not installed)..."

ssh $IONOS_USER@$IONOS_IP << 'ENDSSH'
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        systemctl enable docker
        systemctl start docker
        echo "✅ Docker installed"
    else
        echo "✅ Docker already installed"
    fi

    # Check if Docker Compose is installed
    if ! docker compose version &> /dev/null; then
        echo "Installing Docker Compose plugin..."
        apt-get update
        apt-get install -y docker-compose-plugin
        echo "✅ Docker Compose installed"
    else
        echo "✅ Docker Compose already installed"
    fi
ENDSSH

echo ""
echo "🐳 Step 4: Building and starting Docker containers..."

ssh $IONOS_USER@$IONOS_IP << ENDSSH
    cd $PROJECT_DIR

    # Stop existing containers
    echo "Stopping existing containers..."
    docker-compose -f docker-compose.mcp.yml down 2>/dev/null || true

    # Build and start
    echo "Building containers..."
    docker-compose -f docker-compose.mcp.yml build

    echo "Starting containers..."
    docker-compose -f docker-compose.mcp.yml up -d

    echo "Waiting for services to start..."
    sleep 5

    # Show status
    echo ""
    echo "Container status:"
    docker-compose -f docker-compose.mcp.yml ps
ENDSSH

echo ""
echo "🔥 Step 5: Configuring firewall..."

ssh $IONOS_USER@$IONOS_IP << 'ENDSSH'
    # Install ufw if not present
    if ! command -v ufw &> /dev/null; then
        echo "Installing ufw..."
        apt-get update
        apt-get install -y ufw
    fi

    # Configure firewall
    echo "Configuring firewall rules..."
    ufw allow 22/tcp    # SSH
    ufw allow 5000/tcp  # DOCX Generator
    ufw allow 7860/tcp  # MCP Server

    # Enable firewall (if not already enabled)
    echo "y" | ufw enable 2>/dev/null || true

    echo "Firewall status:"
    ufw status
ENDSSH

echo ""
echo "✅ Step 6: Testing services..."

echo "Testing DOCX Generator Health..."
if curl -s -f http://$IONOS_IP:5000/health > /dev/null; then
    echo "✅ DOCX Generator is healthy"
    curl -s http://$IONOS_IP:5000/health | python3 -m json.tool
else
    echo "⚠️  DOCX Generator health check failed"
fi

echo ""
echo "Testing MCP Server Health..."
if curl -s -f http://$IONOS_IP:7860/health > /dev/null; then
    echo "✅ MCP Server is healthy"
else
    echo "⚠️  MCP Server health check failed"
fi

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📋 Service URLs:"
echo "   DOCX Generator: http://$IONOS_IP:5000"
echo "   Health Check:   http://$IONOS_IP:5000/health"
echo "   MCP Server:     http://$IONOS_IP:7860/sse"
echo ""
echo "🔑 Configuration:"
echo "   API Key: a08462e2e9a4ec542c91c55aa9c02e8840856d173dd306fbbdff60d0117e81d6"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Test DOCX Generation:"
echo "   curl -X POST http://$IONOS_IP:5000/generate_docx \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'Authorization: Bearer a08462e2e9a4ec542c91c55aa9c02e8840856d173dd306fbbdff60d0117e81d6' \\"
echo "     -d '{\"text\": \"Test Dokument\", \"filename\": \"test\"}'"
echo ""
echo "2. Connect MCP Server to chat.mistral.ai:"
echo "   - Go to: https://chat.mistral.ai/"
echo "   - Settings → MCP Servers → Add Server"
echo "   - URL: http://$IONOS_IP:7860/sse"
echo ""
echo "3. Optional - Set up HTTPS with nginx + Let's Encrypt:"
echo "   See: DEPLOYMENT.md for instructions"
echo ""
echo "📊 View logs:"
echo "   ssh $IONOS_USER@$IONOS_IP 'cd $PROJECT_DIR && docker-compose -f docker-compose.mcp.yml logs -f'"
echo ""
echo "🔄 Restart services:"
echo "   ssh $IONOS_USER@$IONOS_IP 'cd $PROJECT_DIR && docker-compose -f docker-compose.mcp.yml restart'"
echo ""

# Cleanup
rm -rf $DEPLOY_DIR
