# Architecture

This document describes the system architecture and design decisions of Aspectify.

## System Overview

Aspectify is built on a modular, layered architecture separating concerns across backend API, frontend UI, and external LLM services.

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Input Handler│  │Visualizations│  │  API Client  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP REST API
┌────────────────────────────▼────────────────────────────┐
│                   Backend (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   API Layer  │  │    Service   │  │    Utils     │ │
│  │   (Routes)   │  │     Layer    │  │   (Parsers)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────────┬────────────────────────────┘
                             │ LangChain API
┌────────────────────────────▼────────────────────────────┐
│               External LLM (Google Gemini)              │
└─────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Layer Structure

**1. API Layer** (`app/api/`)
- **Purpose**: HTTP request handling and response formatting
- **Components**:
  - `analyze.py`: Main analysis endpoint accepting text or CSV
  - `health.py`: Health check endpoint
  - `routers.py`: Router configuration and registration
- **Responsibilities**:
  - Request validation
  - File upload handling
  - Error response formatting
  - Turkish error messages

**2. Service Layer** (`app/services/`)
- **Purpose**: Business logic orchestration
- **Components**:
  - `absa_service.py`: Main ABSA orchestrator
- **Responsibilities**:
  - Input parsing via utils
  - Item normalization
  - Batch processing coordination
  - Async LLM calls with semaphore-based concurrency
  - Response aggregation
  - Quota error handling

**3. Utility Layer** (`app/utils/`)
- **Purpose**: Data transformation and validation
- **Components**:
  - `parsers.py`: Input/output parsing
  - `sanitizer.py`: Text cleaning and normalization
  - `language_detector.py`: Language detection
- **Key Functions**:
  - `parse_data()`: Converts text/CSV to standardized dict format
  - `create_df()`: DataFrame validation and column standardization
  - `toon_to_dicts()`: Parses TOON format LLM outputs
  - `sanitize_comment()`: Cleans text (Unicode, truncation, delimiter escaping)

**4. Prompting Layer** (`app/prompting/`)
- **Purpose**: Prompt management and rendering
- **Components**:
  - `manager.py`: Prompt loading, rendering, normalization
  - `minifiers.py`: Prompt compression
- **Features**:
  - YAML-based prompt templates
  - Jinja2 template rendering
  - Item normalization (comments→comment, language handling, ID generation)

**5. LLM Integration** (`app/llm/`)
- **Purpose**: External AI model communication
- **Components**:
  - `client.py`: LangChain Google GenAI wrapper
- **Configuration**:
  - Model: `gemini-1.5-flash`
  - Temperature: 0.0 (deterministic)
  - Max tokens: 8192

### Data Flow

```
1. User Input (text or CSV)
   ↓
2. API Layer: Validation & File Handling
   ↓
3. Service Layer: parse_data() → normalize_items()
   ↓
4. Prompting: Render Jinja2 template with items
   ↓
5. LLM Client: Send batch to Gemini
   ↓
6. Parsing: toon_to_dicts() extracts aspects
   ↓
7. Response: JSON with aspects per item
```

## Frontend Architecture

### Component Structure

**1. Entry Point** (`frontend/app.py`)
- Application routing
- Sidebar rendering
- CSS styling
- Mode selection

**2. API Client** (`frontend/api/client.py`)
- `call_api_text()`: POST text to `/analyze`
- `call_api_csv()`: POST CSV file to `/analyze`
- Error handling and user feedback

**3. Input Handlers** (`frontend/components/input_handlers.py`)
- `handle_text_input()`: Single text form
- `handle_csv_upload()`: CSV file upload with preview
- `handle_sample_data()`: Demo with pre-loaded dataset
- Callback pattern: `on_results(results, is_single)`

**4. Visualizations** (`frontend/components/visualizations.py`)
- `display_results()`: Main orchestrator
- `_display_summary_metrics()`: 4-column metrics
- `_display_sentiment_pie_chart()`: Plotly pie chart
- `_display_term_frequency_chart()`: Horizontal bar chart
- `_display_aspect_sentiment_matrix()`: Grouped table with satisfaction %
- `_display_detailed_results()`: Expandable item view
- `_display_export_options()`: CSV/Excel download

**5. Assets** (`frontend/assets/`)
- `sample_data.csv`: 15 phone review samples

## Data Formats

### Input Formats

**Text Input:**
```python
{
    "text": "The screen is great but battery drains fast."
}
```

**CSV Input:**
```csv
id,comments
1,The screen is great but battery drains fast.
2,Camera quality is excellent.
```

### TOON Output Format

Compact line-based format from LLM:

```
L:<id>|TERM~SENT;;TERM2~SENT2
```

**Example:**
```
L:1|screen~positive;;battery~negative
L:2|camera~positive
```

**Format Rules:**
- Each line starts with `L:<id>|`
- Aspects separated by `;;`
- Term and sentiment separated by `~`
- Sentiments: `positive`, `negative`, `neutral`

### API Response Format

```json
{
  "items_submitted": 2,
  "batches_sent": 1,
  "results": [
    {
      "id": "1",
      "aspects": [
        {"term": "screen", "sentiment": "positive"},
        {"term": "battery", "sentiment": "negative"}
      ]
    },
    {
      "id": "2",
      "aspects": [
        {"term": "camera", "sentiment": "positive"}
      ]
    }
  ],
  "duration_seconds": 1.23
}
```

## Design Decisions

### 1. TOON Format Over JSON

**Rationale:**
- Reduces token usage (~40% savings)
- Simpler for LLM to generate
- Easier to parse with regex patterns
- More compact for batch processing

**Trade-off:** Slightly more complex parsing logic

### 2. Async Batch Processing

**Implementation:**
```python
semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
```

**Rationale:**
- Prevents quota exhaustion
- Better error handling per batch
- Maintains order for results
- Graceful degradation on failures

### 3. Manager-Based Normalization

**Rationale:**
- Centralized item transformation logic
- Consistent behavior across service calls
- Easier to test and maintain
- Handles edge cases (missing IDs, language tuples)

### 4. Evidence Removal

**Decision:** Originally extracted evidence, now removed

**Rationale:**
- Not needed for most use cases
- Reduces LLM output complexity
- Faster processing
- Lower token costs

**Migration:** Simplified `toon_to_dicts()` from ~60 to ~25 lines

### 5. CSV-First Approach

**Decision:** CSV uploads with strict validation (id, comments columns)

**Rationale:**
- Standard format for bulk data
- Easy to validate and preview
- Supports batch workflows
- Familiar to business users

**Fallback:** Single text input also supported

### 6. Tolerant Parsing

**Implementation:**
```python
# Handles whitespace, blank lines, malformed entries
line = line.strip()
if not line or not line.startswith('L:'):
    continue
```

**Rationale:**
- LLMs occasionally produce extra whitespace
- Partial results better than full failure
- Graceful degradation improves UX

## Security Considerations

1. **Input Sanitization:**
   - Unicode normalization (NFKC)
   - Delimiter escaping
   - Control character removal
   - Max length truncation

2. **File Upload Validation:**
   - CSV extension check
   - Column presence validation
   - Pandas safe parsing

3. **Error Handling:**
   - No stack traces exposed to users
   - Generic error messages for external failures
   - Quota errors handled specifically

## Performance Optimization

1. **Batch Processing:**
   - Fixed-size batches (default: 10 items)
   - Async concurrency with semaphore
   - Avoids token counting overhead

2. **Prompt Efficiency:**
   - TOON format reduces tokens
   - Minimal instructions
   - Examples only when needed

3. **Frontend Caching:**
   - Streamlit session state for results
   - Avoid re-rendering on interactions
   - Lazy loading for detailed views

## Testing Strategy

- **Unit Tests**: Core utilities (parsers, sanitizer, manager)
- **Integration Tests**: Service layer with mock LLM
- **Coverage Target**: >80% for critical paths
- **Test Files**:
  - `tests/unit/test_parsers.py`
  - `tests/unit/test_sanitizer.py`
  - `tests/unit/test_manager.py`
  - `tests/unit/test_toon_parser.py`

## Deployment Considerations

- **Environment Variables**: API keys via `.env` file
- **Process Management**: Uvicorn with auto-reload
- **Monitoring**: Health check endpoint at `/health`
- **Scalability**: Stateless design enables horizontal scaling

