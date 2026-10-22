import torch
import numpy as np
import logging
from config.settings import settings
from omnivoice import OmniVoice, OmniVoiceGenerationConfig
from core.normalizer import AmharicTextNormalizer
from core.chunker import TextChunker

logger = logging.getLogger("uvicorn.error")

class TTSEngineSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTSEngineSingleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info(f"Initializing OmniVoice model on device {settings.DEVICE}...")
        dtype = torch.float16 if settings.DTYPE == "float16" else torch.float32
        
        self.model = OmniVoice.from_pretrained(
            settings.MODEL_ID,
            device_map=settings.DEVICE,
            dtype=dtype,
        )
        self.config = OmniVoiceGenerationConfig(num_step=32, guidance_scale=2.0)
        logger.info("OmniVoice Engine loaded successfully.")

    def synthesize(self, text: str) -> bytes:
        # 1. Normalize Input Text
        normalized_text = AmharicTextNormalizer.normalize(text)
        
        # 2. Chunk into processing units
        chunks = TextChunker.chunk_amharic_text(normalized_text, settings.MAX_CHUNK_CHARS)
        
        audio_segments = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Synthesizing chunk {i+1}/{len(chunks)}: '{chunk}'")
            audio = self.model.generate(
                text=chunk,
                language="Amharic",
                generation_config=self.config,
            )
            
            # Extract raw array
            audio_data = audio[0] if isinstance(audio, (list, tuple)) else audio
            if isinstance(audio_data, torch.Tensor):
                audio_data = audio_data.cpu().numpy()
            
            audio_segments.append(audio_data.flatten())

        # 3. Concatenate all audio segments
        if not audio_segments:
            return b""
            
        full_waveform = np.concatenate(audio_segments)
        
        # Convert float32 [-1.0, 1.0] to 16-bit PCM bytes
        int16_pcm = (full_waveform * 32767).astype(np.int16)
        return int16_pcm.tobytes()