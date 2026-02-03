"""
FastAPI Server for Blow AI Voice Assistant - FIXED VERSION
Enhanced audio processing with better debugging and validation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import base64
import tempfile
import os
from typing import List, Dict, Optional
import numpy as np
import io
import wave
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Voice assistant imports
try:
    import whisper
    import soundfile as sf
    import ollama
    import edge_tts
    from scipy.signal import butter, filtfilt, resample_poly
    import librosa
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nInstall with:")
    print("  pip install openai-whisper soundfile ollama edge-tts scipy librosa google-generativeai")
    exit(1)

app = FastAPI(title="Blow AI Voic``e Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- CONFIG --------------------
CONFIG = {
    "assistant_name": "Blow",
    "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
    "whisper_model": os.getenv("WHISPER_MODEL", "base"),
    "tts_voice": os.getenv("TTS_VOICE", "en-US-GuyNeural"),
    "target_sample_rate": int(os.getenv("TARGET_SAMPLE_RATE", "16000")),
    "min_audio_duration": float(os.getenv("MIN_AUDIO_DURATION", "0.3")),
    "max_audio_duration": float(os.getenv("MAX_AUDIO_DURATION", "30.0")),
    "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
    "default_llm": os.getenv("DEFAULT_LLM", "ollama"),
}

# -------------------- GLOBAL STATE --------------------
class AssistantState:
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.whisper_model = None
        self.selected_llm: str = CONFIG["default_llm"]  # Track which LLM is being used
        self.gemini_chat = None  # For Gemini conversation state
        
    def reset(self):
        self.conversation_history = []
        self.gemini_chat = None

state = AssistantState()

# -------------------- MODELS --------------------
class TranscribeRequest(BaseModel):
    audio_data: str
    sample_rate: int = 48000

class ChatRequest(BaseModel):
    message: str
    use_history: bool = True
    llm_model: str = "ollama"  # "ollama" or "gemini"

class TTSRequest(BaseModel):
    text: str
    voice: str = "en-US-GuyNeural"

# -------------------- AUDIO PROCESSING --------------------

def decode_audio_data(audio_bytes: bytes, reported_sr: int) -> tuple[Optional[np.ndarray], Optional[int]]:
    """
    Try multiple methods to decode audio data
    Returns: (audio_array, sample_rate) or (None, None) if failed
    """
    
    # Method 1: Try soundfile with BytesIO (handles WAV directly)
    try:
        audio_array, sr = sf.read(io.BytesIO(audio_bytes))
        print(f"   ✅ Decoded as WAV (sr={sr}Hz, shape={audio_array.shape})")
        return audio_array, sr
    except Exception as e:
        print(f"   ⚠️  WAV decode failed: {str(e)[:80]}")
    
    # Method 2: Try as WebM with temp file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        audio_array, sr = sf.read(tmp_path)
        os.unlink(tmp_path)
        print(f"   ✅ Decoded as WebM (sr={sr}Hz, shape={audio_array.shape})")
        return audio_array, sr
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"   ⚠️  WebM decode failed: {str(e)[:80]}")
    
    # Method 3: Try with librosa (more robust)
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        audio_array, sr = librosa.load(tmp_path, sr=None, mono=True)
        os.unlink(tmp_path)
        print(f"   ✅ Decoded with librosa (sr={sr}Hz, shape={audio_array.shape})")
        return audio_array, sr
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"   ⚠️  Librosa decode failed: {str(e)[:80]}")
    
    # Method 4: Try as OGG
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        audio_array, sr = sf.read(tmp_path)
        os.unlink(tmp_path)
        print(f"   ✅ Decoded as OGG (sr={sr}Hz, shape={audio_array.shape})")
        return audio_array, sr
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print(f"   ⚠️  OGG decode failed: {str(e)[:80]}")
    
    print(f"   ❌ All decode methods failed")
    return None, None


def preprocess_audio(audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Minimal preprocessing to avoid degrading speech quality
    """
    # Ensure mono
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    # Remove DC offset
    audio_data = audio_data - np.mean(audio_data)
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val * 0.95
    
    # Only apply high-pass filter if sample rate is high enough
    if sample_rate >= 16000:
        try:
            nyquist = sample_rate / 2
            cutoff = 80  # Remove frequencies below 80Hz
            normalized_cutoff = min(cutoff / nyquist, 0.99)
            b, a = butter(2, normalized_cutoff, btype='high')  # Order 2 (gentler)
            audio_data = filtfilt(b, a, audio_data)
        except Exception as e:
            print(f"   ⚠️  Filter failed: {e}")
    
    return audio_data.astype(np.float32)


