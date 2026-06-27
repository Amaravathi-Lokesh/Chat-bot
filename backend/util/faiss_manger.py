import faiss
import numpy as np
import pickle
import os

DIMENSION=3072

INDEX_FILE="faiss.index"

META_FILE="faiss_meta.pkl"

if os.path.exists(INDEX_FILE):

    index=faiss.read_index(
        INDEX_FILE
    )

else:

    index=faiss.IndexFlatIP(
        DIMENSION
    )

if os.path.exists(META_FILE):

    with open(
        META_FILE,
        "rb"
    ) as f:

        metadata=pickle.load(f)

else:

    metadata=[]
def add_vector(embedding,chunk_id,save=True):

    vector=np.array(

        [embedding],

        dtype=np.float32

    )

    faiss.normalize_L2(
        vector
    )

    index.add(vector)

    metadata.append(chunk_id)

    if save:

        faiss.write_index(
            index,
            INDEX_FILE
        )

        with open(
            META_FILE,
            "wb"
        ) as f:

            pickle.dump(
                metadata,
                f
            )
    print("chunk id:",chunk_id)
    print("vectors:",index.ntotal)
def search(

    embedding,

    top_k=20

):

    vector=np.array(

        [embedding],

        dtype=np.float32

    )

    faiss.normalize_L2(
        vector
    )

    scores,ids=index.search(

        vector,

        top_k

    )

    return scores,ids
def get_chunk_ids(

    ids

):

    result=[]

    for i in ids[0]:

        if i==-1:

            continue

        result.append(

            metadata[i]

        )

    return result