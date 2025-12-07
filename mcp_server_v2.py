#!/usr/bin/env python3
"""
MCP Server for DOCX Generation - Integrated Version
Pure MCP implementation - file serving handled by Nginx
"""

import os
import threading
import logging
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from docx_logic import generate_docx_from_text, archive_files_after_delay
from starlette.requests import Request
from starlette.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MCP_Server")

# Load environment variables
load_dotenv()

# Configuration
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/app/docx_files")
ARCHIVE_FOLDER = os.getenv("ARCHIVE_FOLDER", "/app/archive")
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://mcp.eunomialegal.de")
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "/app/templates/bhk-base.docx")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

# Initialize MCP Server
mcp = FastMCP(
    name="DOCXGenerator",
    host="0.0.0.0",
    port=7860
)

print(f"""
{'='*60}
MCP Server for DOCX Generation (Integrated)
{'='*60}
Protocol: Model Context Protocol with SSE Transport
Upload Folder: {UPLOAD_FOLDER}
Public URL: {PUBLIC_URL}
Note: File downloads served by Nginx at {PUBLIC_URL}/download/
{'='*60}
""")


@mcp.tool()
def generate_docx_document(text: str) -> str:
    """
    Generiert ein DOCX-Dokument aus dem bereinigten Diktat-Text und gibt einen Download-Link zurück.

    Dieser Service erstellt formatierte Word-Dokumente für juristische Texte.
    
    Verwenden Sie dieses Tool SOFORT, wenn der Nutzer die Erstellung eines Word-Dokuments wünscht.

    Args:
        text: Der Text für das Dokument (Pflichtfeld)

    Returns:
        str: Statusmeldung mit Download-Link
    """
    import json
    
    filename = "diktat_vergaberecht"
    
    print(f"📤 MCP Tool called: generate_docx_document")
    print(f"📄 Filename: {filename}.docx")
    print(f"📝 Text length: {len(text)} characters")

    try:
        # Generate DOCX (Synchronous call is fine in FastMCP threadpool)
        docx_filename, txt_filename = generate_docx_from_text(
            text, 
            UPLOAD_FOLDER, 
            TEMPLATE_PATH, 
            filename
        )
        
        # Generate download URL
        download_url = f"{PUBLIC_URL}/download/{docx_filename}"
        
        # Calculate expiry time (24 hours)
        expires_at = datetime.now().timestamp() + 86400
        
        # Schedule file deletion and archival
        threading.Thread(
            target=archive_files_after_delay,
            args=(docx_filename, txt_filename, UPLOAD_FOLDER, ARCHIVE_FOLDER, 86400),
            daemon=True
        ).start()
        
        
        print(f"✅ DOCX generated successfully: {download_url}")

        # Return plain text message instead of JSON for better Mistral agent display
        message = f"""✅ Dokument erfolgreich erstellt!

📄 **Datei:** {docx_filename}

📥 **Download-Link:**
{download_url}

💡 **Hinweis:** 
- Rechtsklick → 'Link speichern unter...' wenn der direkte Download nicht funktioniert
- Ihr Browser könnte die Datei als 'ungewöhnlich' markieren - dies ist normal für neue Services
- Klicken Sie auf 'Trotzdem herunterladen' - die Datei ist sicher!

⏱️ **Link gültig bis:** {datetime.fromtimestamp(expires_at).strftime('%d.%m.%Y %H:%M')} Uhr (24 Stunden)
"""
        
        return message


    except Exception as e:
        error_msg = f"Fehler bei der Dokumentgenerierung: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg, exc_info=True)

        return f"❌ Fehler bei der Dokumentgenerierung\n\nDetails: {str(e)}\n\nBitte versuchen Sie es erneut oder kontaktieren Sie den Support."


@mcp.tool()
def check_service_health() -> str:
    """
    Überprüft ob der DOCX Generator Service betriebsbereit ist.

    Returns:
        str: Health-Status als Text
    """
    # Check if upload folder is writable
    is_writable = os.access(UPLOAD_FOLDER, os.W_OK)
    
    if is_writable:
        return "✅ Service ist betriebsbereit\n\n📦 Version: 2.0.0\n💾 Speicher: Verfügbar\n🔒 HTTPS: Aktiv"
    else:
        return "❌ Service-Fehler\n\nSpeicher nicht verfügbar. Bitte kontaktieren Sie den Administrator."


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """
    Health check endpoint for Docker
    """
    return JSONResponse({"status": "healthy", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    print("🚀 Starting Integrated MCP Server...")
    print("📡 Listening on: 0.0.0.0:7860")
    print("🔗 MCP Endpoint: http://0.0.0.0:7860")
    print("🔗 SSE Endpoint: http://0.0.0.0:7860/sse")
    
    # Run with SSE transport
    mcp.run(transport="sse")
