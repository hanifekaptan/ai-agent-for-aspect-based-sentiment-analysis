from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from app.schemas.common import LanguageDetectionResult

class Aspect(BaseModel):
    term: str = Field(..., description="The aspect term identified in the text")
    sentiment: Literal["positive", "negative", "neutral"] = Field(..., description="Sentiment associated with the aspect")
    evidence: Optional[str] = Field(None, description="Supporting evidence for the sentiment")
    
class ProcessingMeta(BaseModel):
    model_version: Optional[str] = Field(None, description="Version of the model used for processing")
    prompt_tokens: Optional[int] = Field(None, description="Number of tokens in the prompt")
    response_tokens: Optional[int] = Field(None, description="Number of tokens in the response")
    total_tokens: Optional[int] = Field(None, description="Total number of tokens used")
    elapsed_ms: Optional[int] = Field(None, description="Elapsed time in milliseconds for processing")
    steps: Optional[List[str]] = Field(None, description="List of processing steps taken")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost for the token usage in USD") 

class SingleAnalysisResult(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the analysis result")
    original_text: str = Field(..., description="The original text that was analyzed")
    processed_text: Optional[str] = Field(None, description="The processed version of the original text")
    language: Optional[LanguageDetectionResult] = Field(None, description="Detected language of the text")
    translated: bool = Field(False, description="Indicates if the text was translated for processing")
    aspects: List[Aspect] = Field(default_factory=list, description="List of identified aspects with sentiments")
    processing: Optional[ProcessingMeta] = Field(None, description="Metadata about the processing steps taken")

class AnalysisResults(BaseModel):
    results: List[SingleAnalysisResult] = Field(..., description="List of analysis results for each text input")