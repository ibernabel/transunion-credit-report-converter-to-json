from fastapi import APIRouter, UploadFile, File, HTTPException
from src.parser.engine import ParserEngine
from src.scrubber.service import PIIScrubber
from src.models.report import CreditReport

router = APIRouter(prefix="/v1")

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/parse", response_model=CreditReport)
async def parse_credit_report(file: UploadFile = File(...)):
    """
    Upload a Transunion PDF Credit Report and get structured JSON back.
    PII is automatically scrubbed by default.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        content = await file.read()
        parser = await ParserEngine.from_pdf_bytes(content)
        report = await parser.get_report()
        
        # Scrub PII before returning
        scrubbed_report = PIIScrubber.scrub_report(report)
        
        # Explicitly clear file content from memory
        del content
        
        return scrubbed_report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
