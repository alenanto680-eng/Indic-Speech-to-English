"""
Pipeline for Speech Recognition and Neural Machine Translation.
Wraps IndicConformer (Speech -> Indic Text) and IndicTrans2 (Indic Text -> English).
"""
import os
import re
import threading
import time
from typing import Dict, Any, Optional

import numpy as np
import torch
from transformers import AutoModel, AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor

from config import (
    ASR_MODEL_NAME,
    TRANSLATION_MODEL_NAME,
    TARGET_LANG,
    LANG_MAPPINGS,
    NUM_CPU_THREADS,
    DEFAULT_LANG,
    DEFAULT_SPEED,
    SAMPLE_RATE,
)


class SpeechTranslationPipeline:
    """
    Combined pipeline for speech transcription and Indic-to-English translation.
    """

    def __init__(
        self,
        asr_model_name: str = ASR_MODEL_NAME,
        translation_model_name: str = TRANSLATION_MODEL_NAME,
        num_threads: Optional[int] = None,
    ):
        self.asr_model_name = asr_model_name
        self.translation_model_name = translation_model_name
        self.num_threads = num_threads or NUM_CPU_THREADS
        self._lock = threading.Lock()

        self.asr_model = None
        self.tokenizer = None
        self.translation_model = None
        self.processor = None

    def load(self):
        """
        Loads both models into memory with CPU thread optimization and warmup.
        """
        if self.asr_model is not None and self.translation_model is not None:
            return self

        torch.set_num_threads(self.num_threads)

        print(f"Loading IndicConformer ASR '{self.asr_model_name}'...")
        self.asr_model = AutoModel.from_pretrained(
            self.asr_model_name,
            trust_remote_code=True,
        )

        print(f"Loading IndicTrans2 MT '{self.translation_model_name}'...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.translation_model_name,
            trust_remote_code=True,
        )
        self.translation_model = AutoModelForSeq2SeqLM.from_pretrained(
            self.translation_model_name,
            trust_remote_code=True,
        ).eval()

        self.processor = IndicProcessor(inference=True)

        self._warmup()
        print("Speech Translation Pipeline is ready.")
        return self

    def _warmup(self):
        """Warm-up pass to avoid initial latency."""
        try:
            with torch.inference_mode():
                dummy_wav = torch.zeros(1, SAMPLE_RATE)
                self.asr_model(dummy_wav, "hi", "ctc")
        except Exception as e:
            print(f"ASR Warm-up skipped: {e}")

    def translate_to_english(self, text: str, src_lang_flores: str, beams: int = 1) -> str:
        """
        Translates text from an Indic source language to English.
        """
        if not text or not text.strip():
            return ""

        # Split sentences by punctuation
        sentences = [s.strip() for s in re.split(r"(?<=[.!?।])\s+", text) if s.strip()] or [text]
        batch = self.processor.preprocess_batch(sentences, src_lang=src_lang_flores, tgt_lang=TARGET_LANG)
        inputs = self.tokenizer(batch, padding=True, truncation=True, return_tensors="pt")

        with torch.inference_mode():
            outputs = self.translation_model.generate(**inputs, max_length=256, num_beams=beams)

        decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return " ".join(self.processor.postprocess_batch(decoded, lang=TARGET_LANG)).strip()

    def process_audio(
        self,
        samples: np.ndarray,
        lang: str = DEFAULT_LANG,
        speed: str = DEFAULT_SPEED,
    ) -> Dict[str, Any]:
        """
        Runs speech-to-text followed by Indic-to-English translation.
        - speed='fast': CTC decoding + 1 beam search
        - speed='accurate': RNN-T decoding + 4 beam search
        """
        if self.asr_model is None:
            self.load()

        src_flores = LANG_MAPPINGS.get(lang, LANG_MAPPINGS[DEFAULT_LANG])
        decoder_mode = "ctc" if speed == "fast" else "rnnt"
        beams = 1 if speed == "fast" else 4

        start_time = time.time()
        wav = torch.from_numpy(samples.copy()).unsqueeze(0)

        with self._lock, torch.inference_mode():
            raw_asr = self.asr_model(wav, lang, decoder_mode)
            if isinstance(raw_asr, (list, tuple)):
                native_text = " ".join(map(str, raw_asr)).strip()
            else:
                native_text = str(raw_asr).strip()

            english_text = ""
            if native_text:
                english_text = self.translate_to_english(native_text, src_flores, beams=beams)

        elapsed = round(time.time() - start_time, 2)
        return {
            "native": native_text,
            "english": english_text,
            "sec": elapsed,
        }


# Global pipeline instance
pipeline = SpeechTranslationPipeline()
