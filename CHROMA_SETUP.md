# Complete Pipeline: Chroma Cloud Integration Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Breakdown](#component-breakdown)
4. [End-to-End Workflows](#end-to-end-workflows)
5. [Setup Instructions](#setup-instructions)
6. [Usage Guide](#usage-guide)
7. [API Endpoints](#api-endpoints)
8. [Troubleshooting](#troubleshooting)

---

## System Overview

Your AI-ready application now has a complete RAG (Retrieval-Augmented Generation) pipeline that:

1. **Ingests PDFs** → Reads and processes documents
2. **Creates embeddings** → Converts text to vectors using Google's API
3. **Stores in Chroma** → Manages vectors in Chroma Cloud
4. **Enables semantic search** → Finds relevant documents by meaning (not keywords)
5. **Powers your agent** → Agent uses search results to answer questions

---

## Architecture Diagram

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER APPLICATION                          │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Application (main.py)                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   /ask       │    │  /documents  │    │ Other Routes │   │
│  │   endpoint   │    │  /add/       │    │              │   │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘   │
│         │                   │                                 │
│         ↓                   ↓                                 │
│  ┌────────────────────────────────┐                          │
│  │   Agent Controller             │                          │
│  │  (llmController.py)            │                          │
│  └────────┬──────────────────┬────┘                          │
│           │                  │                                │
│           ↓                  ↓                                │
│  ┌──────────────┐    ┌──────────────────────┐               │
│  │   Agent      │    │  RAG Pipeline        │               │
│  │  (root_agent)│    │ (rag_pipeline.py)    │               │
│  └──────────────┘    └──────────┬───────────┘               │
│         ↑                       │                             │
│         │                       │                             │
│  ┌──────┴───────────────────────┴──────────┐                │
│  │                                         │                 │
│  │  ┌──────────────────────────────────┐  │                 │
│  │  │  Agent Tools                     │  │                 │
│  │  ├──────────────────────────────────┤  │                 │
│  │  │ 1. get_current_time              │  │                 │
│  │  │ 2. search_knowledge_base ◄──────┐│  │                 │
│  │  └──────────────────────────────────┘  │                 │
│  │                                         │                 │
│  │  ┌──────────────────────────────────┐  │                 │
│  │  │  Services                        │  │                 │
│  │  ├──────────────────────────────────┤  │                 │
│  │  │ • pdf_reader.py                  │  │                 │
│  │  │ • text_chunker.py                │  │                 │
│  │  │ • embedding_service.py           │  │                 │
│  │  │ • chroma_connection.py           │  │                 │
│  │  └──────────────┬───────────────────┘  │                 │
│  └─────────────────┼──────────────────────┘                 │
│                    │                                         │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │   Chroma Cloud         │
        ├────────────────────────┤
        │  API Key: CHROMA_API   │
        │  Tenant: CHROMA_TENANT │
        │  DB: CHROMA_DATABASE   │
        │                        │
        │  Collection: documents │
        │  ├─ IDs               │
        │  ├─ Embeddings        │
        │  ├─ Documents (text)  │
        │  └─ Metadata          │
        └────────────────────────┘
                     ↑
        ┌────────────────────────┐
        │  Google Embedding API  │
        │  (embedding-001)       │
        └────────────────────────┘
```

---

## Component Breakdown

### 1. **PDF Processing Pipeline** (`app/services/rag_pipeline.py`)

Orchestrates the complete document processing flow:

```python
process_pdf(pdf_path: str) → dict
    ↓
    1. read_pdf()              # Extract text from PDF
    ↓
    2. chunk_text()            # Split into 500-char chunks
    ↓
    3. generate_embeddings()   # Create vectors (768-dim)
    ↓
    4. store_embeddings_in_chroma()  # Save to Chroma Cloud
    ↓
    Returns: {success, chunks_count, vectors_stored, error}
```

**Key Points:**
- Chunk size: 500 characters (optimal for semantic search)
- Embedding model: Google's `embedding-001` (768 dimensions)
- Storage: Chroma Cloud (no local files)

### 2. **Chroma Connection** (`app/chroma_connection.py`)

Manages Chroma Cloud authentication and collection access:

```python
get_chroma_client()
├─ Validates environment variables
├─ Creates CloudClient (Singleton pattern - one per app)
└─ Returns authenticated client

get_chroma_collection()
├─ Gets existing collection or creates new one
├─ Name: "documents"
├─ Metric: cosine similarity
└─ Ready for add/query operations
```

**Singleton Pattern:** Reuses same connection for all requests (efficient)

### 3. **Search Knowledge Base Tool** (`agent/tools/search_knowledge_base.py`)

Enables agent to search your knowledge base:

```python
search_knowledge_base(query: str, top_k: int = 3) → dict
    ↓
    1. Embed query using Google API
    ↓
    2. Search Chroma with embedding
    ↓
    3. Get top 3 similar documents
    ↓
    4. Format results for agent
    ↓
    Returns: {status, results, message}
```

### 4. **Agent** (`agent/agent.py`)

LLM Agent with two tools:

```
Agent Decision Logic:
├─ Question about time?
│  └─ Use: get_current_time()
│
└─ Question about knowledge base?
   └─ Use: search_knowledge_base()
```

### 5. **API Routes** (`app/routes/chromaRoutes.py`)

REST endpoints for document management:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/documents/add/` | POST | Add documents to Chroma |
| `/documents/query/` | POST | Search documents |
| `/documents/count/` | GET | Get total documents |
| `/documents/{id}/` | DELETE | Remove document |

---

## End-to-End Workflows

### Workflow 1: Adding a Document to Your Knowledge Base

```
User uploads PDF
        ↓
POST /process-pdf endpoint (or call process_pdf() directly)
        ↓
rag_pipeline.process_pdf("path/to/doc.pdf")
        ↓
┌───────────────────────────────────────────┐
│ Step 1: Extract Text                      │
│ pdf_reader.read_pdf() → "full pdf text"   │
└───────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────┐
│ Step 2: Create Chunks                     │
│ text_chunker.chunk_text()                 │
│ Result: [                                 │
│   {chunk_id: 1, text: "...500 chars..."}  │
│   {chunk_id: 2, text: "...500 chars..."}  │
│   ...                                     │
│ ]                                         │
└───────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────┐
│ Step 3: Generate Embeddings                   │
│ embedding_service.generate_embeddings()       │
│ For each chunk:                               │
│   - Send text to Google Embedding API        │
│   - Receive 768-dim vector                   │
│   - Add to chunk: chunk['embedding']         │
│ Result: chunks_with_embeddings[]             │
└───────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────┐
│ Step 4: Store in Chroma Cloud                 │
│ store_embeddings_in_chroma()                  │
│ For each chunk:                               │
│   - chunk_id: f"chunk_{id}"                  │
│   - document: chunk['text']                  │
│   - embedding: chunk['embedding']            │
│   - metadata: {chunk_id, start_pos, end_pos} │
│                                              │
│ Chroma Cloud stores:                         │
│ • Dense vectors (768 dims)                  │
│ • Original text                             │
│ • Metadata for tracing                      │
└───────────────────────────────────────────────┘
        ↓
✓ Document searchable in knowledge base
```

**Example Code:**
```python
from app.services.rag_pipeline import process_pdf

result = process_pdf("documents/manual.pdf")
print(f"Stored {result['vectors_stored']} vectors")
# Output: Stored 45 vectors
```

---

### Workflow 2: Answering a User Question

```
User asks: "What is the return policy?"
        ↓
POST /ask/ endpoint
{
    "question": "What is the return policy?"
}
        ↓
llmController.ask_agent(question)
        ↓
Runner.run(user_message)  # Google ADK Agent Framework
        ↓
Agent receives question
        ↓
Agent decides: "This is a knowledge base question"
        ↓
Agent calls: search_knowledge_base("What is the return policy?")
        ↓
┌──────────────────────────────────────────────┐
│ Search Tool Logic:                           │
│                                              │
│ 1. Embed question                            │
│    Google API: "What is the return policy?" │
│    → [0.45, -0.12, 0.67, ...]  (768 dims)  │
│                                              │
│ 2. Query Chroma Cloud                        │
│    "Find 3 vectors most similar to this"    │
│                                              │
│ 3. Chroma computes cosine similarity         │
│    Vector 1: distance 0.15 ✓                │
│    Vector 2: distance 0.22 ✓                │
│    Vector 3: distance 0.30 ✓                │
│    Vector 4: distance 0.78 ✗                │
│                                              │
│ 4. Return top 3 documents:                  │
│    - "Returns accepted within 30 days..."   │
│    - "Refund policy: full refund for..."    │
│    - "Return shipping labels provided..."   │
└──────────────────────────────────────────────┘
        ↓
Agent receives search results
        ↓
Agent generates response:
"Based on our knowledge base, the return policy
allows returns within 30 days of purchase with
full refund. Return shipping labels are provided..."
        ↓
Response sent to user
```

**Example Code:**
```python
import requests

response = requests.post(
    "http://localhost:8000/ask/",
    json={"question": "What is the return policy?"}
)

print(response.json())
# {
#   "answer": "Based on our knowledge base, returns
#             are accepted within 30 days..."
# }
```

---

## Setup Instructions

### 1. Environment Variables

Create or update `.env`:

```env
# Google API
GOOGLE_API_KEY=your_google_api_key_here

# Chroma Cloud
CHROMA_API_KEY=your_chroma_api_key_here
CHROMA_TENANT=your_tenant_name_here
CHROMA_DATABASE=your_database_name_here
```

**How to get Chroma credentials:**
1. Sign up at [chroma.trychroma.com](https://chroma.trychroma.com)
2. Create a new project/database
3. Copy API key, tenant, and database names from dashboard

### 2. Install Dependencies

```bash
pip install chromadb
```

### 3. Start the Application

```bash
uvicorn main:app --reload
```

### 4. Verify Setup

```bash
# Check Chroma connection
curl http://localhost:8000/documents/count/
# Output: {"count": 0}
```

---

## Usage Guide

### Adding Documents

**Option 1: Direct Python**
```python
from app.services.rag_pipeline import process_pdf

result = process_pdf("path/to/document.pdf")
if result['success']:
    print(f"✓ Stored {result['vectors_stored']} vectors")
else:
    print(f"✗ Error: {result['error']}")
```

**Option 2: API Endpoint**
```bash
# Create endpoint in your routes
@app.post("/process-document/")
async def process_document(pdf_path: str):
    return process_pdf(pdf_path)

# Call it
curl -X POST "http://localhost:8000/process-document/?pdf_path=docs/manual.pdf"
```

### Querying Documents

**Direct Chroma Query:**
```bash
curl -X POST "http://localhost:8000/documents/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query_texts": ["return policy"],
    "n_results": 3
  }'
```

**Through Agent:**
```bash
curl -X POST "http://localhost:8000/ask/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the return policy?"}'
```

### Monitoring

**Get document count:**
```bash
curl http://localhost:8000/documents/count/
# {"count": 45}
```

**List documents (via search):**
```bash
curl -X POST "http://localhost:8000/documents/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query_texts": [""],
    "n_results": 10
  }'
```

---

## API Endpoints

### Document Management Routes

**POST `/documents/add/`**
```json
Request:
{
  "ids": ["doc1", "doc2"],
  "documents": ["Text 1", "Text 2"],
  "metadatas": [{"source": "file1"}, {"source": "file2"}],
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]]
}

Response:
{
  "message": "Documents added successfully",
  "count": 2,
  "ids": ["doc1", "doc2"]
}
```

**POST `/documents/query/`**
```json
Request:
{
  "query_texts": ["search term"],
  "n_results": 5,
  "where": null
}

Response:
{
  "ids": [["doc1", "doc2", "doc3"]],
  "documents": [["Text 1", "Text 2", "Text 3"]],
  "distances": [[0.15, 0.22, 0.30]],
  "metadatas": [[{...}, {...}, {...}]]
}
```

**GET `/documents/count/`**
```json
Response:
{
  "count": 45
}
```

**DELETE `/documents/{document_id}/`**
```json
Response:
{
  "message": "Document chunk_1 deleted successfully"
}
```

### LLM Routes

**POST `/ask/`**
```json
Request:
{
  "question": "What is the return policy?"
}

Response:
{
  "answer": "Based on our knowledge base, returns are accepted..."
}
```

---

## Key Concepts Explained

### Embeddings
- **What**: 768-dimensional vectors representing text meaning
- **Generated by**: Google's `embedding-001` model
- **Why**: Vectors in similar directions = semantically similar text
- **Size**: 768 numbers per chunk

### Cosine Similarity
- **Metric**: Angle between vectors (0-2 range)
- **Lower distance**: More similar
- **Your config**: Configured in Chroma collection
- **Example**:
  - Distance 0.15 = Very similar
  - Distance 0.50 = Moderately similar
  - Distance 0.90 = Very different

### Collections
- **What**: Container for documents and embeddings
- **Your collection**: "documents"
- **Stores**: IDs, vectors, text, metadata
- **Cloud-based**: Persisted in Chroma Cloud

### Chunks
- **What**: Pieces of documents (500 chars each)
- **Why**: Better search relevance than whole documents
- **Generated by**: `text_chunker.py`
- **Stored with**: Original text, embedding, metadata

---

## Troubleshooting

### Issue: "Missing Chroma Cloud credentials"
**Solution**: Verify `.env` has CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE

### Issue: "Connection refused to Chroma"
**Solution**: Check internet connection, verify Chroma credentials are correct

### Issue: "No documents returned from search"
**Solutions**:
1. Check document count: `GET /documents/count/`
2. Try simpler search terms
3. Verify embeddings were stored: Check Chroma dashboard

### Issue: "Agent not using search tool"
**Solutions**:
1. Verify `search_knowledge_base` in agent.tools list
2. Check agent instruction mentions the tool
3. Ensure knowledge base has relevant documents
4. Try asking a question your documents contain

### Issue: "Google API rate limit exceeded"
**Solution**: Add delays between embedding requests (already built into `embedding_service.py` with 1-second delays)

### Issue: "Slow search results"
**Solutions**:
1. Reduce `top_k` parameter (use 3 instead of 10)
2. Check Chroma Cloud service status
3. Verify network connection speed

---

## Performance Tips

1. **Batch Processing**
   - Process multiple PDFs at once
   - Reduces overall processing time

2. **Optimal Chunk Size**
   - 500 characters: Good balance
   - Too small: Lost context
   - Too large: Poor search relevance

3. **Search Parameters**
   - `top_k=3`: Fast, for simple questions
   - `top_k=5`: Balanced
   - `top_k=10`: Comprehensive but slower

4. **Metadata Usage**
   - Add source info to metadata
   - Helps trace answers back to source
   - Improves user trust

5. **Monitoring**
   - Regularly check `/documents/count/`
   - Monitor search quality
   - Track API usage

---

## What's Next?

1. ✅ Set up environment variables
2. ✅ Start your FastAPI app
3. ✅ Upload first PDF with `process_pdf()`
4. ✅ Test search with `/documents/query/`
5. ✅ Ask agent questions via `/ask/`
6. ✅ Monitor results and refine as needed

---

## Architecture Summary

Your system now has:

```
Documents (PDFs)
     ↓
RAG Pipeline (extract, chunk, embed, store)
     ↓
Chroma Cloud (vector database)
     ↓
Agent Tools (search_knowledge_base)
     ↓
Agent (decision-making)
     ↓
API (/ask endpoint)
     ↓
User (gets intelligent answers)
```

All powered by:
- **Google APIs**: Text embeddings
- **Chroma Cloud**: Vector storage
- **Google ADK**: Agent framework
- **FastAPI**: REST API
