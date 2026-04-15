import os
import sys

# --- CRUCIAL FIX ---
# Add the current directory to the system PATH strictly for this script
# This guarantees that HuggingFace Transformers will find the ffmpeg.exe 
# we downloaded earlier, directly inside the backend folder!
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = current_dir + os.pathsep + os.environ.get("PATH", "")

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import shutil

app = FastAPI(title="Voice to Text API")

# Setup CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Speech-to-Text model...")
try:
    asr = pipeline("automatic-speech-recognition", model="microsoft/VibeVoice-ASR-HF")
    print("Model loaded successfully!")
except Exception as e:
    print(f"Warning/Error loading specific model: {e}")
    print("Trying fallback standard model (wav2vec2)...")
    asr = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")

from fastapi.responses import FileResponse

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(current_dir, "index.html"))

@app.get("/style.css")
async def serve_css():
    return FileResponse(os.path.join(current_dir, "style.css"))

@app.post("/transcribe")
async def transcribe(audio_file: UploadFile = File(...)):
    """
    Accepts an audio file upload (wav/mp3)
    Converts audio to text using HuggingFace native handling.
    """
    if not audio_file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    filename = audio_file.filename
    ext = filename.split(".")[-1].lower()
    
    if ext not in ["wav", "mp3", "m4a", "ogg", "flac", "webm", "mp4"]:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
        
    temp_path = f"temp_upload.{ext}"
    
    try:
        # Save uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
            
        print(f"Transcribing {filename}...")
        
        # HuggingFace pipeline will natively use the ffmpeg.exe we put in the folder
        # to decode it correctly, regardless of the audio format!
        result = asr(temp_path)
        
        # Pipeline might return a list or dictionary
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
            
        return {"text": result.get("text", "")}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
