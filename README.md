# PDF Q&A LLM API

## Overview

This API provides a service for querying the contents of PDF documents using AI-powered language models. The core functionality includes:

- Uploading PDF files for indexing
- Querying documents for answers based on content
- General AI-based question-answering without any document context

The system uses **Ollama's Mistral model** for AI-based querying, **Chroma** for document vector storage and retrieval, and **LangChain** for document processing and AI integration. The vector store is used for storing document embeddings, enabling fast retrieval for queries.

## Features

1. **Upload PDF Files**: Allows users to upload PDF files, which are parsed and indexed for future querying.
2. **Query PDF Documents**: After uploading, users can query the document's content. The system retrieves relevant sections from the document and provides answers.
3. **General AI Queries**: Users can ask general questions without any document context.
4. **CORS Enabled**: The API supports cross-origin requests, allowing it to be used with front-end applications from different domains.

## Endpoints

### 1. `/ai` (POST)

- **Description**: A general AI query endpoint without any PDF context
- **Request Body**: JSON object with a query string
  ```json
  {
    "query": "What is the capital of France?"
  }
  ```
- **Response**: JSON object containing the answer
  ```json
  {
    "answer": "Paris"
  }
  ```

### 2. `/ask_pdf` (POST)

- **Description**: Query a PDF document based on its content
- **Request Body**: JSON object with a query string
  ```json
  {
    "query": "What is the purpose of machine learning?"
  }
  ```
- **Response**: JSON object containing the answer and sources
  ```json
  {
    "answer": "Machine learning is used to build systems that can improve automatically through experience.",
    "sources": [
      {
        "source": "Document.pdf",
        "page_content": "Machine learning enables systems to learn from data."
      }
    ]
  }
  ```

### 3. `/pdf` (POST)

- **Description**: Upload and index a PDF file for querying
- **Request Body**: A multipart form-data file upload
- **Response**: JSON object with upload status and details
  ```json
  {
    "status": "Successfully Uploaded",
    "filename": "document.pdf",
    "doc_len": 100,
    "chunks": 10
  }
  ```

### 4. `/health` (GET)

- **Description**: Health check endpoint for ensuring the API is running
- **Response**: JSON object with status
  ```json
  {
    "status": "healthy"
  }
  ```

## Setup

### Requirements

- Python 3.7+
- FastAPI
- Uvicorn (for running the app)
- LangChain and related libraries (langchain_community, langchain_text_splitters, etc.)
- Chroma (for vector storage)
- PDFPlumber (for parsing PDFs)
- Ollama LLM (Mistral model for AI queries)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/pdf-qa-llm-api.git
   cd pdf-qa-llm-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI app with Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at http://localhost:8000.

## Docker Setup

### Dockerization

This project is Dockerized, so you can run the API and its dependencies using Docker and Docker Compose.

1. Build the Docker containers:
   ```bash
   docker-compose build
   ```

2. Start the Docker containers:
   ```bash
   docker-compose up
   ```

3. Stopping the containers:
   ```bash
   docker-compose down
   ```

### Docker Compose File

The `docker-compose.yml` file is set up to build two services:
- `web`: The FastAPI app that runs on port 8000
- `ollama`: The Ollama LLM container running on port 11434

The volumes for pdf and db directories are mounted, ensuring persistence of uploaded PDFs and vector data.

Example Docker Compose Configuration:
```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./db:/app/db
      - ./pdf:/app/pdf
    depends_on:
      - ollama

  ollama:
    build: ./ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

volumes:
  ollama-data:
```

### Dockerfile

The following Dockerfile is used to build the FastAPI app container:

```dockerfile
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
```

## Usage

1. **Uploading PDFs**: Use the `/pdf` endpoint to upload a PDF file. The file will be saved, processed, and indexed.
2. **Querying PDFs**: After uploading a PDF, use the `/ask_pdf` endpoint to ask questions based on the document's content.
3. **General Queries**: Use the `/ai` endpoint to ask general AI questions without any document context.

### Example

#### Uploading a PDF

To upload a PDF, you can use a tool like Postman or cURL:

```bash
curl -X 'POST' \
  'http://localhost:8000/pdf' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path/to/your/document.pdf'
```

#### Querying the PDF

Once the PDF is uploaded, you can query it:

```bash
curl -X 'POST' \
  'http://localhost:8000/ask_pdf' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "What is the main topic of the document?"
}'
```

#### Health Check

To check if the API is running:

```bash
curl -X 'GET' 'http://localhost:8000/health'
```
