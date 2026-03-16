# =============================================================================
# Dockerfile - Container configuration for the FastAPI application
# =============================================================================
# Build the image:    docker build -t todo-api .
# Run the container:  docker run -p 8000:8000 todo-api
# =============================================================================

# Use Python 3.11 slim image as the base
# "slim" means it's smaller than the full image (fewer pre-installed packages)
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Ensures Python output is sent straight to the terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy only the requirements file first (for Docker layer caching)
# This way, if only the code changes, dependencies are NOT reinstalled
COPY src/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src/ .

# Expose the port that the application will listen on
EXPOSE 8000

# Health check - Docker will use this to monitor the container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Command to run the application
# host=0.0.0.0 makes it accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
