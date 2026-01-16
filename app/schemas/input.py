from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class TextInput(BaseModel):
    id: str = Field(..., description="Unique identifier for the text input")
    text: str = Field(..., description="The text content to be processed")
    language: Optional[str] = Field(None, description="Detected language (filled by server), e.g., 'en'")

class BatchTextInput(BaseModel):
    items: List[TextInput] = Field(..., description="A list of text inputs to be processed in a batch")
    
class FileUploadInfo(BaseModel):
    filename: str = Field(..., description="Name of the uploaded file")
    format: Literal["txt", "csv", "json", "jsonl", "xlsx"] = Field(..., description="Format of the uploaded file")
    items_count: int = Field(..., description="Number of text items found in the file")
    size_bytes: int = Field(..., description="Size of the file in bytes")
