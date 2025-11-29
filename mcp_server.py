#!/usr/bin/env python3
"""
MCP Server for DOCX Generation - Mistral Spec-compliant Implementation
Implements Model Context Protocol with SSE transport for chat.mistral.ai integration

Based on Mistral MCP specification: https://docs.mistral.ai/capabilities/agents/
"""

import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import requests

# Load environment variables
load_dotenv()

# Configuration
DOCKER_IP = os.getenv("DOCKER_IP", "http://docx-generator:5000")
DOCKER_API_KEY = os.getenv("DOCKER_API_KEY")

# Initialize MCP Server
# IMPORTANT: Mistral requires no spaces in server name
mcp = FastMCP(
    name="DOCXGenerator",
    host="0.0.0.0",
    port=7860
)

print(f"""
{'='*60}
MCP Server for DOCX Generation (Mistral Spec-compliant)
{'='*60}
Protocol: Model Context Protocol with SSE Transport
Docker Backend: {DOCKER_IP}
API Key: {'Configured' if DOCKER_API_KEY else 'Not configured'}
{'='*60}
""")


@mcp.tool()
def generate_docx_document(text: str, filename: str = "diktat_vergaberecht") -> dict:
    """
    Generiert ein DOCX-Dokument aus dem bereinigten Diktat-Text und gibt einen Download-Link zurück.

    Dieser Service erstellt formatierte Word-Dokumente für juristische Texte,
    insbesondere für Vergaberecht-Gutachten und Diktate.

    Args:
        text: Der bereinigte und vom Nutzer bestätigte Diktat-Text (Pflichtfeld)
        filename: Optionaler Dateiname für das Dokument ohne .docx-Endung (Standard: diktat_vergaberecht)

    Returns:
        dict: Antwort mit folgenden Feldern:
            - status: "success" oder "error"
            - download_url: URL zum Herunterladen des generierten DOCX
            - filename: Name der generierten Datei
            - expires_at: Ablaufzeitpunkt des Download-Links
            - message: Statusmeldung für den Nutzer
    """
    # Docker Service Endpunkt
    url = f"{DOCKER_IP}/generate_docx"

    # Headers mit Authentication für Backend-Service
    headers = {
        "Authorization": f"Bearer {DOCKER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Payload für Backend-Service
    payload = {
        "text": text,
        "filename": filename
    }

    print(f"📤 MCP Tool called: generate_docx_document")
    print(f"📄 Filename: {filename}.docx")
    print(f"📝 Text length: {len(text)} characters")

    try:
        # POST Request zum Docker Backend Service
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()

        print(f"✅ DOCX generated successfully: {result.get('download_url')}")

        return {
            "status": "success",
            "download_url": result.get("download_url"),
            "filename": result.get("filename"),
            "expires_at": result.get("expires_at"),
            "message": f"Dokument erfolgreich erstellt! Download-Link: {result.get('download_url')}"
        }

    except requests.exceptions.RequestException as e:
        error_msg = f"Fehler beim Aufruf des DOCX Generators: {str(e)}"
        print(f"❌ {error_msg}")

        return {
            "status": "error",
            "error": error_msg,
            "message": "Die Dokumentgenerierung ist fehlgeschlagen. Bitte versuchen Sie es später erneut oder kontaktieren Sie den Support."
        }


@mcp.tool()
def check_service_health() -> dict:
    """
    Überprüft ob der DOCX Generator Backend-Service erreichbar und betriebsbereit ist.

    Führt einen Health-Check gegen den Backend-Service durch um sicherzustellen,
    dass Dokumente generiert werden können.

    Returns:
        dict: Health-Status mit folgenden Feldern:
            - status: "healthy" oder "unhealthy"
            - service: Name des Backend-Services
            - version: Version des Backend-Services
            - message: Statusmeldung
    """
    url = f"{DOCKER_IP}/health"

    print(f"🏥 Health check requested for: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        result = response.json()

        print(f"✅ Backend service is healthy")

        return {
            "status": "healthy",
            "service": result.get("service", "docx-generator"),
            "version": result.get("version", "unknown"),
            "message": "DOCX Generator Backend-Service ist erreichbar und betriebsbereit."
        }

    except requests.exceptions.RequestException as e:
        error_msg = f"Service nicht erreichbar: {str(e)}"
        print(f"❌ {error_msg}")

        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "DOCX Generator Backend-Service ist nicht erreichbar. Bitte kontaktieren Sie den Administrator."
        }


if __name__ == "__main__":
    # Run MCP Server with SSE transport (Mistral spec-compliant)
    # This creates endpoints:
    # - POST / -> JSON-RPC requests (initialize, tools/list, tools/call)
    # - GET /sse -> SSE stream for server-to-client messages

    print("🚀 Starting MCP Server...")
    print("📡 Listening on: 0.0.0.0:7860")
    print("🔗 MCP Endpoint: http://0.0.0.0:7860")
    print("🔗 SSE Endpoint: http://0.0.0.0:7860/sse")
    print("")
    print("Available MCP tools:")
    print("  - generate_docx_document(text, filename?)")
    print("  - check_service_health()")
    print("")
    print("Waiting for MCP connections from chat.mistral.ai...")
    print("="*60)

    # Run with SSE transport (Mistral spec-compliant)
    # This automatically handles:
    # - JSON-RPC 2.0 protocol
    # - initialize handshake
    # - tools/list responses
    # - tools/call execution
    # - SSE streaming
    mcp.run(transport="sse")
