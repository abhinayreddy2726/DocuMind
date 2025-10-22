"""
Response models for API endpoints
"""
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class PANData(BaseModel):
    """PAN card extracted data"""
    pan_number: Optional[str] = Field(None, description="PAN number (10 characters)")
    name: Optional[str] = Field(None, description="Full name on PAN card")
    fathers_name: Optional[str] = Field(None, description="Father's name")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (DD/MM/YYYY)")
    signature_present: Optional[str] = Field(None, description="Signature present (Yes/No)")
    pan_valid: Optional[bool] = Field(None, description="PAN format validation result")


class AadhaarData(BaseModel):
    """Aadhaar card extracted data"""
    aadhaar_number: Optional[str] = Field(None, description="Aadhaar number (12 digits)")
    name: Optional[str] = Field(None, description="Full name on Aadhaar card")
    date_of_birth: Optional[str] = Field(None, description="Date of birth or Year of birth")
    gender: Optional[str] = Field(None, description="Gender (Male/Female/Other)")
    address: Optional[str] = Field(None, description="Full address with PIN code")
    qr_code_present: Optional[str] = Field(None, description="QR code present (Yes/No)")
    aadhaar_valid: Optional[bool] = Field(None, description="Aadhaar format validation result")


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process"""
    model_config = {"protected_namespaces": ()}
    
    processed_at: datetime = Field(default_factory=datetime.now)
    processing_time_ms: Optional[float] = None
    model_version: str = Field(default="moondream2")
    original_filename: Optional[str] = None
    file_size_bytes: Optional[int] = None


class ExtractionResponse(BaseModel):
    """Standard extraction response"""
    status: Literal["success", "error"] = Field(..., description="Response status")
    document_type: Literal["pan", "aadhaar"] = Field(..., description="Document type")
    data: Optional[Dict[str, Any]] = Field(None, description="Extracted data")
    metadata: Optional[ExtractionMetadata] = Field(None, description="Processing metadata")
    error: Optional[str] = Field(None, description="Error message if status is error")


class BatchExtractionResponse(BaseModel):
    """Batch extraction response"""
    status: Literal["success", "partial", "error"] = Field(..., description="Overall status")
    total_documents: int = Field(..., description="Total documents processed")
    successful: int = Field(..., description="Successfully processed documents")
    failed: int = Field(..., description="Failed documents")
    results: List[ExtractionResponse] = Field(..., description="Individual extraction results")
    processing_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="API version")
    moondream_connected: bool = Field(..., description="Moondream service connection status")


class ErrorResponse(BaseModel):
    """Error response"""
    status: Literal["error"] = "error"
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)

