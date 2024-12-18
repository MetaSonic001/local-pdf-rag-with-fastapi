import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate

# Create FastAPI app
app = FastAPI(
    title="PDF Q&A LLM API",
    description="API for PDF document querying using Mistral LLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configuration
UPLOAD_FOLDER = "pdf"
VECTOR_STORE_PATH = "db"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# Initialize components
cached_llm = Ollama(model="mistral")
embedding = FastEmbedEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
)

raw_prompt = PromptTemplate.from_template(
    """ 
    <s>[INST] You are a technical assistant good at searching documents. If you do not have an answer from the provided information say so. [/INST] </s>
    [INST] {input}
           Context: {context}
           Answer:
    [/INST]
"""
)

# Pydantic models for request validation
class QueryRequest(BaseModel):
    query: str

class PDFUploadResponse(BaseModel):
    status: str
    filename: str
    doc_len: int
    chunks: int

class SourceDocument(BaseModel):
    source: str
    page_content: str

class PDFQueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]

@app.post("/ai", response_model=Dict[str, str])
async def ai_query(request: QueryRequest):
    """
    General AI query endpoint without PDF context
    """
    try:
        response = cached_llm.invoke(request.query)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask_pdf", response_model=PDFQueryResponse)
async def ask_pdf_query(request: QueryRequest):
    """
    PDF context-based query endpoint
    """
    try:
        # Load vector store
        vector_store = Chroma(
            persist_directory=VECTOR_STORE_PATH, 
            embedding_function=embedding
        )

        # Create retrieval chain
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 20,
                "score_threshold": 0.1,
            },
        )

        document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
        chain = create_retrieval_chain(retriever, document_chain)

        # Invoke chain
        result = chain.invoke({"input": request.query})

        # Prepare sources
        sources = [
            {"source": doc.metadata["source"], "page_content": doc.page_content}
            for doc in result["context"]
        ]

        return {
            "answer": result["answer"],
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    PDF upload and indexing endpoint
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Load and process PDF
        loader = PDFPlumberLoader(file_path)
        docs = loader.load_and_split()

        # Create chunks
        chunks = text_splitter.split_documents(docs)

        # Create vector store
        vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=embedding, 
            persist_directory=VECTOR_STORE_PATH
        )
        vector_store.persist()

        return {
            "status": "Successfully Uploaded",
            "filename": file.filename,
            "doc_len": len(docs),
            "chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Note: For deployment, you'll want to use something like uvicorn to run the server
# uvicorn main:app --host 0.0.0.0 --port 8080