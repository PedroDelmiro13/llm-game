from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.data_processing import fetch_pages, clean_text, chunk_text
from src.embeddings import generate_embeddings
from src.search import search

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://llm-game-gamma.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Iniciando coleta de dados...")
pages = fetch_pages()

all_chunks = []
for page in pages:
    clean = clean_text(page)
    chunks = chunk_text(clean)
    all_chunks.extend(chunks)

print(f"{len(all_chunks)} chunks")

print("Gerando embeddings...")
embeddings = generate_embeddings(all_chunks)
print("Embeddings prontos")

@app.get("/")
def check():
    return {"status": "ok", "message": "API rodando normalmente"}

class QueryRequest(BaseModel):
    query: str

@app.post("/search")
def search_endpoint(request: QueryRequest):
    if not request.query or not request.query.strip():
        return {"results": []}

    if embeddings is None or len(embeddings) == 0:
        return {"results": []}

    results, query_embedding = search(
        request.query,
        all_chunks,
        embeddings,
        generate_embeddings
    )

    return {
        "query_embedding": query_embedding.tolist(),
        "results": [
            {
                "score": float(score),
                "text": text
            }
            for text, score in results
        ]
    }