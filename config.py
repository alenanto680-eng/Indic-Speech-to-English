"""
Configuration settings for Indic Speech-to-English Translation.
"""
from pathlib import Path
import os

# Base paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Models
ASR_MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"
TRANSLATION_MODEL_NAME = "ai4bharat/indictrans2-indic-en-1B"
TARGET_LANG = "eng_Latn"
NUM_CPU_THREADS = os.cpu_count() or 4

# Language code mappings (ASR code -> IndicTrans2 Flores code)
LANG_MAPPINGS = {
    "hi": "hin_Deva",  # Hindi
    "kn": "kan_Knda",  # Kannada
    "ta": "tam_Taml",  # Tamil
    "te": "tel_Telu",  # Telugu
    "ml": "mal_Mlym",  # Malayalam
    "bn": "ben_Beng",  # Bengali
    "mr": "mar_Deva",  # Marathi
    "gu": "guj_Gujr",  # Gujarati
    "pa": "pan_Guru",  # Punjabi
    "or": "ory_Orya",  # Odia
    "ur": "urd_Arab",  # Urdu
}

# Audio Parameters
SAMPLE_RATE = 16000
MIN_AUDIO_SAMPLES = 8000  # 0.5 seconds at 16kHz
DEFAULT_LANG = "ml"
DEFAULT_SPEED = "fast"    # "fast" (CTC + 1 beam) or "accurate" (RNN-T + 4 beams)

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
