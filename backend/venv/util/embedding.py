from sentence_transformers import SentenceTransformer
import threading

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None

_lock = threading.Lock()


def get_model():
    global _model

    if _model is None:

        with _lock:

            if _model is None:

                print("Loading embedding model...")

                _model = SentenceTransformer(
                    MODEL_NAME
                )

                print("Embedding model loaded.")

    return _model


def create_embedding(text):

    model = get_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()