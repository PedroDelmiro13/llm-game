from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
import time

app = FastAPI()

origins = [
    "https://llm-game-gamma.vercel.app",   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
all_chunks = None
embeddings = None

def load_data():
    global all_chunks, embeddings
    from src.data_processing import fetch_pages, clean_text, chunk_text
    from src.embeddings import generate_embeddings

    print("Carregando dados...")
    pages = fetch_pages()
    all_chunks = []
    for page in pages:
        clean = clean_text(page)
        chunks = chunk_text(clean)
        all_chunks.extend(chunks)
    print(f"{len(all_chunks)} chunks")

    print("Gerando embeddings...")
    embeddings = generate_embeddings(all_chunks)
    print("Pronto!")

threading.Thread(target=load_data, daemon=True).start()

@app.get("/")
def check():
    return {"status": "ok", "message": "API rodando, dados carregando em background"}

class QueryRequest(BaseModel):
    query: str

@app.post("/search")
def search_endpoint(request: QueryRequest):
    global all_chunks, embeddings
    start_time = time.time()
    print(f"🔍 Recebida busca: '{request.query}'")

    if all_chunks is None or embeddings is None:
        return {"status": "loading", "message": "Dados ainda carregando, tente novamente em alguns segundos"}

    from src.search import search
    from src.embeddings import generate_embeddings 

    results, query_embedding = search(
        request.query,
        all_chunks,
        embeddings,
        generate_embeddings
    )
    elapsed = time.time() - start_time
    print(f" Busca concluída em {elapsed:.2f} segundos. {len(results)} resultados.")

    return {
        "query_embedding": query_embedding.tolist(),
        "results": [
            {"score": float(score), "text": text}
            for text, score in results
        ]
    }