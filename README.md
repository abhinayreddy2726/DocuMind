# PAN & Aadhaar Card Details Extractor using Moondream AI

A production-ready FastAPI application that extracts details from PAN (Permanent Account Number) and Aadhaar cards using Moondream AI's vision language model. Built for Windows deployment with local processing for privacy and security.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)


## ✨ Features

### Core Functionality
- ✅ **PAN Card Extraction**: Number, Name, Father's Name, DOB, Signature
- ✅ **Aadhaar Card Extraction**: Number, Name, DOB, Gender, Address, QR Code
- ✅ **Automatic Validation**: Format validation for PAN and Aadhaar numbers
- ✅ **Batch Processing**: Process multiple documents simultaneously
- ✅ **Async Support**: High-performance async processing

### API Features
- ✅ **RESTful API**: Clean, well-documented endpoints
- ✅ **Interactive Docs**: Swagger UI and ReDoc
- ✅ **CORS Enabled**: Ready for frontend integration
- ✅ **Health Checks**: Monitor service status
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **File Validation**: Size and type checking

### Technical Features
- ✅ **Local Processing**: Privacy-first, no external API calls
- ✅ **Pydantic Models**: Type-safe data validation
- ✅ **Structured Logging**: Track all operations
- ✅ **Docker Support**: Easy containerized deployment
- ✅ **Test Suite**: Comprehensive test coverage
- ✅ **Type Hints**: Full type annotation

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **RAM**: 4GB minimum (8GB recommended)
- **OS**: Windows 10/11, Linux, or macOS

## 🚀 Quick Start

### Option 1: Automated Setup (Windows)

1. **Clone or download the project**
2. **Double-click `start.bat`**
3. **Open another terminal and start Moondream Station:**
   ```cmd
   moondream-station
   ```
4. **Access the API at:** http://localhost:8000/docs

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
pip install moondream-station
```

#### Step 3: Configure Environment
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file as needed (optional - defaults work fine).

#### Step 4: Start Moondream Station
```bash
# In a new terminal
moondream-station
```

This starts the local AI inference server at `http://localhost:2020/v1`

#### Step 5: Start the API
```bash
# In your main terminal
python main.py
```

The API will be available at: http://localhost:8000

## ⚠️ Important: Moondream SDK Fix Included

This project includes a **built-in fix** for a critical bug in the Moondream Python SDK (v0.1.1):

### The Problem
The official Moondream Python SDK has a bug that causes `KeyError: 'answer'` when connecting to Moondream Station. This happens because:
- The SDK expects a response with an `"answer"` key
- Moondream Station returns data in a different format
- The SDK crashes before you can process any documents

### The Solution ✅
This project automatically applies a monkey-patch that:
1. **Intercepts SDK calls** before they reach the buggy code
2. **Handles multiple response formats** (answer, response, text, content)
3. **Uses the correct API format** (image_url with base64 data URLs)
4. **Works transparently** - no code changes needed by you

### Technical Details
The fix is implemented in:
- `app/services/extractor.py` (lines 21-73)
- Patches the `CloudVL.query()` method at import time
- Fully backward compatible with future SDK fixes

**You don't need to do anything** - the fix is already integrated and working!

## 📚 Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Quick Start Guide**: [QUICKSTART.md](QUICKSTART.md)
- **Windows Installation**: [WINDOWS_INSTALLATION.md](WINDOWS_INSTALLATION.md)

## 🔌 API Endpoints

### Health & Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/api/v1/health` | API v1 health check |

### Document Extraction
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/extract/pan` | Extract PAN card details |
| POST | `/api/v1/extract/aadhaar` | Extract Aadhaar card details |
| POST | `/api/v1/extract` | Generic extraction (specify type) |

### Batch Processing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/batch/extract` | Batch process documents |
| POST | `/api/v1/batch/extract/async` | Async batch processing |

## 💡 Usage Examples

### Python Requests
```python
import requests

# Extract PAN card
url = "http://localhost:8000/api/v1/extract/pan"
files = {"file": open("pan_card.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())

# Extract Aadhaar card
url = "http://localhost:8000/api/v1/extract/aadhaar"
files = {"file": open("aadhaar_card.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())

# Batch processing
files = [
    ("files", open("pan1.jpg", "rb")),
    ("files", open("pan2.jpg", "rb"))
]
data = {"document_type": "pan"}
response = requests.post(
    "http://localhost:8000/api/v1/batch/extract",
    files=files,
    data=data
)
print(response.json())
```

### JavaScript/Fetch
```javascript
// Extract PAN card
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/v1/extract/pan', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### cURL
```bash
# Extract PAN card
curl -X POST "http://localhost:8000/api/v1/extract/pan" \
  -F "file=@pan_card.jpg"

# Extract Aadhaar card
curl -X POST "http://localhost:8000/api/v1/extract/aadhaar" \
  -F "file=@aadhaar_card.jpg"

# Generic extraction
curl -X POST "http://localhost:8000/api/v1/extract" \
  -F "file=@document.jpg" \
  -F "document_type=pan"
