from fastapi import FastAPI
from api.routes import router
from config.settings import settings
from core.tts_engine import TTSEngineSingleton

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)

@app.on_event("startup")
def preload_models():
    # Warm up model on server boot
    TTSEngineSingleton()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)