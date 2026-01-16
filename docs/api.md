# API Reference

Complete API documentation for the Aspectify backend service.

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

Check if the API is running and healthy.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-14T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### Analyze Text/CSV

Perform aspect-based sentiment analysis on text or CSV data.

**Endpoint:** `POST /analyze`

**Content-Type:** `multipart/form-data`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | No* | Single text for analysis |
| `upload_file` | file | No* | CSV file (must have .csv extension) |

*Note: Either `text` OR `upload_file` must be provided, not both.

#### CSV Format Requirements

**Required Columns:**
- `id`: Unique identifier for each row
- `comments`: Text content to analyze

**Example CSV:**
```csv
id,comments
1,The screen is amazing but battery life is poor
2,Camera quality is excellent and price is reasonable
3,Customer service was terrible but product is good
```

**Column Rules:**
- If CSV has single column without header, it's treated as comments
- If CSV has multiple columns but no 'comments' column, returns error
- Missing 'id' column: auto-generates sequential IDs

#### Response Format

```json
{
  "items_submitted": 3,
  "batches_sent": 1,
  "results": [
    {
      "id": "1",
      "aspects": [
        {
          "term": "screen",
          "sentiment": "positive"
        },
        {
          "term": "battery life",
          "sentiment": "negative"
        }
      ]
    },
    {
      "id": "2",
      "aspects": [
        {
          "term": "camera quality",
          "sentiment": "positive"
        },
        {
          "term": "price",
          "sentiment": "positive"
        }
      ]
    },
    {
      "id": "3",
      "aspects": [
        {
          "term": "customer service",
          "sentiment": "negative"
        },
        {
          "term": "product",
          "sentiment": "positive"
        }
      ]
    }
  ],
  "duration_seconds": 1.45
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `items_submitted` | integer | Number of items processed |
| `batches_sent` | integer | Number of batches sent to LLM |
| `results` | array | Analysis results for each item |
| `results[].id` | string | Item identifier |
| `results[].aspects` | array | Extracted aspects with sentiments |
| `results[].aspects[].term` | string | Aspect term/feature |
| `results[].aspects[].sentiment` | string | Sentiment: `positive`, `negative`, or `neutral` |
| `duration_seconds` | float | Total processing time |

#### Status Codes

| Code | Description |
|------|-------------|
| `200 OK` | Successful analysis |
| `400 Bad Request` | Invalid input format or missing required fields |
| `422 Unprocessable Entity` | Invalid file format or CSV structure |
| `500 Internal Server Error` | Server error during processing |
| `503 Service Unavailable` | LLM quota exceeded or external service unavailable |

#### Error Response Format

```json
{
  "detail": "Error message in Turkish"
}
```

**Common Error Messages:**

| Error | Cause |
|-------|-------|
| `Metin veya CSV dosyası gerekli!` | Neither text nor file provided |
| `Sadece .csv dosyaları kabul edilir!` | Non-CSV file uploaded |
| `CSV dosyasında 'comments' sütunu bulunamadı!` | Missing required column |
| `Kota aşıldı veya servis kullanılamıyor` | LLM quota exceeded |

---

## Example Usage

### cURL - Text Input

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "text=The phone screen is beautiful but battery dies quickly"
```

### cURL - CSV Upload

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "upload_file=@reviews.csv"
```

### Python - requests

```python
import requests

# Text analysis
response = requests.post(
    "http://localhost:8000/analyze",
    data={"text": "Great camera but poor battery life"}
)
results = response.json()

# CSV analysis
with open("reviews.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"upload_file": f}
    )
    results = response.json()
```

---

## Rate Limiting

The system uses internal semaphore-based concurrency control:

- **Max Concurrent Batches**: 3
- **Batch Size**: 10 items
- **Retry Logic**: None (fails fast on quota errors)

**Quota Exceeded Handling:**
- Returns `503 Service Unavailable`
- Error message: `"Kota aşıldı veya servis kullanılamıyor"`
- Client should implement exponential backoff

---

## Data Processing Pipeline

```
Input → Validation → Parsing → Normalization → Batching → LLM → Parsing → Response
```

**Steps:**

1. **Validation**: Check file type, required parameters
2. **Parsing**: Convert input to standardized dict format
3. **Normalization**: Map column names, generate IDs, detect language
4. **Batching**: Split into fixed-size batches (default: 10)
5. **LLM Processing**: Async calls to Gemini with prompt template
6. **Output Parsing**: Parse TOON format to structured JSON
7. **Response**: Aggregate results with metadata

---

## Language Support

**Auto-Detection:**
- Language is automatically detected for each text
- Supported languages: Turkish, English, and others via LangDetect
- Language info used in prompt rendering

**Language Field (Internal):**
```python
{
    "id": "1",
    "comment": "Great product",
    "language": ("en", 0.99)  # (language_code, confidence)
}
```

---

## Text Sanitization

All input text is automatically sanitized before processing:

**Sanitization Steps:**
1. Unicode normalization (NFKC)
2. Whitespace normalization (collapse multiple spaces)
3. Word-boundary truncation (max 500 chars by default)
4. Delimiter escaping (`L:` prefix removal)
5. Control character removal

**Example:**
```python
# Before
"Great   screen！！！\n\nL:test"

# After  
"Great screen!!! test"
```

---

## Testing

**Interactive API Docs:**

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these interfaces to test API endpoints directly in your browser.

---

## Error Handling

### Client Errors (4xx)

**400 Bad Request:**
```json
{
  "detail": "Metin veya CSV dosyası gerekli!"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": "CSV dosyasında 'comments' sütunu bulunamadı!"
}
```

### Server Errors (5xx)

**500 Internal Server Error:**
```json
{
  "detail": "İşlem sırasında bir hata oluştu"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Kota aşıldı veya servis kullanılamıyor"
}
```

---

## Best Practices

1. **Batch Processing:**
   - Upload CSV files for bulk analysis
   - Aim for 10-50 items per request for optimal performance
   - Too many items may cause timeout

2. **Text Quality:**
   - Provide complete sentences for better aspect extraction
   - Avoid very short texts (< 10 chars)
   - Remove excessive special characters

3. **CSV Format:**
   - Always include 'id' and 'comments' columns
   - Use UTF-8 encoding
   - Keep comments concise (< 500 chars recommended)

4. **Error Handling:**
   - Implement retry logic with exponential backoff for 503 errors
   - Validate CSV structure before upload
   - Handle network timeouts gracefully

5. **Performance:**
   - Use async clients for concurrent requests
   - Cache results when appropriate
   - Monitor response times and adjust batch sizes

---

## Versioning

**Current Version:** v1

**API Stability:** Stable

**Breaking Changes:** None planned

**Deprecation Policy:** 6-month notice for any breaking changes

---

## Support

- **Issues**: [GitHub Issues](https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment/issues)
- **Documentation**: [Full Docs](https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment)
- **Email**: hanifekaptan.dev@gmail.com
