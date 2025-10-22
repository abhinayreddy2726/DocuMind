"""
Batch processing endpoints
"""
import asyncio
from typing import List, Literal
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from datetime import datetime
import time

from app.core.config import settings
from app.models.response import BatchExtractionResponse, ExtractionResponse
from app.services.extractor import extractor
from app.api.endpoints.extract import save_upload_file, cleanup_file

router = APIRouter()


@router.post("/extract", response_model=BatchExtractionResponse)
async def batch_extract(
    files: List[UploadFile] = File(..., description="Multiple document images"),
    document_type: Literal["pan", "aadhaar"] = Form(..., description="Type of documents")
):
    """
    Process multiple documents in batch
    
    - **files**: List of document images (JPG, JPEG, PNG, PDF)
    - **document_type**: Type of documents ("pan" or "aadhaar")
    
    Returns batch processing results with individual extraction results
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 50:
        raise HTTPException(
            status_code=400,
            detail="Too many files. Maximum 50 files per batch"
        )
    
    start_time = time.time()
    results = []
    file_paths = []
    
    try:
        # Save all uploaded files
        for file in files:
            try:
                file_path = await save_upload_file(file)
                file_paths.append((file_path, file.filename))
            except Exception as e:
                results.append({
                    "status": "error",
                    "document_type": document_type,
                    "data": None,
                    "metadata": {
                        "processed_at": datetime.now().isoformat(),
                        "original_filename": file.filename
                    },
                    "error": f"Error saving file: {str(e)}"
                })
        
        # Process all files
        for file_path, filename in file_paths:
            try:
                result = await extractor.extract_from_image(
                    file_path,
                    document_type=document_type,
                    original_filename=filename
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "status": "error",
                    "document_type": document_type,
                    "data": None,
                    "metadata": {
                        "processed_at": datetime.now().isoformat(),
                        "original_filename": filename
                    },
                    "error": str(e)
                })
        
        # Calculate statistics
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        processing_time = (time.time() - start_time) * 1000
        
        # Determine overall status
        if successful == len(results):
            overall_status = "success"
        elif successful > 0:
            overall_status = "partial"
        else:
            overall_status = "error"
        
        return BatchExtractionResponse(
            status=overall_status,
            total_documents=len(results),
            successful=successful,
            failed=failed,
            results=results,
            processing_time_ms=round(processing_time, 2)
        )
    
    finally:
        # Cleanup uploaded files
        for file_path, _ in file_paths:
            cleanup_file(file_path)


@router.post("/extract/async", response_model=BatchExtractionResponse)
async def batch_extract_async(
    files: List[UploadFile] = File(..., description="Multiple document images"),
    document_type: Literal["pan", "aadhaar"] = Form(..., description="Type of documents")
):
    """
    Process multiple documents asynchronously in parallel
    
    - **files**: List of document images (JPG, JPEG, PNG, PDF)
    - **document_type**: Type of documents ("pan" or "aadhaar")
    
    Returns batch processing results with individual extraction results.
    This endpoint processes documents in parallel for faster processing.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 50:
        raise HTTPException(
            status_code=400,
            detail="Too many files. Maximum 50 files per batch"
        )
    
    start_time = time.time()
    file_paths = []
    
    try:
        # Save all uploaded files
        save_tasks = []
        for file in files:
            save_tasks.append(save_upload_file(file))
        
        # Save files concurrently
        saved_paths = []
        for i, task in enumerate(asyncio.as_completed(save_tasks)):
            try:
                file_path = await task
                saved_paths.append((file_path, files[i].filename))
                file_paths.append((file_path, files[i].filename))
            except Exception as e:
                saved_paths.append((None, files[i].filename, str(e)))
        
        # Process all files concurrently
        extraction_tasks = []
        for file_path, filename in file_paths:
            extraction_tasks.append(
                extractor.extract_from_image(
                    file_path,
                    document_type=document_type,
                    original_filename=filename
                )
            )
        
        # Wait for all extractions to complete
        results = []
        for i, task in enumerate(asyncio.as_completed(extraction_tasks)):
            try:
                result = await task
                results.append(result)
            except Exception as e:
                results.append({
                    "status": "error",
                    "document_type": document_type,
                    "data": None,
                    "metadata": {
                        "processed_at": datetime.now().isoformat(),
                        "original_filename": file_paths[i][1] if i < len(file_paths) else "unknown"
                    },
                    "error": str(e)
                })
        
        # Add errors from file saving
        for item in saved_paths:
            if len(item) == 3:  # Error case
                _, filename, error = item
                results.append({
                    "status": "error",
                    "document_type": document_type,
                    "data": None,
                    "metadata": {
                        "processed_at": datetime.now().isoformat(),
                        "original_filename": filename
                    },
                    "error": error
                })
        
        # Calculate statistics
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        processing_time = (time.time() - start_time) * 1000
        
        # Determine overall status
        if successful == len(results):
            overall_status = "success"
        elif successful > 0:
            overall_status = "partial"
        else:
            overall_status = "error"
        
        return BatchExtractionResponse(
            status=overall_status,
            total_documents=len(results),
            successful=successful,
            failed=failed,
            results=results,
            processing_time_ms=round(processing_time, 2)
        )
    
    finally:
        # Cleanup uploaded files
        for file_path, _ in file_paths:
            cleanup_file(file_path)

