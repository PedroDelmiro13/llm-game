from sentence_transformers import SentenceTransformer
_model = None
def get_model():
    global _model
    if _model is None:
        print("Carregando modelo...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Modelo carregado.")
    return _model
def generate_embeddings(texts):
    model = get_model()
    return model.encode(texts)