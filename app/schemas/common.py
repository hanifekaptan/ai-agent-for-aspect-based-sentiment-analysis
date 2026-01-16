from pydantic import BaseModel, Field
from typing import Optional, Any

class LanguageDetectionResult(BaseModel):
    language: str = Field(..., description="Detected language code, e.g., 'en' for English")
    code: int = Field(..., description="Status code of the detection process")
    confidence: float = Field(..., description="Confidence score of the detected language")

class ErrorResponse(BaseModel):
    code: str = Field(..., description="Error code representing the type of error")
    message: str = Field(..., description="Detailed error message explaining the error")
    details: Optional[Any] = Field(None, description="Additional details about the error")