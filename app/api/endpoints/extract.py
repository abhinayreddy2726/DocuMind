"""
Document extraction endpoints
"""
import os
import uuid
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.models.response import ExtractionResponse, ErrorResponse
from app.services.extractor import extractor

router = APIRouter()


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    allowed_extensions = settings.get_allowed_extensions()
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file to temporary location
    
    Args:
        upload_file: FastAPI UploadFile object
    
    Returns:
        Path to saved file
    """
    # Validate file
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not allowed_file(upload_file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.get_allowed_extensions()}"
        )
    
    # Generate unique filename
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = Path(settings.UPLOAD_FOLDER) / unique_filename
    
    # Save file
    try:
        contents = await upload_file.read()
        
        # Check file size
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return str(file_path)
    
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


def cleanup_file(file_path: str):
    """Delete uploaded file if configured"""
    if settings.DELETE_UPLOADED_FILES:
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


@router.post("/pan", response_model=ExtractionResponse)
async def extract_pan(
    file: UploadFile = File(..., description="PAN card image file")
):
    """
    Extract details from PAN card
    
    - **file**: PAN card image (JPG, JPEG, PNG, PDF)
    
    Returns extracted PAN card details including:
    - PAN Number
    - Name
    - Father's Name
    - Date of Birth
    - Signature Present
    """
    file_path = None
    
    try:
        # Save uploaded file
        file_path = await save_upload_file(file)
        
        # Extract information
        result = await extractor.extract_from_image(
            file_path,
            document_type="pan",
            original_filename=file.filename
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file_path:
            cleanup_file(file_path)


@router.post("/aadhaar", response_model=ExtractionResponse)
async def extract_aadhaar(
    file: UploadFile = File(..., description="Aadhaar card image file")
):
    """
    Extract details from Aadhaar card
    
    - **file**: Aadhaar card image (JPG, JPEG, PNG, PDF)
    
    Returns extracted Aadhaar card details including:
    - Aadhaar Number
    - Name
    - Date of Birth
    - Gender
    - Address
    - QR Code Present
    """
    file_path = None
    
    try:
        # Save uploaded file
        file_path = await save_upload_file(file)
        
        # Extract information
        result = await extractor.extract_from_image(
            file_path,
            document_type="aadhaar",
            original_filename=file.filename
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file_path:
            cleanup_file(file_path)


@router.post("/", response_model=ExtractionResponse)
async def extract_document(
    file: UploadFile = File(..., description="Document image file"),
    document_type: Literal["pan", "aadhaar"] = Form(..., description="Type of document")
):
    """
    Generic document extraction endpoint
    
    - **file**: Document image (JPG, JPEG, PNG, PDF)
    - **document_type**: Type of document ("pan" or "aadhaar")
    
    Returns extracted document details based on document type
    """
    file_path = None
    
    try:
        # Save uploaded file
        file_path = await save_upload_file(file)
        
        # Extract information
        result = await extractor.extract_from_image(
            file_path,
            document_type=document_type,
            original_filename=file.filename
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file_path:
            cleanup_file(file_path)

