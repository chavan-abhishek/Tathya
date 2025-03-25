# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from models import process_content  # Import from models.py

app = FastAPI(title="Misinformation Detector API")

# Define a Pydantic model for the request body
class AnalyzeRequest(BaseModel):
    content: str

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    # Call the NLP processing function from models.py
    result = process_content(request.content)
    return result