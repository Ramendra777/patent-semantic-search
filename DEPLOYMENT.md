# Deployment Guide: Technical Document Search System

This guide provides instructions for deploying the Document Search System in a production-ready containerized environment.

## Prerequisites

- **Docker & Docker Compose**: Ensure they are installed and running.
- **Hardware**: At least **8GB of RAM** is recommended to run the Milvus Standalone stack comfortably.

## Quick Start (Local Production Simulation)

1.  **Clone the Repository** and navigate to the root directory.
2.  **Initialize Environment**:
    ```bash
    cp .env.example .env
    ```
3.  **Start All Services**:
    ```bash
    docker-compose up -d
    ```
4.  **Ingest Initial Data**:
    Since the database starts empty, run the ingestion script once:
    ```bash
    cd data_processing
    # Ensure you use a local python with requirements installed
    pip install -r requirements.txt
    python ingest.py
    ```

## Production Configuration

### Environment Variables (.env)
Modify your `.env` file to reflect your production domains:
- `CORS_ORIGINS`: Set this to your frontend domain (e.g., `https://search.yourdomain.com`).
- `API_BASE_URL`: Set this to your public backend URL (e.g., `https://api.yourdomain.com`).

### Persistence
The system uses Docker volumes located in the `./volumes/` directory to persist Milvus data, etcd metadata, and MinIO storage. Ensure this directory is backed up regularly.

### Reverse Proxy (Nginx)
It is highly recommended to use a reverse proxy (like Nginx or Caddy) in front of the `backend` (port 8000) and `frontend` (port 3000) to handle SSL (HTTPS) and routing.

## Troublshooting

- **Memory Errors**: If Milvus fails to start, check if your system has enough available RAM.
- **Connection Issues**: Ensure all services share the same Docker network (default created by docker-compose).
- **Ingestion Failures**: If you hit rate limits while fetching papers, provide an `HF_TOKEN` in the `.env` file.
