# 🌐 Indic Speech to English · Real-Time Translation

An open-source, AI-powered system that captures spoken Indian languages in real time, converts speech to native text using **AI4Bharat IndicConformer**, and translates it into fluent English using **AI4Bharat IndicTrans2**.

Includes a clean, responsive web interface with live audio streaming, animated waveform visualizer, side-by-side transcripts, and dark/light themes.

---

## ⚡ Highlights

- **End-to-End Pipeline**: Combines Speech-to-Text (ASR) + Neural Machine Translation (NMT) in a single integrated flow.
- **Zero API Keys Required**: 100% open-source and runs locally on your machine with no external API charges or limits.
- **Offline Capable**: Once model weights are downloaded from Hugging Face on the first run, the server runs completely offline.
- **11+ Supported Indian Languages**: Hindi, Malayalam, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Punjabi, Odia, and Urdu.
- **Speed & Quality Modes**:
  - **Fast**: CTC acoustic decoding + greedy translation (1 beam).
  - **More Accurate**: RNN-T acoustic decoding + 4-beam translation search.
- **Modern Web UI**: Live microphone stream with auto voice-detection (VAD), live sound bars, side-by-side native and English display, and one-click clipboard copy.

---

## 📂 Project Structure

```text
indic-translate/
├── config.py              # Central settings (models, language mappings, thresholds)
├── model.py               # Combined ASR + MT translation pipeline with warmup
├── server.py              # Clean FastAPI backend serving web UI & /chunk endpoint
├── run.py                 # CLI launcher for the web application
├── requirements.txt       # Core Python dependencies
├── .gitignore             # Git ignore file for venv, cache, and checkpoints
├── static/                # Frontend web assets
│   ├── css/
│   │   └── style.css      # UI stylesheet (light/dark themes, layout, waveforms)
│   └── js/
│       └── app.js         # Client-side audio capture, VAD, and UI events
└── templates/
    └── index.html         # Web client interface
```

---

## 🧠 Underlying Models

1. **Speech Recognition (ASR)**:
   - [`ai4bharat/indic-conformer-600m-multilingual`](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
   - Transcribes spoken audio into native Indian script.
2. **Translation (NMT)**:
   - [`ai4bharat/indictrans2-indic-en-1B`](https://huggingface.co/ai4bharat/indictrans2-indic-en-1B)
   - Translates Indic sentences into English using `IndicTransToolkit`.

---

## 🛠️ Prerequisites

Before installing the Python packages, ensure `ffmpeg` and system audio libraries are installed:

### Linux (Ubuntu / Debian)
```bash
sudo apt update
sudo apt install -y libsndfile1 ffmpeg python3-dev
```

### macOS
```bash
brew install libsndfile ffmpeg
```

---

## 🚀 Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/indic-translate.git
cd indic-translate
```

### 2. Create and Activate a Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note for NVIDIA GPU users (Optional)**:
> For GPU acceleration, install PyTorch with CUDA support from [pytorch.org](https://pytorch.org):
> ```bash
> pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
> ```

---

## 🌐 Running the Web Application

Launch the server using any of the following:

```bash
# Option 1: Using the runner script (Recommended)
python run.py

# Custom host or port
python run.py --host 0.0.0.0 --port 8000

# Option 2: Running server.py directly
python server.py

# Option 3: Using uvicorn
uvicorn server:app --host 0.0.0.0 --port 8000
```

Open your browser and navigate to:
```
http://localhost:8000
```

### How to Use the Web App:
1. **Choose Your Language**: Select the Indian language you want to speak in the dropdown.
2. **Select Speed**:
   - `Fast` (faster turnaround, great for real-time conversation).
   - `More Accurate` (higher precision for formal or complex sentences).
3. **Click the Microphone**: Speak naturally. The animated sound bars react to your voice.
4. **Instant Output**: When you pause, the native transcription and English translation appear side-by-side.
5. **Copy**: Click **Copy English** to copy the translated text to your clipboard.

---

## 🗣️ Supported Languages & Mapping

| Code | Language | Native Script | IndicTrans2 Code |
| :---: | :--- | :--- | :--- |
| `hi` | Hindi | हिन्दी | `hin_Deva` |
| `ml` | Malayalam | മലയാളം | `mal_Mlym` |
| `ta` | Tamil | தமிழ் | `tam_Taml` |
| `te` | Telugu | తెలుగు | `tel_Telu` |
| `kn` | Kannada | ಕನ್ನಡ | `kan_Knda` |
| `bn` | Bengali | বাংলা | `ben_Beng` |
| `mr` | Marathi | मराठी | `mar_Deva` |
| `gu` | Gujarati | ગુજરાતી | `guj_Gujr` |
| `pa` | Punjabi | ਪੰਜਾਬੀ | `pan_Guru` |
| `or` | Odia | ଓଡ଼ିଆ | `ory_Orya` |
| `ur` | Urdu | اردو | `urd_Arab` |

---

## 🔌 API Reference

### `POST /chunk`
Processes an audio chunk and returns both native transcript and English translation.

- **Query Parameters**:
  - `lang` (default: `ml`): Source Indian language code.
  - `speed` (default: `fast`): `fast` or `accurate`.
- **Body**: Binary raw audio bytes (`float32`, 16,000 Hz, mono).
- **Response**:
  ```json
  {
    "native": "സുഖമാണോ",
    "english": "How are you",
    "sec": 0.38
  }
  ```

### `GET /health`
Returns system and model readiness status.

- **Response**:
  ```json
  {
    "status": "ok",
    "models_loaded": true,
    "asr_model": "ai4bharat/indic-conformer-600m-multilingual",
    "translation_model": "ai4bharat/indictrans2-indic-en-1B"
  }
  ```

---

## ❓ Frequently Asked Questions (FAQ)

### Do I need any API keys or tokens?
**No.** Both the ASR and translation models are open-source and hosted publicly by AI4Bharat on Hugging Face. No tokens or API keys are required.

### Can it run offline?
**Yes.** Once the model weights are downloaded to your local cache on the first launch, the application operates 100% locally with zero internet connectivity.

---

## 📄 License & Acknowledgements

- Speech recognition powered by [AI4Bharat IndicConformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual).
- Machine translation powered by [AI4Bharat IndicTrans2](https://huggingface.co/ai4bharat/indictrans2-indic-en-1B) and [IndicTransToolkit](https://github.com/AI4Bharat/IndicTransToolkit).
- Web framework by [FastAPI](https://fastapi.tiangolo.com/).
