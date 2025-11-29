FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/docx_files /app/archive /app/templates

# Copy application files
COPY app.py .
COPY .env .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
