"""
FastAPI Server for Indic Speech to English Translation.
Serves the web client and translates audio chunks in real-time.
"""
from contextlib import asynccontextmanager
import numpy as np
from fastapi import FastAPI, Request, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool

from config import (
    STATIC_DIR,
    TEMPLATES_DIR,
    SERVER_HOST,
    SERVER_PORT,
    DEFAULT_LANG,
    DEFAULT_SPEED,
    MIN_AUDIO_SAMPLES,
    ASR_MODEL_NAME,
    TRANSLATION_MODEL_NAME,
)
from model import pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Eagerly load both models on server startup
    pipeline.load()
    yield


app = FastAPI(
    title="Indic Speech to English",
    description="Real-time Speech Recognition and Translation into English for 11+ Indian languages",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse)
async def home():
    """Renders the speech translation user interface."""
    return FileResponse(TEMPLATES_DIR / "index.html")


@app.post("/chunk")
async def process_chunk(
    request: Request,
    lang: str = Query(DEFAULT_LANG, description="Language code (e.g., 'ml', 'hi', 'ta')"),
    speed: str = Query(DEFAULT_SPEED, description="Processing speed ('fast' or 'accurate')"),
):
    """
    Receives raw float32 PCM audio, transcribes the native speech,
    and returns both the native transcription and English translation.
    """
    raw_bytes = await request.body()
    samples = np.frombuffer(raw_bytes, dtype=np.float32).copy()

    if len(samples) < MIN_AUDIO_SAMPLES:
        # Audio is under 0.5s, ignore
        return {"native": "", "english": "", "sec": 0.0}

    result = await run_in_threadpool(pipeline.process_audio, samples, lang=lang, speed=speed)
    return result


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "models_loaded": pipeline.asr_model is not None and pipeline.translation_model is not None,
        "asr_model": ASR_MODEL_NAME,
        "translation_model": TRANSLATION_MODEL_NAME,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=SERVER_HOST, port=SERVER_PORT, reload=False)
