import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Document Search System API")

# Setup CORS for the frontend
orig_env = os.getenv("CORS_ORIGINS", "*")
origins = [o.strip() for o in orig_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.search import router as search_router

app.include_router(search_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Search System API"}
