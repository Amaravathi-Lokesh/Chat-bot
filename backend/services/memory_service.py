from db_model import ChatMemory
class MemoryService:

    def save_memory(self,db,chat_id,key,value,memory_type="FACT"):

        old=(
            db.query(ChatMemory)

            .filter(

                ChatMemory.chat_id==chat_id,

                ChatMemory.key==key

            )

            .first()

        )

        if old:

            old.value=value

        else:

            obj=ChatMemory(

                chat_id=chat_id,

                key=key,

                value=value,

                memory_type=memory_type

            )

            db.add(obj)

        db.commit()
    def load_memory(self,db,chat_id):

        data=(
            db.query(ChatMemory)
            .filter(
                ChatMemory.chat_id==chat_id
            )
            .all()
        )
        text=""
        for item in data:
            text+=f"{item.key}:{item.value}\n"
        return text