from fastapi import FastAPI
from pydantic import BaseModel
import threading

app = FastAPI()

all_chunks = None
embeddings = None
model = None

def load_data():
    global all_chunks, embeddings, model
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
    
    if all_chunks is None or embeddings is None:
        return {"status": "loading", "message": "Dados ainda carregando, tente novamente em alguns segundos"}
    
    from src.search import search
    results, query_embedding = search(
        request.query,
        all_chunks,
        embeddings,
        generate_embeddings 
    )
    
    return {
        "query_embedding": query_embedding.tolist(),
        "results": [
            {"score": float(score), "text": text}
            for text, score in results
        ]
    }