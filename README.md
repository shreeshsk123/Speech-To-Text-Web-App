# 🎤 Speech-To-Text Web App

A simple and efficient web application that converts speech (audio) into text using Python and modern web technologies.

---

## 🚀 Features

* 🎙️ Convert speech/audio to text
* 📁 Upload audio files
* ⚡ Fast and accurate transcription
* 🌐 Simple and clean UI
* 🧠 Uses Python-based speech recognition

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python (Flask / your framework)
* **Libraries:** SpeechRecognition, pydub (if used)
* **Tools:** FFmpeg

---

## 📂 Project Structure

```
Speech-To-Text-Web-App/
│── static/
│── templates/
│── main.py
│── requirements.txt
│── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```
git clone https://github.com/shreeshsk123/Speech-To-Text-Web-App.git
cd Speech-To-Text-Web-App
```

---

### 2️⃣ Install Python

Make sure Python 3.x is installed
Download: https://www.python.org/downloads/

✔ أثناء installation, tick **"Add Python to PATH"**

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Install FFmpeg (IMPORTANT ⚠️)

This project requires FFmpeg for audio processing.

#### Steps:

1. Download FFmpeg: https://ffmpeg.org/download.html
2. Extract the ZIP file
3. Move folder to:

```
C:\ffmpeg
```

4. Add this path to Environment Variables:

```
C:\ffmpeg\bin
```

---

### 5️⃣ Verify FFmpeg Installation

```
ffmpeg -version
```

✔ If it shows version → Setup is correct

---

## ▶️ Running the Application

```
python main.py
```

Then open your browser:

```
http://127.0.0.1:5000/
```

---

## 👨‍💻 Usage

1. Upload an audio file 🎵
2. Click on convert
3. Get text output instantly ✨

---

## ⚠️ Important Notes

* ❌ Do NOT include large files like `ffmpeg.exe` in the repository
* ✅ Install FFmpeg separately
* ⚠️ Ensure microphone/audio permissions (if using live input)

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork this repo and submit a pull request.

---

## 📧 Contact

**Author:** Shreesh Khamkar
GitHub: https://github.com/shreeshsk123

---

## ⭐ If you like this project

Give it a ⭐ on GitHub!
