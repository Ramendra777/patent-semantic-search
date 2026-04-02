# Technical Document Search System

## Project Overview

This is a comprehensive search system for technical documents (patents and research papers), allowing users to retrieve semantically similar content based on natural language queries. 

In addition to core semantic search, this system features an advanced sub-topic generation pipeline that clusters search results and visualizes their velocity and trends over time via an interactive heatmap. It uses a modern technology stack composed of:
- **Backend**: Python with FastAPI
- **Frontend**: NuxtJS (Vue 3) + Tailwind CSS + Chart.js
- **Vector Database**: Milvus
- **Deployment**: Docker Compose

## Approach

### 1. Data Ingestion & Embeddings
The data processing pipeline parses the provided `g_patent_abstract.tsv` dataset and fetches scholarly articles interactively from the OpenAlex API (bypassing the need to download the hundreds of GB snapshot). Both sets of data are embedded using the `all-MiniLM-L6-v2` dense embedding model from `sentence-transformers`, which maps text logic to 384-dimensional vectors. 

### 2. Semantic Search
User queries submitted via the NuxtJS UI are routed through the FastAPI backend to generate a query vector. Milvus executes an Approximate Nearest Neighbor (ANN) search using Cosine distance to return the 50 most semantically relevant documents almost instantly.

### 3. Sub-topic Clustering & Trends
Instead of pre-clustering millions of documents, the backend performs **dynamic on-the-fly clustering** of the top 50 highly-relevant returned documents using `scikit-learn` KMeans. 
Once clustered, the temporal growth (velocity) of each topic is isolated by publication year, and passed to the frontend for visualization in a multi-series line chart (Trend Map), offering an immediate macroscopic view of the area of research.

## How to Run

### Prerequisites
- **Docker & Docker Compose**: For running the Milvus vector database.
- **Python 3.10+**: For the backend and data ingestion.
- **Node.js 20+**: For the frontend UI.

### Step 1: Start the Vector Database
Launch Milvus and its mandatory dependencies (etcd, minio) using Docker:
```bash
docker-compose up -d etcd minio standalone
```

### Step 2: Seed the Data
Navigate to the `data_processing` directory to ingest patents and research papers:
```bash
cd data_processing
pip install -r requirements.txt
python ingest.py
```

### Step 3: Launch the Backend API
Start the FastAPI server (it connects to Milvus at `localhost:19530`):
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Step 4: Launch the Frontend UI
Start the Nuxt 3 development server:
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser to start searching.

## Assumptions, Challenges, and Trade-offs

1. **OpenAlex Data Dump vs API**: The instructions recommended downloading the OpenAlex snapshot format. Due to storage constraints and massive data processing overheads, fetching a randomized 30-50k subset via the OpenAlex API is fundamentally faster and practically mimics the exact requirements.
2. **On-the-fly vs Pre-computed Clustering**: Sub-topic clustering is performed dynamically on search results rather than pre-clustering the entire vector database. This choice avoids the "curse of dimensionality" across the complete dataset and guarantees clusters are hyper-specific to the exact context the user researched.
3. **Missing Metadata in Abstract TSV**: The `g_patent_abstract.tsv` dataset contains only abstracts and IDs. For proper demonstration of the trend mapping features, publication dates and citations for these patents were augmented probabilistically during testing, whereas actual OpenAlex documents use their authoritative dates.
