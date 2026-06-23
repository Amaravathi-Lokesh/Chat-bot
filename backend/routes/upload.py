from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
import fitz
import shutil
import os
from util.embedding import create_embedding
from util.chunker import chunk_text
from database import SessionLocal
from db_model import Document, DocumentChunk
from fastapi import Depends
# from auth import get_current_user
from util.pdf_clearer import clean_text
from util.document_parser import parse_document
from util.topic_detector import detect_topic
from util.keyword_extractor import extract_keywords
from util.faiss_manger import *
from services.document_process import process_document
router = APIRouter()

UPLOAD_DIR = "upload"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload/document")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id:str =Form(...),
    chat_id:str =Form(...)
    
):   
  
    
    path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )
     # Assuming the user object has an 'id' field
    # Save PDF
    background_tasks.add_task(
    process_document,
    path,
    file.filename,
    user_id,
    chat_id
)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Extract PDF

    pdf = fitz.open(path)

    pages = []

    for page_num, page in enumerate(pdf):

        page_text = page.get_text()

        pages.append({
            "page": page_num + 1,
            "text": page_text
        })

    pdf.close()
    full_text = ""

    for p in pages:
        full_text += p["text"] + "\n"

    text = clean_text(full_text)
    #text=clean_text(pages["text"])
    db = SessionLocal()

    # Save document

    doc = Document(
        user_id=user_id,
        chat_id=chat_id,
        filename=file.filename,
        filepath=path,
        extracted_text=text
    )

    db.add(doc)

    db.commit()

    db.refresh(doc)
    #Document parse
    all_chunks = []

    for page in pages:

        page_text = clean_text(page["text"])

        parsed = parse_document(page_text)

        page_chunks = chunk_text(
            "\n\n".join(parsed)
        )

        for chunk in page_chunks:

            all_chunks.append({

                "page": page["page"],

                "chunk": chunk

            })
    print("="*50)
    print("Chunks:", len(all_chunks))

    for i, item in enumerate(all_chunks):

        print()

        print("Chunk:", i)

        print("pages:",item["page"])

        print(item["chunk"][:300])

        print()

        print("="*50)
    # Save ALL chunks

    for i,item in enumerate(all_chunks):

        chunk = item["chunk"]

        page = item["page"]

        topic = await detect_topic(chunk)

        keywords = extract_keywords(chunk)
        embedding=create_embedding(chunk)
        c = DocumentChunk(

            document_id=doc.id,

            chunk_number=i,

            topic=topic,

            keywords=",".join(keywords),

            source=file.filename,

            page_number=page,

            token_count=len(chunk.split()),

            chunk_text=chunk,

            embedding=embedding

        )

        print(len(embedding))
        print(embedding[:10])

        db.add(c)
        db.flush()
        # db.refresh(c)
        add_vector(embedding ,c.id)

    # Commit once

    db.commit()

    db.close()
    
    return {

        "filename": file.filename,

        "saved": True,

        "characters": len(text),

        "chunks": len(all_chunks)

    }