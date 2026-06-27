from database import SessionLocal
from db_model import DocumentChunk
from util.faiss_manger import add_vector, index, metadata

import faiss
import pickle

def rebuild_faiss():

    db = SessionLocal()

    # Clear old index
    index.reset()
    metadata.clear()

    chunks = db.query(DocumentChunk).all()

    print(f"Chunks in database: {len(chunks)}")

    for chunk in chunks:

        if chunk.embedding:

            add_vector(
                chunk.embedding,
                chunk.id,
                save=False      # <-- change here
            )

    print(f"Vectors after rebuild: {index.ntotal}")

    # Save only once
    faiss.write_index(index, "faiss.index")

    with open("faiss_meta.pkl", "wb") as f:
        pickle.dump(metadata, f)

    db.close()

    print("FAISS rebuild completed")