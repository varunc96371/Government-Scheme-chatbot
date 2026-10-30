import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
from sentence_transformers import SentenceTransformer

try:
    model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
except Exception:
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        model = None

def generate_embedding(text):
    """
    Generate a semantic embedding for the given text using S-BERT.
    """
    if model is None:
        import numpy as np
        return np.zeros((len(text), 384))
    embedding = model.encode(text)
    return embedding