def validate_audio(audio_array: np.ndarray, sample_rate: int) -> tuple[bool, str]:
    """
    Validate audio quality
    Returns: (is_valid, error_message)
    """
    # Check for NaN or inf
    if np.any(np.isnan(audio_array)) or np.any(np.isinf(audio_array)):
        return False, "Audio contains invalid values (NaN/inf)"
    
    # Check duration
    duration = len(audio_array) / sample_rate
    if duration < CONFIG["min_audio_duration"]:
        return False, f"Audio too short ({duration:.2f}s < {CONFIG['min_audio_duration']}s)"
    
    if duration > CONFIG["max_audio_duration"]:
        return False, f"Audio too long ({duration:.2f}s > {CONFIG['max_audio_duration']}s)"
    
    # Check RMS (signal strength)
    rms = np.sqrt(np.mean(audio_array**2))
    if rms < 0.001:
        return False, f"Audio too quiet (RMS={rms:.6f})"
    
    # Check for completely silent audio
    if np.max(np.abs(audio_array)) < 0.001:
        return False, "Audio appears to be silent"
    
    return True, ""


def save_debug_audio(audio_array: np.ndarray, sample_rate: int, prefix: str = "debug"):
    """Save audio for debugging purposes"""
    try:
        debug_path = f"/tmp/{prefix}_{int(asyncio.get_event_loop().time()*1000)}.wav"
        sf.write(debug_path, audio_array, sample_rate)
        print(f"   💾 Debug audio saved: {debug_path}")
    except Exception as e:
        print(f"   ⚠️  Could not save debug audio: {e}")


# -------------------- STARTUP --------------------
@app.on_event("startup")
async def startup_event():
    """Initialize Whisper model and Gemini on startup"""
    print("🚀 Initializing Blow AI Voice Assistant API...")
    try:
        print(f"📦 Loading Whisper '{CONFIG['whisper_model']}' model...")
        state.whisper_model = whisper.load_model(CONFIG["whisper_model"])
        print("✅ Whisper model loaded successfully")
        print(f"   Model: {CONFIG['whisper_model']}")
        print(f"   Target sample rate: {CONFIG['target_sample_rate']}Hz")
    except Exception as e:
        print(f"❌ Failed to load Whisper: {e}")

    try:
        ollama.list()
        print("✅ Ollama connected")
    except Exception as e:
        print(f"⚠️  Ollama not available: {e}")
    
    # Initialize Gemini
    try:
        if CONFIG["gemini_api_key"]:
            genai.configure(api_key=CONFIG["gemini_api_key"])
            print("✅ Gemini AI configured successfully")
    except Exception as e:
        print(f"⚠️  Gemini initialization failed: {e}")

# -------------------- ENDPOINTS --------------------

