from pydantic import BaseModel, Field

class SynthesisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Amharic text string to synthesize.")
    language: str = Field(default="Amharic", description="Target language")
    format: str = Field(default="wav", description="Audio output format (wav or pcm)")

class HealthResponse(BaseModel):
    status: str
    device: str
    model: str