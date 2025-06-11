FROM python:3.11-slim

WORKDIR /app

# Copy requirements files
COPY backend/requirements.txt /app/backend-requirements.txt
COPY ai/requirements.txt /app/ai-requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/backend-requirements.txt -r /app/ai-requirements.txt

# Create the directory structure
RUN mkdir -p /app/src/ai

# Copy backend application code to /app/src
COPY backend/src/ /app/src/
# Copy AI application code to /app/src/ai
COPY ai/src/ /app/src/ai/

# Expose the port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Command to run the application
CMD ["python", "-m", "src.main"]