import numpy as np
from db_model import ResponseCache

class CacheService:

    def cosine(self,a,b):

        a=np.array(a)
        b=np.array(b)
        if len(a)!=len(b):
            return 0
        return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

    def search(self,db,embedding):

        items=db.query(ResponseCache).all()

        best=None
        best_score=0

        for item in items:

            score=self.cosine(
                embedding,
                item.embedding
            )

            if score>best_score:

                best_score=score
                best=item

        return best,best_score

    def save(self,db,question,embedding,answer):

        obj=ResponseCache(

            question=question,

            embedding=embedding,

            answer=answer

        )

        db.add(obj)

        db.commit()