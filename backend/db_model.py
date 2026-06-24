# from polars import datetime
import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text,ForeignKey,JSON,Float
from sqlalchemy.orm import relationship
from database import Base
import datetime
from services.openai_embedding import create_embedding
from pgvector.sqlalchemy import Vector
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) 
    summary = Column(Text, default="")
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String)
    chat_id = Column(Integer, ForeignKey("chats.id"))

    filename = Column(String)
    filepath = Column(String)

    extracted_text = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document"
    )
from sqlalchemy.orm import relationship

class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id = Column(Integer,primary_key=True)
    document_id = Column(Integer,ForeignKey("documents.id"))
    chunk_number = Column(Integer)
    topic=Column(String)
    keywords = Column(String)
    source=Column(String)
    page_number=Column(Integer)
    token_count=Column(Integer)
    chunk_text = Column(Text)
    embedding = Column(Vector(1536))
    document = relationship(
        "Document",
        back_populates="chunks"
    )
class ActiveEntity(Base):

    __tablename__="active_entities"

    id=Column(Integer,primary_key=True)

    chat_id=Column(Integer)

    entity=Column(String)

    entity_type=Column(String)

    confidence=Column(Float)
class ChatMemory(Base):

    __tablename__="chat_memory"

    id=Column(Integer,primary_key=True,index=True)

    chat_id=Column(Integer,index=True)

    memory_type=Column(String)

    key=Column(String)

    value=Column(Text)

    confidence=Column(Float,default=1.0)
class ResponseCache(Base):
    __tablename__ = "response_cache"

    id = Column(Integer, primary_key=True)

    question = Column(Text)

    embedding = Column(JSON)

    answer = Column(Text)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)