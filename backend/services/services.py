# from sympy import content
from services.cache_service import CacheService
import json
import numpy as np
from services.openai_embedding import create_embedding
from providers.ai import Ai
from providers.openai import AIservice
from db_model import DocumentChunk, Message, Chat,Document,ActiveEntity
from sqlalchemy.orm import Session
from util.faiss_manger import search,get_chunk_ids
from util.selected_documents import select_documents
from services.memory_service import MemoryService
from services.memory_extractor import MemoryExtractor
from services.cache_services import CacheService
class Service:
    def __init__(self):
        self.genai = Ai()
        self.ai=AIservice()
        self.memory_service=MemoryService()
        self.memory_extractor=MemoryExtractor(self.ai)
        self.cache=CacheService()
    def retrieve_chunks(
    self,
    question,
    db,
    limit=5
):

        chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.chunk_text.contains(question)
        )
        .limit(limit)
        .all()
    )

        return chunks
    def score_chunk(self, chunk, query):

        score = 0

        words = query.lower().split()

        text = chunk.chunk_text.lower()

        for word in words:

            if word in text:
                score += 1

        return score
    def source_score(self, chunk, query):
        s=0
        if not chunk.source:
            return 0

        q=query.lower()

        src=chunk.source.lower()

        if src.replace(".pdf","") in q:
            return 1

        return 0
    def keyword_score(self, chunk, query):

        score = 0

        words = query.lower().split()

        text = chunk.chunk_text.lower()

        for word in words:

            if word in text:
                score += 1

        return score / max(len(words),1)
    def topic_score(self, chunk, query):
        s=0
        if not chunk.topic:
            return 0

        q=query.lower()

        topic=chunk.topic.lower()
        for i in q.split():
            if i in topic:
                s+=1

        return s
    def cosine_similarity(self, a, b):

        a = np.array(a)
        b = np.array(b)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0

        return np.dot(a, b) / (norm_a * norm_b)
    async def expand_query(
    self,
    query
):

        prompt = f"""
    Expand this search query.

    Rules:

    Generate:

    1 main query.

    5 related search keywords.

    Return JSON ONLY.

    Example:

    {{
    "main":"AWS",
    "keywords":[
    "Amazon Web Services",
    "Cloud Computing",
    "EC2",
    "S3",
    "Lambda"
    ]
    }}

    Query:

    {query}
    """

        response = await self.genai.generate_response(
            prompt
        )
        response = response.strip()

        response = response.replace("```json", "")

        response = response.replace("```", "")
        if hasattr(response, "content"):
            response = response.content

        response = str(response).strip()

        # response = response.strip()
        print(response)
        try:
            
            return json.loads(response)
        except:

            return {

                "main": query,

                "keywords": []

            }
    def rerank_score(self,chunk,query):

            score = 0

            query = query.lower()

            text = chunk.chunk_text.lower()

            # exact query

            if query in text:
                score += 5

            # topic match

            if chunk.topic:

                if query in chunk.topic.lower():

                    score += 3

            # keyword match

            if chunk.keywords:

                kws = chunk.keywords.lower().split(",")

                for k in kws:

                    if k.strip() in query:

                        score += 2

            # shorter chunks usually more focused

            if chunk.token_count:

                if chunk.token_count < 250:

                    score += 1

            return score
    def confidence_score(self,scores):
        if len(scores)==0:
            return 0
        return scores[0][0]
    def compress_chunk(
    self,
    chunk,
    query
):

            lines = chunk.split("\n")

            results = []

            words = query.lower().split()

            for line in lines:

                text = line.lower()

                for word in words:

                    if word in text:

                        results.append(
                            line.strip()
                        )

                        break

            if len(results)==0:

                return chunk[:500]

            return ". ".join(results)
    async def rewrite_question(
    self,
    history,
    question
):

            prompt = f"""
        Conversation:

        {history}

        Latest user question:

        {question}

        Rewrite the latest question into a standalone search query.

        Rules:

        1. Keep original meaning.

        2. Resolve pronouns.

        3. Resolve references.

        4. Return ONLY rewritten query.

        Standalone query:
        """

            rewritten = await self.genai.generate_response(
                prompt
            )

            if hasattr(rewritten, "content"):
                rewritten = rewritten.content

            rewritten = str(rewritten).strip()

            if (
                "AI service" in rewritten
                or
                len(rewritten) < 3
            ):

                return question

            return rewritten
    async def verify_answer(
    self,
    answer,
    context
):

            prompt=f"""
        You are an answer verifier.

        Document Context:

        {context}

        AI Answer:

        {answer}

        Tasks:

        1. Is the answer supported by the document?

        2. Does it contain hallucinations?

        3. Does it contradict the document?

        Reply ONLY in JSON.

        Example:

        {{
        "verified":true,
        "confidence":"HIGH",
        "reason":"Supported by document."
        }}
        """

            response=await self.genai.generate_response(
                prompt
            )

            return response
    async def extract_entity(self,text):

            prompt=f"""
        Extract the main technical entity.

        Examples:

        AWS

        Docker

        Azure

        CI/CD

        Kubernetes

        FastAPI

        Python

        Question:

        {text}

        Return ONLY one entity.

        If none:

        NONE
        """

            response=await self.genai.generate_response(
                prompt
            )

            return response.strip()
    async def filter_chunks(

    self,

    question,

    chunks

):

            context=""

            for i,c in enumerate(chunks):

                context+=f"""

        Chunk {i}

        Topic:

        {c.topic}

        Content:

        {c.chunk_text}

        """

            prompt=f"""
        Question:

        {question}

        Chunks:

        {context}

        Select only useful chunks.

        Return chunk numbers.

        Example:

        0,2

        Only numbers.
        """

            response=await self.genai.generate_response(
                prompt
            )

            return response
    async def classify_intent(self, question):

            prompt = f"""
        Classify the user query.

        Possible intents:

        CHAT
        RAG
        MEMORY

        Rules:

        CHAT:
        Greetings
        Small talk
        General conversation

        RAG:
        Document related
        Technical concepts
        Questions needing uploaded files

        MEMORY:
        User profile
        Remember this
        What is my name
        What college do I study in

        Question:

        {question}

        Return ONLY:

        CHAT
        RAG
        MEMORY
        """

            result = await self.ai.generate_response(prompt)
            if result is None:
                return "CHAT"

            return result.strip().upper()
    async def multi_query(self, question):

        prompt = f"""
    Generate 5 different search queries for RAG retrieval.

    Question:
    {question}

    Return JSON only.

    Example:

    {{
    "queries":[
    "AWS",
    "Amazon Web Services",
    "AWS cloud",
    "AWS services",
    "AWS platform"
    ]
    }}

    JSON:
    """

        response = await self.genai.generate_response(prompt)

        try:
            response=response.replace("```json","")
            response=response.replace("```","")
            response=response.strip()

            data=json.loads(response)

            return data.get("queries",[question])

        except:
            return [question]
    async def process_message(self,user_id: str,chat_id: int,content: str,db: Session):

    # Save user message

        user_msg = Message(
            user_id=user_id,
            chat_id=chat_id,
            role="user",
            content=content
        )

        db.add(user_msg)
        db.commit()
        memory=await self.memory_extractor.extract(content)
        if memory:
            for key,value in memory.items():
                self.memory_service.save_memory(db,chat_id,key,value)
        # Load chat

        chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id)
            .first()
        )
        if chat is None:
            raise Exception(f"Chat {chat_id} not found")
        # if not chat:
        #     raise HTTPException(404, "Chat not found")

        # if chat.user_id != current_user.username:
        #     raise HTTPException(403, "Unauthorized")

        if chat.title == "New Chat":

            if (
                chat.title is None
                or
                chat.title.startswith("Chat")
            ):

                title_prompt = f"""
        Generate a short title.

        Rules:
        - Maximum 5 words.
        - No punctuation.
        - Based on user question.

        Question:

        {content}

        Title:
        """

                title = await self.genai.generate_response(
                    title_prompt
                )

                chat.title = title.strip()

                db.commit()

        summary = ""

        if chat:
            summary = chat.summary or ""
        memory_context=self.memory_service.load_memory(db,chat_id)
        # Load recent messages
        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.id.asc())
            .limit(5)
            .all()
        )
        active=(db.query(ActiveEntity)
            .filter(ActiveEntity.chat_id==chat_id)
            .first()
        )

        current_entity=""

        if active:

            current_entity=active.entity
        history = ""

        for msg in messages:
            if "AI service is temporarily unavailable" in msg.content:
                continue

            history += f"{msg.role}: {msg.content}\n"
            
        search_query=content
        if current_entity:
            search_query=current_entity+" "+search_query
        if len(history.strip()):
            search_query=await self.rewrite_question(history,content)

        ################################################
        # LOAD DOCUMENTS FOR CURRENT CHAT ONLY
        ################################################

        docs = (
            db.query(Document)
            .filter(Document.chat_id == chat_id)
            .all()
        )
        sedoc=await select_documents(self.genai,content,docs)
        for d in sedoc:
            print(d.id,d.filename)
        doc_score=[]
        for d in sedoc:
            s=0
            text=d.extracted_text.lower()
            for w in search_query.lower().split():
                if w in text:
                    s+=1
                    doc_score.append((s,d))
        doc_score.sort(key=lambda x:x[0],reverse=True)
        document_ids = []

        for s,d in doc_score[:3]:
            document_ids.append(d.id)

        print("Current Chat:", chat_id)
        print("Documents:", document_ids)

        ################################################
        # SEARCH CHUNKS
        ################################################

        retrieved_chunks = []

        # query = content.lower()
        # 
        expand=await self.expand_query(search_query)
        queries=await self.multi_query(search_query)
        query_embedding=create_embedding(expand["main"])
        cached,scored=self.cache.search(db,query_embedding)
        faiss_score,faiss_id=search(query_embedding,top_k=100)
        chunk_id=get_chunk_ids(faiss_id)
        if cached and scored>0.95:
            return cached.answer
        
        
        chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.id.in_(chunk_id)
            )
            .filter(
                DocumentChunk.document_id.in_(document_ids)
            )
            
            .all()
        )
        print("========== DEBUG ==========")
        print("FAISS IDs:", faiss_id)
        print("Chunk IDs:", chunk_id)
        print("Document IDs:", document_ids)
        print("Chunks from DB:", len(chunks))
        print("===========================")
        print(
            db.query(DocumentChunk)
            .filter(DocumentChunk.id.in_(chunk_id))
            .count()
        )

        print(
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id.in_(document_ids))
            .count()
        )
        # print("loaded chunks:",chunks)
        # chunk_data = [
        #     {
        #         "id": chunk.id,
        #         "text": chunk.chunk_text
        #     }
        #     for chunk in chunks
        # ]

        # CacheService.set(
        #     cache_key,
        #     chunk_data,
        #     ttl=3600
        # )
        scores = []

        for q in queries:

            print("Searching:", q)

            query_embedding = create_embedding(q)
            # print(len(query_embedding))
            # print(query_embedding[:10])

            for chunk in chunks:

                if not chunk.embedding:
                    continue

                semantic = self.cosine_similarity(
                    query_embedding,
                    chunk.embedding
                )

                keyword = self.score_chunk(
                    chunk,
                    q
                )

                topic = self.topic_score(
                    chunk,
                    q
                )

                source = self.source_score(
                    chunk,
                    q
                )
                rerank=self.rerank_score(chunk,q)
                final_score = (

                    semantic * 0.55 +

                    keyword * 0.25 +

                    topic * 0.10 +

                    source * 0.05+
                    rerank *0.15

                )

                scores.append(

                    (

                        final_score,

                        chunk,

                        q,
                        semantic,
                        keyword,
                        topic,
                        source,
                        rerank
                    )
                )
            
        scores.sort(
            key=lambda x:x[0],
            reverse=True
        )
        

        SIMILARITY_THRESHOLD = 0.20

        unique = {}

        best_chunks = []
        for score, chunk, query_used,*rest in scores:
            if score < SIMILARITY_THRESHOLD:
                continue
            if chunk.id not in unique:

                unique[chunk.id] = query_used

                best_chunks.append(chunk)

            if len(best_chunks) >= 5:

                break
        compressed = []

        seen = set()

        for chunk in best_chunks:

            fingerprint = chunk.chunk_text[:200]

            if fingerprint not in seen:

                seen.add(fingerprint)

                compressed.append(chunk)

        best_chunks = compressed
        ###########  CONFIDENCE  ##########
        retrieval_confidence = 0
        if len(best_chunks) > 0:
            total = 0
            count = 0
            for score, chunk, query_used, *rest in scores:
                if chunk in best_chunks:
                    total += score
                    count += 1
            retrieval_confidence = total / count

        selected=await self.filter_chunks(search_query,best_chunks)
        indexes=[]

        for x in selected.split(","):

            try:

                indexes.append(int(x) )
            except:

                pass
            filtered=[]

        for i in indexes:

            if i<len(best_chunks):

                filtered.append(
                    best_chunks[i]
                )

        if len(filtered):

            best_chunks=filtered
        entity=await self.extract_entity(search_query)
        if entity!="NONE":
            old=(db.query(ActiveEntity)
                .filter(ActiveEntity.chat_id==chat_id)
                .first())
            if old:
                old.entity=1.0
            else:
                obj=ActiveEntity(
                    chat_id=chat_id,
                    entity=entity,
                    entity_type="GENERAL",
                    confidence=1.0
                )
                db.add(obj)
            db.commit()

        # best_chunks = list(unique.values())
        sources = []

        for chunk in best_chunks:

            if chunk.document:
                sources.append(
                    chunk.document.filename
                )

        sources = list(set(sources))
        cos=self.confidence_score(scores)
        cstat=""
        if cos>=1.5:
            cstat="HIGH"
        elif cos>=0.8:
            cstat="MEDIUM"
        else:
            cstat="LOW"
        print("Sources:", sources)
        source_text = ""

        if len(sources):

            source_text = "\n".join(sources)

        else:

            source_text = "No sources."

        print("Retrieved:",len(best_chunks))
       
        ################################################
        # BUILD DOCUMENT CONTEXT
        ################################################

        document_context = ""
        citations = []

        if len(best_chunks) == 0:

            document_context = ""

        else:

            for chunk in best_chunks:
                com=self.compress_chunk(chunk.chunk_text,content)
                document_context += f"""

        Source:
        {chunk.source}

        Page:
        {chunk.page_number}

        Topic:
        {chunk.topic}

        Relevent Content:
        {com}

        """

                citations.append(

                    {
                        "source": chunk.source,
                        "page": chunk.page_number,
                        "topic": chunk.topic
                    }

                )

                document_context += "\n\n"

        print("Retrieved Chunks:", len(best_chunks))
        mode = await self.classify_intent(content)
        use_document=False
        con=0.70
        if mode=="RAG" and len(best_chunks)>0 or retrieval_confidence>=con:
            use_document=True
        if use_document:
            prompt=f"""

You are a helpful AI assistant.
Confidence:
{cstat}
1.If confidence is HIGH:
use retrieved document information to answer.
2.If confidence is MEDIUM:
use document information and your knowledge.
3.If confidence is LOW:
use your own knowledge.
If document information was used,

mention the source naturally.

Never invent citations.

==================

DOCUMENT:

{document_context}

==================
LONG-TERM-MEMORY:
{memory_context}
==================
SHORT-TERM-MEMORY:

{summary}

==================

CHAT HISTORY:

{history}

==================

QUESTION:

{content}

==================

ANSWER:

"""
        elif mode=="MEMORY":
            prompt=f""""
            Your are helpful AI Assistant
            Answer using long-term memory and your own knowlege if need
            Long-Term Memory:
            {memory_context}
            Chat-history:
            {history}
            Question:
            {content}
            Answer:
            """
        else:
            prompt=f"""
                Your are helpful AI Assistant
                Answer normally using your own knowledge
                with using user values
                LONG-TERM-MEMORY:
                {memory_context}
                ==================
                SHORT-TERM-MEMORY:
                {summary}
                ==================
                CHAT HISTORY:
                {history}
                ==================
                QUESTION:
                {content}
                ==================
                ANSWER:
                """

        ################################################
        # PROMPT
        ################################################

        
        print(prompt)

        ################################################
        # AI
        ################################################

        ai_response = await self.ai.generate_response(
            prompt
        )
       
        if use_document:
            verify=await self.verify_answer(ai_response,document_context)
        else:
            verify={
                "verified":True,
                "confidence":"GENERAL",
                "reason":"Genral Knowledge"

            }
        try:

            verify = verify.replace("```json","")
            verify = verify.replace("```","")
            verify = verify.strip()
            verify = json.loads(verify)
        except:

            verify={

                "verified":True,

                "confidence":"MEDIUM",

                "reason":"Verification unavailable"

            }
        verified=verify.get("verified",True)
        confidence=verify.get("confidence","MEDIUM")
        reason=verify.get("reason","")
        
        ################################################
        # SAVE ASSISTANT
        ################################################

        bot_msg = Message(
            user_id=user_id,
            chat_id=chat_id,
            role="assistant",
            content=ai_response
        )

        db.add(bot_msg)
        db.commit()

        ################################################
        # MEMORY
        ################################################

        if chat:

            memory_prompt = f"""
Update long-term memory.

Current memory:

{summary}

Recent conversation:

{history}

Latest message:

{content}

Keep only important long-term facts.

Do not copy the whole conversation.

Return updated memory only.
"""

            new_summary = await self.ai.generate_response(
                memory_prompt
            )

            chat.summary = new_summary

            db.commit()

        ################################################
        # CLEAN RESPONSE
        ################################################

        clean_response = ai_response.strip()

        clean_response = clean_response.replace(
            "\\n",
            "\n"
        )
        self.cache.save(db,content,query_embedding,clean_response)

        return  clean_response
        
    async def stream_message(
    self,
    user_id,
    chat_id,
    content,
    db
):

        prompt = f"""
    User:

    {content}

    Assistant:
    """

        full_response = ""

        async for token in self.ai.stream_message(prompt):

            full_response += token

            yield token

        bot = Message(
            user_id=user_id,
            chat_id=chat_id,
            role="assistant",
            content=full_response
        )

        db.add(bot)
        db.commit()