import os
import shutil
import re
from collections import Counter
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import PyPDF2
from fastapi.responses import FileResponse

# ====================================================================
# AUTO-CONFIGURE FFMPEG DEPENDENCY FOR HUGGINGFACE AUDIO SUPPORT
# ====================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")

if not os.path.exists(ffmpeg_path):
    try:
        import imageio_ffmpeg
        # Copy the pre-compiled ffmpeg binary to our local dir named exactly 'ffmpeg.exe'
        shutil.copy2(imageio_ffmpeg.get_ffmpeg_exe(), ffmpeg_path)
    except ImportError:
        pass

# Ensure path is set for ffmpeg inside backend so HuggingFace can find it natively
os.environ["PATH"] = current_dir + os.pathsep + os.environ.get("PATH", "")


class AudioTranscriber:
    """
    Handles loading the AI model for Audio and processing audio files into text.
    """
    def __init__(self):
        print("Loading Whisper model for Speech-to-Text...")
        try:
            self.asr = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
            print("Audio model loaded successfully!")
        except Exception as e:
            print(f"Loading fallback audio model due to error: {e}")
            self.asr = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")

    def transcribe(self, file_path: str) -> str:
        """
        Transcribes the given audio file and returns the text.
        """
        result = self.asr(file_path)
        if isinstance(result, list) and len(result) > 0:
            result = result[0]
        return result.get("text", "")


