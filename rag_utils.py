import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# ------------------------------------------
# 1) CONFIG: which embed model to use
# ------------------------------------------
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500  # max tokens/characters per chunk (customize as needed)
OVERLAP = 50      # overlap between chunks

# Global references to the index and data
faiss_index = None
doc_texts = []
embedder = None

def load_company_data(data_folder: str = "company_data") -> List[str]:
    """
    Load all .txt files from the data_folder and return a list of text passages.
    """
    texts = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(data_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                texts.append(content)
    return texts

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    """
    Split a single large text into overlapping chunks.
    E.g., if chunk_size=500, overlap=50, each chunk shares 50 chars with the next.
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Move start by chunk_size - overlap
        start += (chunk_size - overlap)
    
    return chunks

def initialize_faiss_index(data_folder: str = "company_data"):
    """
    Load .txt files, chunk them, embed them, build a FAISS index.
    Store references globally: faiss_index, doc_texts, embedder.
    """
    global faiss_index, doc_texts, embedder

    # 1) Load data
    raw_texts = load_company_data(data_folder)

    # 2) Chunk data
    all_chunks = []
    for txt in raw_texts:
        chunks = chunk_text(txt, CHUNK_SIZE, OVERLAP)
        all_chunks.extend(chunks)

    doc_texts = all_chunks  # store them in global doc_texts

    # 3) Initialize embedder
    embedder = SentenceTransformer(EMBED_MODEL_NAME)

    # 4) Embed all chunks
    embeddings = embedder.encode(all_chunks, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype="float32")

    # 5) Build FAISS index
    d = embeddings.shape[1]  # dimension of embeddings
    faiss_index = faiss.IndexFlatIP(d)  # inner product / cosine similarity
    faiss_index.add(embeddings)

def retrieve_context(
    query: str,
    top_k: int = 3
) -> List[Tuple[str, float]]:
    """
    Given a query, embed it, search the FAISS index,
    return top_k (chunk, score).
    """
    global faiss_index, doc_texts, embedder

    if faiss_index is None or embedder is None or not doc_texts:
        raise ValueError("FAISS index not initialized. Call initialize_faiss_index() first.")

    # 1) Embed the query
    query_emb = embedder.encode([query])
    query_emb = np.array(query_emb, dtype="float32")

    # 2) Search the index
    scores, indices = faiss_index.search(query_emb, top_k)
    # 'scores' shape: (1, top_k), 'indices' shape: (1, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        chunk_text = doc_texts[idx]
        score = scores[0][i]
        results.append((chunk_text, float(score)))

    return results
