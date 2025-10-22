"""
Validation service for PAN and Aadhaar numbers
"""
import re
from typing import Tuple


def validate_pan_format(pan_number: str) -> Tuple[bool, str]:
    """
    Validate PAN number format
    
    PAN Format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
    
    Args:
        pan_number: PAN number to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not pan_number:
        return False, "PAN number is empty"
    
    # Remove spaces and convert to uppercase
    pan_number = pan_number.strip().upper()
    
    # PAN pattern: 5 letters, 4 digits, 1 letter
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    if not re.match(pan_pattern, pan_number):
        return False, "Invalid PAN format. Expected format: ABCDE1234F (5 letters, 4 digits, 1 letter)"
    
    return True, "Valid PAN format"


def validate_aadhaar_format(aadhaar_number: str) -> Tuple[bool, str]:
    """
    Validate Aadhaar number format
    
    Aadhaar Format: 12 digits (may be formatted as XXXX XXXX XXXX)
    
    Args:
        aadhaar_number: Aadhaar number to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not aadhaar_number:
        return False, "Aadhaar number is empty"
    
    # Remove spaces and any non-digit characters except X (for masked digits)
    cleaned = aadhaar_number.strip().replace(" ", "").replace("-", "")
    
    # Check if it contains only digits or X (for masked Aadhaar)
    if not re.match(r'^[0-9X]{12}$', cleaned):
        return False, "Invalid Aadhaar format. Expected 12 digits (may contain X for masked digits)"
    
    # If it's all X's, it's likely completely masked
    if cleaned == "X" * 12:
        return False, "Aadhaar number is completely masked"
    
    return True, "Valid Aadhaar format"


def clean_pan_number(pan_number: str) -> str:
    """
    Clean and format PAN number
    
    Args:
        pan_number: Raw PAN number
    
    Returns:
        Cleaned PAN number in uppercase
    """
    if not pan_number:
        return ""
    
    return pan_number.strip().upper().replace(" ", "")


def clean_aadhaar_number(aadhaar_number: str) -> str:
    """
    Clean and format Aadhaar number
    
    Args:
        aadhaar_number: Raw Aadhaar number
    
    Returns:
        Cleaned Aadhaar number in XXXX XXXX XXXX format
    """
    if not aadhaar_number:
        return ""
    
    # Remove all spaces and hyphens
    cleaned = aadhaar_number.strip().replace(" ", "").replace("-", "")
    
    # Format as XXXX XXXX XXXX
    if len(cleaned) == 12:
        return f"{cleaned[0:4]} {cleaned[4:8]} {cleaned[8:12]}"
    
    return cleaned


def validate_extracted_data(data: dict, document_type: str) -> dict:
    """
    Validate and clean extracted data
    
    Args:
        data: Extracted data dictionary
        document_type: Type of document ("pan" or "aadhaar")
    
    Returns:
        Validated and cleaned data dictionary
    """
    validated_data = data.copy()
    
    if document_type == "pan":
        # Validate and clean PAN number
        if "pan_number" in validated_data and validated_data["pan_number"]:
            pan = clean_pan_number(validated_data["pan_number"])
            is_valid, message = validate_pan_format(pan)
            validated_data["pan_number"] = pan
            validated_data["pan_valid"] = is_valid
        else:
            validated_data["pan_valid"] = False
    
    elif document_type == "aadhaar":
        # Validate and clean Aadhaar number
        if "aadhaar_number" in validated_data and validated_data["aadhaar_number"]:
            aadhaar = clean_aadhaar_number(validated_data["aadhaar_number"])
            is_valid, message = validate_aadhaar_format(aadhaar)
            validated_data["aadhaar_number"] = aadhaar
            validated_data["aadhaar_valid"] = is_valid
        else:
            validated_data["aadhaar_valid"] = False
    
    return validated_data