class DocumentProcessor:
    """
    Handles parsing and extracting raw text from uploaded Document files (e.g., PDFs).
    """
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Reads a PDF file page by page and concatenates the text.
        Also cleans up broken newlines for better summarization and readability.
        """
        text = ""
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n\n"
        except Exception as e:
            raise ValueError(f"Failed to read PDF file: {e}")
            
        # Clean up the raw PDF text layout:
        # 1. Replace single newlines with spaces to fix broken lines
        # 2. Keep multiple newlines to preserve actual paragraph/page breaks
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        text = re.sub(r' +', ' ', text) # Fix double spaces
        
        return text.strip()


class TextAnalyzer:
    """
    A class to generate insights from text: creating summaries and extracting keywords.
    
    Uses a pure Python EXTRACTIVE SUMMARIZATION algorithm:
    1. Split the text into sentences
    2. Score each sentence by how many important (non-stop) words it contains
    3. Pick the top 3 highest-scoring sentences as the summary
    
    This approach needs NO external model downloads and is very fast.
    """
    def __init__(self):
        # A static set of common English STOP WORDS.
        # These are filtered out during keyword extraction and summarization scoring.
        # This avoids needing large external NLTK data downloads.
        self.stop_words = {
            "the", "and", "that", "this", "then", "there", "with", "from", 
            "have", "has", "had", "been", "will", "would", "shall", "should", 
            "what", "when", "where", "which", "who", "whom", "they", "them", 
            "their", "these", "those", "you", "your", "yours", "our", "ours",
            "are", "was", "were", "can", "could", "for", "not", "but", "all",
            "any", "both", "each", "few", "more", "most", "other", "some", "such",
            "only", "own", "same", "very", "too", "also", "just", "now", "well",
            "even", "much", "many", "like", "how", "why", "we", "my", "me", "is", "it",
            "about", "above", "after", "again", "against", "being", "below",
            "between", "does", "doing", "down", "during", "into", "its",
            "off", "once", "out", "over", "than", "through", "under", "until",
            "while", "here", "there", "a", "an", "in", "on", "at", "to", "of", "by"
        }

    def _split_into_sentences(self, text: str) -> list:
        """
        Splits raw text into a list of clean sentences using regex.
        Handles period, question mark, and exclamation mark as delimiters.
        """
        # Split on sentence endings followed by space or end-of-string
        raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        # Keep only sentences with at least 5 words (filters out headings/labels)
        return [s.strip() for s in raw_sentences if len(s.strip().split()) >= 5]

    def _score_sentence(self, sentence: str, word_frequencies: dict) -> float:
        """
        Scores a single sentence based on the sum of its meaningful word frequencies.
        Higher score = sentence contains more important/frequent words.
        """
        words = re.findall(r'\b[a-z]{3,}\b', sentence.lower())
        if not words:
            return 0.0
        score = sum(word_frequencies.get(w, 0) for w in words)
        # Normalize by sentence length to avoid bias towards very long sentences
        return score / len(words)

    def summarize(self, text: str, top_n: int = 3) -> str:
        """
        Generates a summary by extracting the top N most important sentences.
        
        Algorithm (Extractive Summarization):
        1. Count frequency of every meaningful word across the entire text
        2. Score each sentence by the average frequency of its words
        3. Return top N highest-scoring sentences in their original order
        """
        sentences = self._split_into_sentences(text)
        
        if len(sentences) < 2:
            return "Text is too short to generate a meaningful summary."
        
        # Step 1: Build word frequency table (excluding stop words)
        all_words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        filtered = [w for w in all_words if w not in self.stop_words]
        word_freq = Counter(filtered)
        
        # Step 2: Score each sentence
        scored = [(i, sentence, self._score_sentence(sentence, word_freq)) 
                  for i, sentence in enumerate(sentences)]
        
        # Step 3: Sort by score (descending) and pick top N
        top_sentences = sorted(scored, key=lambda x: x[2], reverse=True)[:top_n]
        
        # Step 4: Re-sort by original position so the summary reads naturally
        top_sentences.sort(key=lambda x: x[0])
        
        return " ".join(s[1] for s in top_sentences)

    def extract_keywords(self, text: str, top_n: int = 6) -> list:
        """
        Extracts the top N most frequent meaningful words from the text.
        """
        # Lowercase the text and extract words longer than 3 characters
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Discard the irrelevant common English words
        filtered_words = [word for word in words if word not in self.stop_words]
        
        # Count occurrences using Python's built-in Counter
        counts = Counter(filtered_words)
        
        # Return only the word strings of the top_n most common occurrences
        return [item[0] for item in counts.most_common(top_n)]


# ====================================================================
# API SERVER CONFIGURATION
# ====================================================================

app = FastAPI(title="Viva Ready Speech & Text API")

# Standard CORS Setup for Web Interactivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our specialized engines globally when server starts
# NOTE: TextAnalyzer uses lazy loading - it won't download the heavy model until first use
audio_engine = AudioTranscriber()
pdf_engine = DocumentProcessor()
text_engine = TextAnalyzer()


@app.get("/health")
async def health_check():
    """Simple health check to verify the server is running."""
    return {"status": "ok"}


# ====================================================================
# APP ROUTES
# ====================================================================

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(current_dir, "index.html"))

@app.get("/style.css")
async def serve_css():
    return FileResponse(os.path.join(current_dir, "style.css"))

@app.get("/firebase-config.js")
async def serve_fb():
    # Only if firebase config is a separate physical file nearby
    return FileResponse(os.path.join(current_dir, "firebase-config.js"))

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    """
    Main Universal Endpoint:
    Accepts Audio OR PDF, converts it to readable text, 
    and passes it through the AI Pipeline for Summarization and Keyword Extraction.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    filename = file.filename.lower()
    ext = filename.split(".")[-1]
    # Use absolute path so it works no matter how the server is launched
    temp_path = os.path.join(current_dir, f"temp_upload.{ext}")
    
    try:
        # Step 1: Save the incoming file streams strictly to disk temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Step 2: Route file to appropriate Processing Engine Class
        if ext == "pdf":
            raw_text = pdf_engine.extract_text_from_pdf(temp_path)
        elif ext in ["wav", "mp3", "m4a", "ogg", "flac", "webm", "mp4"]:
            raw_text = audio_engine.transcribe(temp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        if not raw_text or not raw_text.strip():
            return {"error": "Processing completed, but no understandable text was identified."}
            
        # Step 3: Run Text Analysis via NLP Engine
        summary = text_engine.summarize(raw_text)
        keywords = text_engine.extract_keywords(raw_text)
        
        # Return comprehensive data payload
        return {
            "success": True,
            "originalText": raw_text,
            "summary": summary,
            "keywords": keywords,
            "type": "PDF" if ext == "pdf" else "Audio"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing Pipeline Error: {str(e)}")
    finally:
        # Step 4: Cleanup File System
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
