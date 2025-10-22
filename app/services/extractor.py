"""
Document extraction service using Moondream AI
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import base64

from app.core.config import settings
from app.utils.prompts import get_extraction_prompt
from app.services.validator import validate_extracted_data

try:
    import moondream as md
    from PIL import Image
    import requests
    MOONDREAM_AVAILABLE = True
    
    # Monkey-patch the moondream SDK to fix the bug with Moondream Station
    def patched_query(self, image, question):
        """Patched query method that handles Moondream Station response format"""
        # Prepare the request
        if hasattr(self, '_encode_image'):
            encoded_image = self._encode_image(image)
        else:
            # Fallback encoding
            from io import BytesIO
            import base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            encoded_image = base64.b64encode(buffered.getvalue()).decode()
        
        # Make the API request with data URL format
        image_data_url = f"data:image/jpeg;base64,{encoded_image}"
        payload = {
            "image_url": image_data_url,
            "question": question
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/query",
                json=payload,
                timeout=60
            )
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, dict):
                # Try to extract the answer from various possible keys
                if "answer" in result:
                    return {"answer": result["answer"]}
                elif "response" in result:
                    return {"answer": result["response"]}
                elif "text" in result:
                    return {"answer": result["text"]}
                elif "content" in result:
                    return {"answer": result["content"]}
                else:
                    # If it's a dict but no known key, return as-is
                    return result
            elif isinstance(result, str):
                return {"answer": result}
            else:
                return {"answer": str(result)}
        except Exception as e:
            raise Exception(f"Error calling Moondream API: {str(e)}")
    
    # Apply the monkey patch
    if hasattr(md, 'cloud_vl') and hasattr(md.cloud_vl, 'CloudVL'):
        md.cloud_vl.CloudVL.query = patched_query
    
except ImportError:
    MOONDREAM_AVAILABLE = False
    print("Warning: moondream package not installed. Install with: pip install moondream")


class DocumentExtractor:
    """Service for extracting information from documents using Moondream AI"""
    
    def __init__(self):
        self.endpoint = settings.MOONDREAM_ENDPOINT
        self.model_name = settings.MOONDREAM_MODEL
        self.timeout = settings.MOONDREAM_TIMEOUT
        self.model = None
        
        # Initialize Moondream model
        if MOONDREAM_AVAILABLE:
            try:
                self.model = md.vl(endpoint=self.endpoint)
            except Exception as e:
                print(f"Warning: Could not initialize Moondream model: {e}")
    
    async def check_connection(self) -> bool:
        """
        Check if Moondream service is available
        
        Returns:
            True if service is available, False otherwise
        """
        if not MOONDREAM_AVAILABLE or self.model is None:
            return False
        
        try:
            # Try a simple query to check connection
            # Create a small test image
            test_image = Image.new('RGB', (100, 100), color='white')
            result = self.model.query(test_image, "test")
            return True
        except:
            return False
    
    async def extract_from_image(
        self,
        image_path: str,
        document_type: str,
        original_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract information from document image
        
        Args:
            image_path: Path to the image file
            document_type: Type of document ("pan" or "aadhaar")
            original_filename: Original filename for metadata
        
        Returns:
            Dictionary containing extraction results
        """
        start_time = time.time()
        
        try:
            # Get the appropriate prompt
            prompt = get_extraction_prompt(document_type)
            
            if not prompt:
                raise ValueError(f"Unknown document type: {document_type}")
            
            # Read image file
            image_path_obj = Path(image_path)
            if not image_path_obj.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            file_size = image_path_obj.stat().st_size
            
            # Call Moondream API
            extracted_data = await self._call_moondream_api(image_path, prompt)
            
            # Validate and clean extracted data
            if settings.VALIDATE_PAN_FORMAT or settings.VALIDATE_AADHAAR_FORMAT:
                extracted_data = validate_extracted_data(extracted_data, document_type)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Build response
            response = {
                "status": "success",
                "document_type": document_type,
                "data": extracted_data,
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "processing_time_ms": round(processing_time, 2),
                    "model_version": self.model_name if self.model_name else "moondream-station",
                    "original_filename": original_filename,
                    "file_size_bytes": file_size
                }
            }
            
            # Save extracted data if configured
            if settings.SAVE_EXTRACTED_DATA:
                await self._save_extraction_result(response, original_filename)
            
            return response
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "document_type": document_type,
                "data": None,
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "processing_time_ms": round(processing_time, 2),
                    "original_filename": original_filename
                },
                "error": str(e)
            }
    
    async def _call_moondream_api(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Call Moondream API for image analysis using the Python SDK
        
        Args:
            image_path: Path to image file
            prompt: Extraction prompt
        
        Returns:
            Extracted data dictionary
        """
        if not MOONDREAM_AVAILABLE:
            raise Exception(
                "Moondream package not installed. "
                "Install with: pip install moondream"
            )
        
        if self.model is None:
            raise Exception(
                "Moondream model not initialized. "
                "Please ensure Moondream Station is running at " + self.endpoint
            )
        
        result = None
        answer_text = None
        
        try:
            # Load image using PIL
            image = Image.open(image_path)
            
            # Query the model
            result = self.model.query(image, prompt)
            
            # Debug: Print the result structure (remove in production)
            print(f"DEBUG - Moondream result type: {type(result)}")
            print(f"DEBUG - Moondream result: {result}")
            
            # Extract the answer - handle different response formats
            if isinstance(result, dict):
                # Try different possible keys
                if "answer" in result:
                    answer_text = result["answer"]
                elif "response" in result:
                    answer_text = result["response"]
                elif "text" in result:
                    answer_text = result["text"]
                elif "content" in result:
                    answer_text = result["content"]
                else:
                    # If dict but no known key, convert to string
                    answer_text = str(result)
            elif isinstance(result, str):
                answer_text = result
            else:
                # For any other type, convert to string
                answer_text = str(result)
            
            if not answer_text:
                raise Exception("No response received from Moondream model")
            
            print(f"DEBUG - Extracted answer text: {answer_text[:200]}...")
            
            # Try to parse JSON from the response
            extracted_data = self._parse_json_response(answer_text)
            
            return extracted_data
            
        except FileNotFoundError:
            raise Exception(f"Image file not found: {image_path}")
        except KeyError as e:
            result_str = str(result) if result else "No result"
            raise Exception(f"Unexpected response format from Moondream: missing key {str(e)}. Response was: {result_str}")
        except json.JSONDecodeError as e:
            answer_preview = answer_text[:500] if answer_text else "No answer text"
            raise Exception(f"Failed to parse JSON from Moondream response. Response text: {answer_preview}...")
        except Exception as e:
            error_msg = str(e)
            # Check if it's a connection error
            if "connect" in error_msg.lower() or "connection" in error_msg.lower():
                raise Exception(
                    "Cannot connect to Moondream Station. "
                    "Please ensure it's running at " + self.endpoint + 
                    "\nStart it with: moondream-station"
                )
            # Re-raise with more context
            import traceback
            full_trace = traceback.format_exc()
            raise Exception(f"Error calling Moondream API: {error_msg}\n\nFull trace:\n{full_trace}")
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Moondream response
        
        Args:
            response_text: Raw response text
        
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                return json.loads(json_text)
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                return json.loads(json_text)
            elif "{" in response_text and "}" in response_text:
                # Try to extract JSON object
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                raise ValueError("Could not parse JSON from response")
    
    async def _save_extraction_result(
        self,
        result: Dict[str, Any],
        filename: Optional[str] = None
    ):
        """
        Save extraction result to output folder
        
        Args:
            result: Extraction result dictionary
            filename: Original filename
        """
        try:
            output_dir = Path(settings.OUTPUT_FOLDER)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(filename).stem if filename else "extraction"
            output_file = output_dir / f"{base_name}_{timestamp}.json"
            
            # Save as JSON
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            # Log error but don't fail the extraction
            print(f"Error saving extraction result: {e}")


# Create global extractor instance
extractor = DocumentExtractor()

