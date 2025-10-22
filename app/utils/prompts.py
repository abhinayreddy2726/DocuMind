"""
AI prompts for document extraction
"""

PAN_EXTRACTION_PROMPT = """
Analyze this PAN card image carefully and extract the following information:

1. PAN Number: A 10-character alphanumeric code (Format: 5 letters, 4 digits, 1 letter. Example: ABCDE1234F)
2. Name: The full name of the cardholder as printed on the card
3. Father's Name: The father's name as printed on the card
4. Date of Birth: The date of birth in DD/MM/YYYY format
5. Signature: Check if a signature is present on the card (answer "Yes" or "No")

Please extract the exact text as it appears on the card. If any field is not clearly visible or not present, return "Not Found" for that field.

Return the information in the following JSON format:
{
    "pan_number": "XXXXX0000X",
    "name": "Full Name",
    "fathers_name": "Father's Full Name",
    "date_of_birth": "DD/MM/YYYY",
    "signature_present": "Yes/No"
}

Important:
- Extract exact text without modifications
- Maintain proper capitalization as shown on the card
- For PAN number, ensure all characters are captured correctly
- Date should be in DD/MM/YYYY format
"""

AADHAAR_EXTRACTION_PROMPT = """
Analyze this Aadhaar card image carefully and extract the following information:

1. Aadhaar Number: A 12-digit number (may be formatted as XXXX XXXX XXXX or with some digits masked)
2. Name: The full name of the cardholder as printed on the card
3. Date of Birth / Year of Birth: The date of birth (DD/MM/YYYY) or year of birth (YYYY)
4. Gender: The gender (Male/Female/Other)
5. Address: The complete address including street, city, state, and PIN code
6. QR Code: Check if a QR code is present on the card (answer "Yes" or "No")

Please extract the exact text as it appears on the card. If any field is not clearly visible or not present, return "Not Found" for that field.

Return the information in the following JSON format:
{
    "aadhaar_number": "XXXX XXXX XXXX",
    "name": "Full Name",
    "date_of_birth": "DD/MM/YYYY or YYYY",
    "gender": "Male/Female/Other",
    "address": "Complete address with PIN code",
    "qr_code_present": "Yes/No"
}

Important:
- Extract exact text without modifications
- Maintain proper capitalization as shown on the card
- For Aadhaar number, preserve the spacing format (XXXX XXXX XXXX)
- Include complete address with all details
- Some Aadhaar cards may have masked digits (XXXX) in the number
"""


def get_extraction_prompt(document_type: str) -> str:
    """
    Get the appropriate extraction prompt based on document type
    
    Args:
        document_type: Type of document ("pan" or "aadhaar")
    
    Returns:
        Extraction prompt string
    """
    prompts = {
        "pan": PAN_EXTRACTION_PROMPT,
        "aadhaar": AADHAAR_EXTRACTION_PROMPT
    }
    
    return prompts.get(document_type.lower(), "")

