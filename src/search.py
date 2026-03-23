from sklearn.metrics.pairwise import cosine_similarity

def search(query, chunks, embeddings, embed_fn, top_k=5):
    if len(embeddings) == 0:
        return []

    query_embedding = embed_fn([query])[0]
    scores = cosine_similarity([query_embedding], embeddings)[0]
    ranked = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)

    return [(chunks[i], score) for i, score in ranked[:top_k]]