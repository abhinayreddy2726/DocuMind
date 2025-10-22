"""
Request models for API endpoints
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """Generic extraction request"""
    document_type: Literal["pan", "aadhaar"] = Field(
        ...,
        description="Type of document to extract"
    )


class BatchExtractionRequest(BaseModel):
    """Batch extraction request"""
    document_type: Literal["pan", "aadhaar"] = Field(
        ...,
        description="Type of documents to extract"
    )
    async_processing: bool = Field(
        default=False,
        description="Process documents asynchronously"
    )

