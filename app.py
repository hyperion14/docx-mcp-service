"""
DOCX Generator Service for Mistral Agent Integration
Receives text from Mistral Custom Agent, generates DOCX files, and provides download links.
"""

from flask import Flask, request, jsonify, send_from_directory
from docx import Document
import os
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv
import shutil

# Import docx_logic functions
from docx_logic import generate_docx_from_text, archive_files_after_delay

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/app/docx_files'
ARCHIVE_FOLDER = '/app/archive'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

# API Key for authentication
API_KEY = os.getenv("DOCKER_API_KEY", "YOUR_API_KEY")
DOCKER_IP = os.getenv("DOCKER_IP", "http://localhost:5000")

# Public URL for download links (used by external clients like Mistral)
PUBLIC_URL = os.getenv("PUBLIC_URL", DOCKER_IP)

# Optional: Template path for advanced DOCX formatting
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "/app/templates/bhk-base.docx")


def verify_api_key(request):
    """Verify API key from request headers."""
    auth_header = request.headers.get('Authorization', '')
    expected_auth = f"Bearer {API_KEY}"

    if auth_header != expected_auth:
        logger.warning(f"Unauthorized access attempt: {auth_header}")
        return False
    return True


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "docx-generator",
        "version": "1.0.0",
        "upload_folder": UPLOAD_FOLDER,
        "archive_folder": ARCHIVE_FOLDER
    }), 200


@app.route('/generate_docx', methods=['POST'])
def generate_docx():
    """
    Generate DOCX from text input.

    Expected JSON payload:
    {
        "text": "Text content to convert to DOCX",
        "filename": "optional_custom_name" (optional),
        "format_mode": "bhk" or "plain" (optional, default: "bhk")
    }

    Returns:
    {
        "download_url": "http://[PUBLIC_URL]/download/[filename]",
        "filename": "generated_filename.docx",
        "expires_at": "timestamp",
        "format_mode": "bhk" or "plain"
    }
    """
    # Authentication
    if not verify_api_key(request):
        return jsonify({"error": "Unauthorized"}), 401

    # Validate request
    if not request.json:
        return jsonify({"error": "No JSON payload provided"}), 400

    data = request.json
    text = data.get('text', '')
    custom_filename = data.get('filename', None)
    format_mode = data.get('format_mode', 'bhk')  # Default to BHK format

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Validate format_mode
    if format_mode not in ['bhk', 'plain']:
        return jsonify({"error": "Invalid format_mode. Must be 'bhk' or 'plain'"}), 400

    try:
        # Use docx_logic function for generation
        use_bhk_format = (format_mode == 'bhk')
        
        filename, txt_filename = generate_docx_from_text(
            text=text,
            output_folder=UPLOAD_FOLDER,
            template_path=TEMPLATE_PATH,
            custom_filename=custom_filename,
            use_bhk_format=use_bhk_format
        )

        logger.info(f"Generated DOCX: {filename} (format: {format_mode})")

        # Generate download URL using PUBLIC_URL (for external access via subdomain)
        download_url = f"{PUBLIC_URL}/download/{filename}"

        # Calculate expiry time (24 hours)
        expires_at = datetime.now().timestamp() + 86400

        # Schedule file deletion and archival after 24 hours
        threading.Thread(
            target=archive_files_after_delay,
            args=(filename, txt_filename, 86400),
            daemon=True
        ).start()

        return jsonify({
            "download_url": download_url,
            "filename": filename,
            "source_filename": txt_filename,
            "format_mode": format_mode,
            "expires_at": datetime.fromtimestamp(expires_at).isoformat(),
            "message": f"DOCX generated successfully in {format_mode.upper()} format. Files will be archived after 24 hours."
        }), 200

    except Exception as e:
        logger.error(f"Error generating DOCX: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Failed to generate DOCX",
            "details": str(e)
        }), 500


@app.route('/download/<filename>')
def download_file(filename):
    """
    Download a generated DOCX file.

    Args:
        filename: Name of the file to download

    Returns:
        File download or 404 if not found
    """
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        logger.warning(f"File not found: {filename}")
        return jsonify({
            "error": "File not found",
            "message": "The file may have been archived or deleted after 24 hours."
        }), 404

    logger.info(f"Downloading file: {filename}")
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


# archive_files_after_delay is now imported from docx_logic
# Kept here for backward compatibility with old function signature
def archive_files_after_delay(docx_filename, txt_filename, delay):
    """
    Backward compatibility wrapper for archive_files_after_delay.
    Calls the function from docx_logic with correct parameters.
    
    Args:
        docx_filename: Name of the DOCX file
        txt_filename: Name of the source TXT file
        delay: Delay in seconds (default: 86400 = 24 hours)
    """
    # Import and call the function from docx_logic
    from docx_logic import archive_files_after_delay as archive_func
    archive_func(
        docx_filename=docx_filename,
        txt_filename=txt_filename,
        upload_folder=UPLOAD_FOLDER,
        archive_folder=ARCHIVE_FOLDER,
        delay=delay
    )


@app.route('/list_archives', methods=['GET'])
def list_archives():
    """
    List archived files by date (admin endpoint).

    Requires authentication.

    Returns:
        JSON with archive structure
    """
    if not verify_api_key(request):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        archives = {}

        if not os.path.exists(ARCHIVE_FOLDER):
            return jsonify({"archives": {}}), 200

        for date_folder in os.listdir(ARCHIVE_FOLDER):
            date_path = os.path.join(ARCHIVE_FOLDER, date_folder)

            if os.path.isdir(date_path):
                files = os.listdir(date_path)
                archives[date_folder] = {
                    "count": len(files),
                    "files": files
                }

        return jsonify({"archives": archives}), 200

    except Exception as e:
        logger.error(f"Error listing archives: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to list archives"}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Get service statistics (admin endpoint).

    Requires authentication.

    Returns:
        Statistics about active and archived files
    """
    if not verify_api_key(request):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        active_files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
        active_docx = [f for f in active_files if f.endswith('.docx')]
        active_txt = [f for f in active_files if f.endswith('.txt')]

        archive_count = 0
        if os.path.exists(ARCHIVE_FOLDER):
            for date_folder in os.listdir(ARCHIVE_FOLDER):
                date_path = os.path.join(ARCHIVE_FOLDER, date_folder)
                if os.path.isdir(date_path):
                    archive_count += len(os.listdir(date_path))

        return jsonify({
            "active_files": {
                "docx": len(active_docx),
                "txt": len(active_txt),
                "total": len(active_files)
            },
            "archived_files": archive_count,
            "upload_folder": UPLOAD_FOLDER,
            "archive_folder": ARCHIVE_FOLDER
        }), 200

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to get statistics"}), 500


if __name__ == '__main__':
    logger.info("Starting DOCX Generator Service")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"Archive folder: {ARCHIVE_FOLDER}")
    logger.info(f"API Key configured: {'Yes' if API_KEY != 'YOUR_API_KEY' else 'No (using default)'}")

    app.run(host='0.0.0.0', port=5000, debug=False)
