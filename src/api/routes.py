from fastapi import APIRouter, UploadFile, File, HTTPException
from src.parser.engine import ParserEngine
from src.scrubber.service import PIIScrubber
from src.models.report import CreditReport
from src.utils.logging_config import api_logger
import os

router = APIRouter(prefix="/v1")

# File upload configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024  # Default 10MB

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/parse", response_model=CreditReport)
async def parse_credit_report(file: UploadFile = File(...)):
    """
    Upload a Transunion PDF Credit Report and get structured JSON back.
    PII is automatically scrubbed by default.
    
    Security validations:
    - File extension validation
    - File size limit enforcement
    - Sanitized error messages
    """
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported."
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
            api_logger.warning(
                f"File size exceeded limit",
                extra={
                    "uploaded_file": file.filename,
                    "size_bytes": len(content),
                    "max_size_bytes": MAX_FILE_SIZE
                }
            )
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {max_size_mb:.0f}MB"
            )
        
        # Validate file is not empty
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file provided"
            )
        
        # Parse PDF
        parser = await ParserEngine.from_pdf_bytes(content)
        report = await parser.get_report()
        
        # Scrub PII before returning
        scrubbed_report = PIIScrubber.scrub_report(report)
        
        # Explicitly clear file content from memory
        del content
        
        api_logger.info(
            "PDF parsed successfully",
            extra={"uploaded_file": file.filename}
        )
        
        return scrubbed_report
        
    except HTTPException:
        # Re-raise HTTP exceptions (already sanitized)
        raise
        
    except ValueError as e:
        # Handle parsing/validation errors
        api_logger.warning(
            f"Invalid PDF format",
            extra={"uploaded_file": file.filename, "error": str(e)}
        )
        raise HTTPException(
            status_code=400, 
            detail="Invalid PDF format or unsupported credit report structure"
        )
        
    except Exception as e:
        # Handle unexpected errors - don't expose internal details
        api_logger.error(
            f"PDF processing error",
            extra={"uploaded_file": file.filename, "error_type": type(e).__name__},
            exc_info=True
        )
        raise HTTPException(
            status_code=500, 
            detail="Internal server error processing PDF. Please try again or contact support."
        )

