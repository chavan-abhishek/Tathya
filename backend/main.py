# backend/main.py
import asyncio
from fastapi import FastAPI, UploadFile, Depends, Body, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import select
import os
import aiofiles
from backend.models import process_content

DB_URL = "postgresql+asyncpg://PathRef_owner:npg_xlqJ0nr1NUiQ@ep-super-pine-a5dd48l3-pooler.us-east-2.aws.neon.tech/PathRef"

engine = create_async_engine(DB_URL, echo=True, connect_args={"ssl": "require"})
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

app = FastAPI(title="Misinformation Detector API")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    path_reference = Column(String, unique=True, nullable=False)

class AnalyzeRequest(BaseModel):
    content: str
    reference_file_path: str
    source: str = "unknown"

class QueryRequest(BaseModel):
    query: str

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/upload/")
async def upload_file_db(file: UploadFile, db: AsyncSession = Depends(get_db)):
    upload_dir = "Uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    file_content = await file.read()
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(file_content)

    new_doc = Document(path_reference=file_path)
    db.add(new_doc)
    await db.commit()

    return {"message": "File uploaded successfully", "file_path": file_path}

@app.post("/query/")  # Changed to POST
async def query_pdf(request: QueryRequest = Body(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document.path_reference).order_by(Document.id.desc()).limit(1))
    file_path = result.scalar()

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Reference file not found")

    response = process_content(request.query, file_path, source="unknown")
    return {"response": response}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        result = process_content(request.content, request.reference_file_path, request.source)
        return result
    except Exception as e:
        return {"error": str(e)}