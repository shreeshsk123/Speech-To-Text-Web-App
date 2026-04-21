# 🎤📄 Speech & Document To Text Web App

A modern web application that converts **audio (speech)** and **PDF documents** into readable text using **AI-powered transcription and extraction techniques**.

---

## 🚀 Overview

This application allows users to upload audio and PDF files and convert them into text using advanced AI models and backend processing.

---

## ✨ Features

* 🎙️ Convert speech/audio to text using OpenAI Whisper
* 📄 Extract text from PDF documents
* 📁 Upload audio and PDF files
* ⚡ Fast and accurate processing
* 🌐 Simple and clean user interface

---

## 🧠 AI Model

* OpenAI Whisper (for speech-to-text)

---

## 🛠️ Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python (Flask)

### Libraries & Tools

* Whisper
* PyDub
* FFmpeg
* PyPDF / pdfplumber

---

## 📂 Project Structure

```
Speech-Document-To-Text-App/
│
├── static/            # CSS, JS, assets
├── templates/         # HTML files
├── uploads/           # Uploaded files
├── main.py            # Backend logic
├── requirements.txt   # Dependencies
└── README.md
```

---

## ⚙️ Installation & Setup

1. Clone the repository:

```
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Install FFmpeg and add it to system PATH.

4. Run the application:

```
python main.py
```

5. Open in browser:

```
http://127.0.0.1:5000
```

---

## 🔄 How It Works

### Audio to Text

* Upload audio file
* Audio is processed using FFmpeg
* Whisper model generates transcription
* Text is displayed on the UI

### PDF to Text

* Upload PDF file
* Text is extracted using PDF parser
* Extracted content is displayed

---

## 📌 Use Cases

* Lecture transcription
* Meeting notes
* Document digitization
* Accessibility tools

---

## 📈 Future Improvements

* Multi-language support
* Real-time speech input
* File export (TXT, DOCX)
* Cloud deployment

---

## 🤝 Contribution

Feel free to fork this repository and submit pull requests.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Shreesh Khamkar
