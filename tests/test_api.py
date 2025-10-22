"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io
from PIL import Image

from main import app

client = TestClient(app)


def create_test_image() -> bytes:
    """Create a test image in memory"""
    img = Image.new('RGB', (800, 600), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "moondream_connected" in data
    
    def test_api_v1_health_endpoint(self):
        """Test API v1 health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


class TestExtractionEndpoints:
    """Test extraction endpoints"""
    
    def test_pan_extraction_no_file(self):
        """Test PAN extraction without file"""
        response = client.post("/api/v1/extract/pan")
        assert response.status_code == 422  # Validation error
    
    def test_pan_extraction_with_file(self):
        """Test PAN extraction with file"""
        test_image = create_test_image()
        files = {"file": ("test_pan.jpg", test_image, "image/jpeg")}
        
        response = client.post("/api/v1/extract/pan", files=files)
        
        # Response should be 200 or 500 depending on Moondream availability
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "document_type" in data
            assert data["document_type"] == "pan"
    
    def test_aadhaar_extraction_no_file(self):
        """Test Aadhaar extraction without file"""
        response = client.post("/api/v1/extract/aadhaar")
        assert response.status_code == 422  # Validation error
    
    def test_aadhaar_extraction_with_file(self):
        """Test Aadhaar extraction with file"""
        test_image = create_test_image()
        files = {"file": ("test_aadhaar.jpg", test_image, "image/jpeg")}
        
        response = client.post("/api/v1/extract/aadhaar", files=files)
        
        # Response should be 200 or 500 depending on Moondream availability
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "document_type" in data
            assert data["document_type"] == "aadhaar"
    
    def test_generic_extraction_with_file(self):
        """Test generic extraction endpoint"""
        test_image = create_test_image()
        files = {"file": ("test_doc.jpg", test_image, "image/jpeg")}
        data = {"document_type": "pan"}
        
        response = client.post("/api/v1/extract", files=files, data=data)
        
        # Response should be 200 or 500 depending on Moondream availability
        assert response.status_code in [200, 500]
    
    def test_invalid_file_type(self):
        """Test with invalid file type"""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        
        response = client.post("/api/v1/extract/pan", files=files)
        assert response.status_code == 400


class TestBatchEndpoints:
    """Test batch processing endpoints"""
    
    def test_batch_extraction_no_files(self):
        """Test batch extraction without files"""
        data = {"document_type": "pan"}
        response = client.post("/api/v1/batch/extract", data=data)
        assert response.status_code == 422  # Validation error
    
    def test_batch_extraction_with_files(self):
        """Test batch extraction with multiple files"""
        test_image1 = create_test_image()
        test_image2 = create_test_image()
        
        files = [
            ("files", ("test1.jpg", test_image1, "image/jpeg")),
            ("files", ("test2.jpg", test_image2, "image/jpeg"))
        ]
        data = {"document_type": "pan"}
        
        response = client.post("/api/v1/batch/extract", files=files, data=data)
        
        # Response should be 200 or 500 depending on Moondream availability
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "total_documents" in data
            assert "successful" in data
            assert "failed" in data
            assert "results" in data
    
    def test_async_batch_extraction_with_files(self):
        """Test async batch extraction with multiple files"""
        test_image1 = create_test_image()
        test_image2 = create_test_image()
        
        files = [
            ("files", ("test1.jpg", test_image1, "image/jpeg")),
            ("files", ("test2.jpg", test_image2, "image/jpeg"))
        ]
        data = {"document_type": "aadhaar"}
        
        response = client.post("/api/v1/batch/extract/async", files=files, data=data)
        
        # Response should be 200 or 500 depending on Moondream availability
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "total_documents" in data
            assert "results" in data
    
    def test_batch_extraction_too_many_files(self):
        """Test batch extraction with too many files"""
        # Create 51 files (exceeds limit of 50)
        files = []
        for i in range(51):
            test_image = create_test_image()
            files.append(("files", (f"test{i}.jpg", test_image, "image/jpeg")))
        
        data = {"document_type": "pan"}
        response = client.post("/api/v1/batch/extract", files=files, data=data)
        assert response.status_code == 400


class TestValidation:
    """Test validation functions"""
    
    def test_pan_format_validation(self):
        """Test PAN format validation"""
        from app.services.validator import validate_pan_format
        
        # Valid PAN
        is_valid, msg = validate_pan_format("ABCDE1234F")
        assert is_valid is True
        
        # Invalid PAN - too short
        is_valid, msg = validate_pan_format("ABC123")
        assert is_valid is False
        
        # Invalid PAN - wrong format
        is_valid, msg = validate_pan_format("1234567890")
        assert is_valid is False
        
        # Empty PAN
        is_valid, msg = validate_pan_format("")
        assert is_valid is False
    
    def test_aadhaar_format_validation(self):
        """Test Aadhaar format validation"""
        from app.services.validator import validate_aadhaar_format
        
        # Valid Aadhaar
        is_valid, msg = validate_aadhaar_format("1234 5678 9012")
        assert is_valid is True
        
        # Valid Aadhaar without spaces
        is_valid, msg = validate_aadhaar_format("123456789012")
        assert is_valid is True
        
        # Invalid Aadhaar - too short
        is_valid, msg = validate_aadhaar_format("12345")
        assert is_valid is False
        
        # Empty Aadhaar
        is_valid, msg = validate_aadhaar_format("")
        assert is_valid is False
        
        # Masked Aadhaar
        is_valid, msg = validate_aadhaar_format("XXXX 5678 9012")
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