@app.get("/")
async def root():
    return {
        "name": "Blow AI Voice Assistant API",
        "version": "5.0 - Fixed Audio Processing",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Check if all services are running"""
    health = {
        "whisper": state.whisper_model is not None,
        "ollama": False,
        "gemini": False,
        "tts": True
    }
    
    try:
        ollama.list()
        health["ollama"] = True
    except:
        pass
    
    try:
        genai.list_models()
        health["gemini"] = True
    except:
        pass
    
    return health

@app.get("/models")
async def get_available_models():
    """Get list of available LLM models"""
    models = {
        "available": ["ollama", "gemini"],
        "current": state.selected_llm,
        "ollama": {
            "name": "Ollama (Local)",
            "model": CONFIG["ollama_model"],
            "available": False
        },
        "gemini": {
            "name": "Google Gemini 2.0 Flash",
            "model": "gemini-2.5-flash",
            "available": False
        }
    }
    
    try:
        ollama.list()
        models["ollama"]["available"] = True
    except:
        pass
    
    try:
        genai.list_models()
        models["gemini"]["available"] = True
    except:
        pass
    
    return models

@app.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    """Transcribe audio to text using Whisper"""
    if not state.whisper_model:
        raise HTTPException(status_code=503, detail="Whisper model not loaded")
    
    try:
        print("\n" + "="*70)
        print("🎤 TRANSCRIPTION REQUEST")
        print("="*70)
        print(f"Reported sample rate: {request.sample_rate}Hz")
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_data)
        print(f"Received: {len(audio_bytes):,} bytes ({len(audio_bytes)/1024:.1f} KB)")
        
        # Decode audio
        audio_array, detected_sr = decode_audio_data(audio_bytes, request.sample_rate)
        
        if audio_array is None:
            return {
                "text": "",
                "success": False,
                "error": "Could not decode audio format"
            }
        
        print(f"\n📊 Raw Audio Info:")
        print(f"   Duration: {len(audio_array)/detected_sr:.2f}s")
        print(f"   Samples: {len(audio_array):,}")
        print(f"   Sample rate: {detected_sr}Hz")
        print(f"   Min: {np.min(audio_array):.4f}, Max: {np.max(audio_array):.4f}")
        print(f"   RMS: {np.sqrt(np.mean(audio_array**2)):.4f}")
        
        # Save debug audio (original)
        save_debug_audio(audio_array, detected_sr, "01_original")
        
        # Preprocess
        audio_array = preprocess_audio(audio_array, detected_sr)
        save_debug_audio(audio_array, detected_sr, "02_preprocessed")
        
        # Resample to 16kHz if needed
        if detected_sr != CONFIG["target_sample_rate"]:
            print(f"\n🔄 Resampling: {detected_sr}Hz → {CONFIG['target_sample_rate']}Hz")
            audio_array = librosa.resample(
                audio_array,
                orig_sr=detected_sr,
                target_sr=CONFIG["target_sample_rate"]
            )
            save_debug_audio(audio_array, CONFIG["target_sample_rate"], "03_resampled")
        
        # Validate audio
        is_valid, error_msg = validate_audio(audio_array, CONFIG["target_sample_rate"])
        if not is_valid:
            print(f"\n❌ Audio validation failed: {error_msg}")
            return {
                "text": "",
                "success": False,
                "error": error_msg
            }
        
        print(f"\n📊 Processed Audio Info:")
        print(f"   Duration: {len(audio_array)/CONFIG['target_sample_rate']:.2f}s")
        print(f"   Samples: {len(audio_array):,}")
        print(f"   RMS: {np.sqrt(np.mean(audio_array**2)):.4f}")
        
        # Transcribe with Whisper
        print(f"\n🔄 Running Whisper transcription...")
        
        result = state.whisper_model.transcribe(
            audio_array,
            language="en",
            fp16=False,
            task="transcribe",
            temperature=0.0,
            best_of=3,
            beam_size=5,
            word_timestamps=False,
            condition_on_previous_text=False,
            initial_prompt="This is a conversation with a voice assistant.",
        )
        
        text = result.get("text", "").strip()
        
        # Filter out common Whisper artifacts
        artifacts = [".", "..", "...", "....", "Thank you.", "Thanks for watching!"]
        if text in artifacts:
            print(f"\n⚠️  Whisper returned artifact: '{text}'")
            text = ""
        
        print(f"\n📝 Transcription Result:")
        print(f"   Text: '{text}'")
        print(f"   Length: {len(text)} characters")
        print(f"   Language: {result.get('language', 'unknown')}")
        
        if not text:
            print(f"   ⚠️  No valid speech detected")
            print(f"   💡 Suggestion: Speak louder and closer to the microphone")
        
        print("="*70 + "\n")
        
        return {
            "text": text,
            "success": bool(text),
            "audio_duration": len(audio_array) / CONFIG["target_sample_rate"],
            "language": result.get("language", "en")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"\n❌ TRANSCRIPTION ERROR:\n{error_msg}\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """Get AI response from selected model (Ollama or Gemini)"""
    try:
        print(f"\n💬 Chat request: '{request.message}'")
        print(f"   Using LLM: {request.llm_model}")
        
        llm = request.llm_model or CONFIG["default_llm"]
        state.selected_llm = llm
        
        system_prompt = (
            "You are Blow, a helpful and friendly voice assistant. "
            "Keep responses concise (2-3 sentences) and conversational. "
            "Be natural and engaging."
        )
        
        if llm == "gemini":
            # Use Gemini
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Build conversation context
                conversation_text = ""
                if request.use_history and state.conversation_history:
                    for msg in state.conversation_history[-6:]:
                        role = "User" if msg["role"] == "user" else "Assistant"
                        conversation_text += f"{role}: {msg['content']}\n"
                
                prompt = f"{system_prompt}\n\n{conversation_text}User: {request.message}"
                
                response = model.generate_content(prompt)
                assistant_reply = response.text.strip()
                
                # Update history
                state.conversation_history.append({"role": "user", "content": request.message})
                state.conversation_history.append({"role": "assistant", "content": assistant_reply})
                
                print(f"🤖 Response: '{assistant_reply[:100]}{'...' if len(assistant_reply) > 100 else ''}'")
                
                return {
                    "response": assistant_reply,
                    "success": True,
                    "model": "gemini"
                }
            except Exception as e:
                print(f"❌ Gemini error: {e}")
                raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")
        
        else:
            # Use Ollama (default)
            try:
                messages = [
                    {"role": "system", "content": system_prompt}
                ]
                
                if request.use_history and state.conversation_history:
                    messages.extend(state.conversation_history[-6:])
                
                messages.append({"role": "user", "content": request.message})
                
                response = ollama.chat(model=CONFIG["ollama_model"], messages=messages)
                assistant_reply = response['message']['content'].strip()
                
                # Update history
                state.conversation_history.append({"role": "user", "content": request.message})
                state.conversation_history.append({"role": "assistant", "content": assistant_reply})
                
                print(f"🤖 Response: '{assistant_reply[:100]}{'...' if len(assistant_reply) > 100 else ''}'")
                
                return {
                    "response": assistant_reply,
                    "success": True,
                    "model": "ollama"
                }
            except Exception as e:
                print(f"❌ Ollama error: {e}")
                raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Edge TTS"""
    try:
        print(f"🔊 TTS request: '{request.text[:50]}...'")
        
        temp_file = os.path.join(
            tempfile.gettempdir(),
            f"tts_{int(asyncio.get_event_loop().time()*1000)}.mp3"
        )
        
        communicate = edge_tts.Communicate(request.text, request.voice)
        await communicate.save(temp_file)
        
        with open(temp_file, 'rb') as f:
            audio_data = f.read()
        
        try:
            os.remove(temp_file)
        except:
            pass
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        print(f"   ✅ TTS generated ({len(audio_data):,} bytes)")
        
        return {
            "audio": audio_base64,
            "success": True
        }
        
    except Exception as e:
        print(f"❌ TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation")
async def get_conversation():
    """Get conversation history"""
    return {
        "history": state.conversation_history,
        "count": len(state.conversation_history)
    }

@app.delete("/conversation")
async def clear_conversation():
    """Clear conversation history"""
    count = len(state.conversation_history)
    state.conversation_history.clear()
    print(f"🗑️  Cleared {count} conversation messages")
    return {
        "success": True,
        "cleared": count
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Starting Blow AI Voice Assistant API Server (Fixed Version)")
    print("="*70)
    print(f"Whisper Model: {CONFIG['whisper_model']}")
    print(f"Ollama Model: {CONFIG['ollama_model']}")
    print(f"Target Sample Rate: {CONFIG['target_sample_rate']}Hz")
    print(f"Min Duration: {CONFIG['min_audio_duration']}s")
    print("="*70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")