```

## 📊 Response Format

### PAN Card Response
```json
{
  "status": "success",
  "document_type": "pan",
  "data": {
    "pan_number": "ABCDE1234F",
    "name": "John Doe",
    "fathers_name": "James Doe",
    "date_of_birth": "01/01/1990",
    "signature_present": "Yes",
    "pan_valid": true
  },
  "metadata": {
    "processed_at": "2025-01-15T10:30:00",
    "processing_time_ms": 1250,
    "model_version": "moondream2",
    "original_filename": "pan_card.jpg",
    "file_size_bytes": 245678
  }
}
```

### Aadhaar Card Response
```json
{
  "status": "success",
  "document_type": "aadhaar",
  "data": {
    "aadhaar_number": "1234 5678 9012",
    "name": "John Doe",
    "date_of_birth": "01/01/1990",
    "gender": "Male",
    "address": "123 Main St, City, State, 123456",
    "qr_code_present": "Yes",
    "aadhaar_valid": true
  },
  "metadata": {
    "processed_at": "2025-01-15T10:30:00",
    "processing_time_ms": 1580,
    "model_version": "moondream2",
    "original_filename": "aadhaar_card.jpg",
    "file_size_bytes": 312456
  }
}
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_api.py::TestHealthEndpoints -v
```

### Manual Testing
1. Open Swagger UI: http://localhost:8000/docs
2. Select an endpoint (e.g., `/api/v1/extract/pan`)
3. Click "Try it out"
4. Upload a test image
5. Click "Execute"
6. View the response

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Server Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Moondream Configuration
MOONDREAM_ENDPOINT=http://localhost:2020/v1
MOONDREAM_TIMEOUT=30

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=["jpg", "jpeg", "png", "pdf"]

# Processing Settings
SAVE_EXTRACTED_DATA=True
DELETE_UPLOADED_FILES=False
VALIDATE_PAN_FORMAT=True
VALIDATE_AADHAAR_FORMAT=True

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t pan-aadhaar-extractor .

# Run container
docker run -p 8000:8000 pan-aadhaar-extractor

# Or use Docker Compose
docker-compose up -d
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📁 Project Structure

```
DocuMind/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── health.py          # Health check endpoints
│   │       ├── extract.py         # Extraction endpoints
│   │       └── batch.py           # Batch processing
│   ├── core/
│   │   └── config.py              # Configuration settings
│   ├── models/
│   │   ├── request.py             # Request schemas
│   │   └── response.py            # Response schemas
│   ├── services/
│   │   ├── extractor.py           # Extraction service
│   │   └── validator.py           # Validation logic
│   └── utils/
│       └── prompts.py             # AI prompts
├── tests/
│   └── test_api.py                # API tests
├── uploads/                       # Temporary uploads
├── outputs/                       # Extraction results
├── logs/                          # Application logs
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose
└── start.bat                      # Windows startup script
```

## 🔒 Privacy & Security

- **Local Processing**: All AI inference happens locally via Moondream Station
- **No External Calls**: No data sent to external servers
- **Secure File Handling**: Files are validated and optionally deleted after processing
- **Format Validation**: PAN and Aadhaar numbers are validated for correct format
- **Configurable Storage**: Control whether to save extracted data

## 🛠️ Troubleshooting

### Common Issues

**1. KeyError: 'answer' - Moondream SDK Bug (FIXED)**

This project includes a **built-in fix** for a bug in the Moondream Python SDK (v0.1.1) that causes a `KeyError: 'answer'` when connecting to Moondream Station.

**What was the issue?**
- The Moondream Python SDK expected an `"answer"` key in the API response
- Moondream Station returns data in a different format
- This caused extraction to fail with `KeyError: 'answer'`

**How it's fixed:**
- ✅ Automatic monkey-patch applied in `app/services/extractor.py`
- ✅ Handles multiple response formats (`answer`, `response`, `text`, `content`)
- ✅ Uses correct API format (`image_url` with base64 data URLs)
- ✅ No manual intervention needed

**If you still see the error:**
```bash
# 1. Clear Python cache
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# 2. Restart the application
python main.py

# 3. Ensure Moondream Station is running
moondream-station
```

**2. Moondream Station not connecting**
```bash
# Check if Moondream Station is running
curl http://localhost:2020/v1/query

# Start Moondream Station in a new terminal
moondream-station

# Or start in background (Windows PowerShell)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "moondream-station"
```

**3. Port 8000 already in use**
```bash
# Use a different port
uvicorn main:app --port 8001
```

**4. Module import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
pip install moondream-station
```

**5. File upload errors**
- Check file size (max 10MB by default)
- Verify file type (jpg, jpeg, png, pdf)
- Ensure uploads folder exists and is writable

**6. Validation errors (model_version)**
- This is fixed in the latest version
- Ensure you're using the updated `app/services/extractor.py`
- The fix sets `model_version` to a string instead of the model object

## 📈 Performance

- **Average Processing Time**: 1-2 seconds per document
- **Batch Processing**: 10-20 documents in 15-30 seconds
- **Async Processing**: Up to 50% faster for large batches
- **Memory Usage**: ~500MB-1GB depending on model



## 🔄 Future Enhancements

- [ ] Support for more document types (Driving License, Voter ID, Passport)
- [ ] Multi-language support
- [ ] Webhook notifications
- [ ] Admin dashboard
- [ ] API analytics and metrics
- [ ] Rate limiting per user
- [ ] Caching for repeated requests
- [ ] Mobile app integration

## 📞 Support

- **Documentation**: Check the `/docs` endpoint
- **Moondream Docs**: https://docs.moondream.ai/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Issues**: Open an issue on GitHub


## 🙏 Acknowledgments

- **Moondream AI**: Vision language model
- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

## ⚠️ Disclaimer

This tool is for educational and legitimate purposes only. Ensure you have proper authorization before processing identity documents. Always comply with local privacy laws and regulations (GDPR, CCPA, etc.).

---

**Version**: 1.0.0  
**Last Updated**: October 2025  

For more information, visit the [documentation](http://localhost:8000/docs) or check out the [Quick Start Guide](QUICKSTART.md).

