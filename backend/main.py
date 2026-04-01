from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Document Search System API")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.search import router as search_router

app.include_router(search_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Search System API"}
