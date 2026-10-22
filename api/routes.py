import io
import wave
import hashlib
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response, StreamingResponse
from config.settings import settings
from api.schemas import SynthesisRequest, HealthResponse
from core.tts_engine import TTSEngineSingleton

router = APIRouter()

async def get_redis():
    redis = await aioredis.from_url(settings.REDIS_URL)
    try:
        yield redis
    finally:
        await redis.close()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        device=settings.DEVICE,
        model=settings.MODEL_ID
    )

@router.post("/v1/synthesize")
async def synthesize_text(
    payload: SynthesisRequest,
    redis: aioredis.Redis = Depends(get_redis)
):
    try:
        # Generate Cache Key
        text_hash = hashlib.sha256(payload.text.encode('utf-8')).hexdigest()
        cache_key = f"tts:amharic:{text_hash}"
        
        # Check Cache
        cached_pcm = await redis.get(cache_key)
        if cached_pcm:
            pcm_bytes = cached_pcm
        else:
            engine = TTSEngineSingleton()
            pcm_bytes = engine.synthesize(payload.text)
            # Store in Redis with 7-day TTL
            await redis.set(cache_key, pcm_bytes, ex=604800)

        # Wrap in WAV Container if requested
        if payload.format.lower() == "wav":
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)        # Mono
                wav_file.setsampwidth(2)       # 16-bit
                wav_file.setframerate(settings.SAMPLE_RATE)
                wav_file.writeframes(pcm_bytes)
            
            return Response(content=wav_buffer.getvalue(), media_type="audio/wav")

        return Response(content=pcm_bytes, media_type="audio/pcm")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))