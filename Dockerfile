FROM python:3.12.7-slim

# Set the working directory inside the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
build-essential \
python3-dev \
&& rm -rf /var/lib/apt/lists/*

# Copy application files
COPY main.py requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Create necessary directories
RUN mkdir -p db pdf

# Expose the app port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]