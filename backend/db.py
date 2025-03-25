# backend/db.py
import asyncio
from fastapi import FastAPI, UploadFile, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import select
import os
import aiofiles

# Import process_content from models.py (not analyze_content)
from backend.models import process_content

DB_URL = "postgresql+asyncpg://PathRef_owner:npg_xlqJ0nr1NUiQ@ep-super-pine-a5dd48l3-pooler.us-east-2.aws.neon.tech/PathRef"

engine = create_async_engine(DB_URL, echo=True, connect_args={"ssl": "require"})
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

app = FastAPI()

class Document(Base):
    __tablename__ = "documents"  # Fixed typo: _tablename_ -> __tablename__
    id = Column(Integer, primary_key=True, index=True)
    path_reference = Column(String, unique=True, nullable=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session

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

@app.get("/query/")
async def query_pdf(query: str = Body(...), db: AsyncSession = Depends(get_db)):
    # Get the latest uploaded document from the database
    result = await db.execute(select(Document.path_reference).order_by(Document.id.desc()).limit(1))
    file_path = result.scalar()

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Reference file not found")

    # Use process_content from models.py with the file path
    response = process_content(query, file_path, source="unknown")

    return {"response": response}

async def main():
    await init_db()

if __name__ == "__main__":  # Fixed typo: _name_ -> __name__
    asyncio.run(main())