# 🎙️ Blow AI - Advanced Voice Assistant

<div align="center">

![Blow AI Banner](https://img.shields.io/badge/Blow_AI-Voice_Assistant-2563eb?style=for-the-badge&logo=microphone&logoColor=white)

**Your Intelligent Voice-Powered AI Companion**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE)

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration)

</div>

---

## 🌟 Overview

**Blow AI** is a cutting-edge voice assistant that combines the power of speech recognition, natural language processing, and text-to-speech synthesis to create a seamless conversational experience. Whether you're looking to automate tasks, get quick answers, or simply have an engaging conversation, Blow AI is your go-to companion.

### ✨ Why Choose Blow AI?

- 🎤 **Natural Voice Interaction** - Speak naturally and get human-like responses
- 🧠 **Dual AI Models** - Choose between local Ollama or cloud-based Gemini AI
- 🎨 **Beautiful Modern UI** - Sleek, responsive design that works on any device
- 🔒 **Privacy-Focused** - Option to run completely offline with local models
- 🌍 **Multiple Voices** - 10+ natural-sounding voices across different accents
- 💬 **Conversation History** - Never lose track of your discussions
- ⚡ **Real-Time Processing** - Lightning-fast responses with optimized audio processing

---

## 🚀 Features

### 🎯 Core Capabilities

| Feature | Description |
|---------|-------------|
| **Voice Recognition** | Powered by OpenAI Whisper for accurate speech-to-text conversion |
| **AI Conversations** | Intelligent responses using Ollama (local) or Google Gemini (cloud) |
| **Text-to-Speech** | Natural voice synthesis with Edge TTS engine |
| **Chat History** | Save and organize multiple conversation threads |
| **Custom Prompts** | Create and save your favorite prompt templates |
| **Voice Selection** | Choose from 10+ voices (US, UK, AU, IN accents) |
| **Real-Time Streaming** | See transcriptions and responses as they happen |

### 🎨 User Interface

- **Modern Design** - Clean, intuitive interface inspired by leading AI assistants
- **Responsive Layout** - Perfect on desktop, tablet, and mobile devices
- **Dark/Light Mode Ready** - Easy on the eyes in any lighting condition
- **Sidebar Navigation** - Quick access to chat history and settings
- **Quick Actions** - Pre-built prompts to get started instantly

### 🔧 Technical Highlights

- **FastAPI Backend** - High-performance async API server
- **Advanced Audio Processing** - Multi-format support (WebM, WAV, OGG)
- **Noise Reduction** - Built-in filters for clearer audio
- **Error Recovery** - Robust error handling and validation
- **Extensible Architecture** - Easy to add new features and models

---

## 📸 Demo

<div align="center">

### Main Interface
![Main Interface](https://github.com/muthumaran333/blow-ai-/blob/main/image/image1.png)

### Voice Recording Modal
![Voice Modal](https://github.com/muthumaran333/blow-ai-/blob/main/image/image3.png)

### Settings Panel
![Settings](https://github.com/muthumaran333/blow-ai-/blob/main/image/image2.png)

</div>

---

## 🛠️ Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download here](https://python.org)
- **Node.js** (optional, for frontend development) - [Download here](https://nodejs.org)
- **Ollama** (for local AI) - [Download here](https://ollama.ai)
- **FFmpeg** (for audio processing) - [Download here](https://ffmpeg.org)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/blow-ai-voice-assistant.git
cd blow-ai-voice-assistant
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
```txt
fastapi
uvicorn[standard]
openai-whisper
soundfile
ollama
edge-tts
scipy
librosa
google-generativeai
python-dotenv
numpy
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# AI Model Settings
OLLAMA_MODEL=llama3.2:3b
DEFAULT_LLM=ollama

# Whisper Settings
WHISPER_MODEL=base
TARGET_SAMPLE_RATE=16000

# TTS Settings
TTS_VOICE=en-US-GuyNeural

# Audio Processing
MIN_AUDIO_DURATION=0.3
MAX_AUDIO_DURATION=30.0

# Google Gemini (Optional)
GEMINI_API_KEY=your_api_key_here
```

### Step 5: Install Ollama Models

```bash
# Download and run Ollama
ollama pull llama3.2:3b

# Or use other models
ollama pull llama2
ollama pull mistral
```

### Step 6: Start the Server

```bash
# Start the FastAPI backend
python server.py

# Server will run on http://localhost:8000
```

### Step 7: Open the Interface

Open `index.html` in your web browser or serve it with a simple HTTP server:

```bash
# Python HTTP Server
python -m http.server 8080

# Then visit http://localhost:8080
```

---

## 🎮 Usage

### Basic Voice Interaction

1. **Click the Microphone Button** 🎤 or press the voice button in the input area
2. **Speak Your Message** - The assistant will transcribe your speech in real-time
3. **Get AI Response** - Blow will process your request and respond with voice
4. **Continue Conversation** - Your chat history is automatically saved

### Text Input

Simply type your message in the input field and press **Enter** or click the send button.

### Switching AI Models

1. Open the **sidebar** (click the menu icon)
2. Select your preferred model:
   - **Ollama** - Fast, local, private
   - **Gemini** - Advanced, cloud-based, powerful

### Customizing Voice

1. Click **Settings** ⚙️ in the header or sidebar
2. Choose from 10+ available voices
3. Click **Test Voice** to hear a sample
4. Your preference is automatically saved

### Creating Custom Prompts

1. Open the sidebar
2. Find the **Custom Prompts** section
3. Click the **+** button
4. Enter your prompt text
5. Use it anytime with one click

---

## ⚙️ Configuration

### Available Voices

| Voice ID | Name | Accent | Gender |
|----------|------|--------|--------|
| en-US-GuyNeural | Guy | US | Male |
| en-US-JennyNeural | Jenny | US | Female |
| en-US-AriaNeural | Aria | US | Female |
| en-US-DavisNeural | Davis | US | Male |
| en-GB-RyanNeural | Ryan | UK | Male |
| en-GB-SoniaNeural | Sonia | UK | Female |
| en-AU-NatashaNeural | Natasha | AU | Female |
| en-AU-WilliamNeural | William | AU | Male |
| en-IN-NeerjaNeural | Neerja | IN | Female |
| en-IN-PrabhatNeural | Prabhat | IN | Male |

### Whisper Models

Choose based on your needs:

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39 MB | Fastest | Good |
| base | 74 MB | Fast | Better |
| small | 244 MB | Medium | Great |
| medium | 769 MB | Slow | Excellent |
| large | 1550 MB | Slowest | Best |

### Recommended Settings

**For Best Performance:**
- Whisper Model: `base` or `small`
- Ollama Model: `llama3.2:3b`
- Sample Rate: `16000`

**For Best Quality:**
- Whisper Model: `medium` or `large`
- Ollama Model: `llama2:13b` or use Gemini
- Sample Rate: `48000`

---

## 🔌 API Endpoints

### Health Check
```http
GET /health
```

### Transcribe Audio
```http
POST /transcribe
Content-Type: application/json

{
  "audio_data": "base64_encoded_audio",
  "sample_rate": 48000
}
```

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Hello, Blow!",
  "use_history": true,
  "llm_model": "ollama"
}
```

### Text-to-Speech
```http
POST /tts
Content-Type: application/json

{
  "text": "Hello, world!",
  "voice": "en-US-GuyNeural"
}
```

### Get Available Models
```http
GET /models
```

### Conversation History
```http
GET /conversation
DELETE /conversation
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  Frontend (HTML/JS)              │
│  ┌───────────┐  ┌───────────┐  ┌─────────────┐ │
│  │  Voice UI  │  │  Chat UI  │  │  Settings   │ │
│  └───────────┘  └───────────┘  └─────────────┘ │
└─────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────┐
│              FastAPI Backend Server              │
│  ┌───────────────────────────────────────────┐  │
│  │  Audio Processing Pipeline                 │  │
│  │  • Decode → Preprocess → Validate          │  │
│  └───────────────────────────────────────────┘  │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │  Whisper   │  │ Ollama/    │  │ Edge TTS │  │
│  │    STT     │  │  Gemini    │  │          │  │
│  └────────────┘  └────────────┘  └──────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Areas for Contribution

- 🌐 Multi-language support
- 🎨 UI/UX improvements
- 🔧 New AI model integrations
- 📱 Mobile app development
- 📚 Documentation enhancements
- 🐛 Bug fixes and optimizations

---

## 🐛 Troubleshooting

### Common Issues

**Problem:** Microphone not working
- **Solution:** Check browser permissions and ensure HTTPS or localhost

**Problem:** Whisper transcription fails
- **Solution:** Ensure audio is at least 1 second long and speak clearly

**Problem:** Ollama connection error
- **Solution:** Make sure Ollama is running (`ollama serve`)

**Problem:** Poor audio quality
- **Solution:** Adjust `MIN_AUDIO_DURATION` and speak closer to the microphone

**Problem:** Slow responses
- **Solution:** Use a smaller Whisper model or lighter Ollama model

### Debug Mode

Enable debug logging by modifying the server:

```python
# In server.py, add at startup
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📝 Changelog

### Version 5.0 - Latest Release
- ✨ Enhanced audio processing with multiple format support
- 🔧 Improved error handling and validation
- 🎨 Redesigned UI with modern aesthetics
- 🚀 Performance optimizations for faster responses
- 📱 Better mobile responsiveness
- 🔊 Expanded voice selection with 10+ options
- 💾 Custom prompt management system

### Version 4.0
- Added Gemini AI integration
- Implemented conversation history
- Created settings panel

### Version 3.0
- Initial voice recognition
- Basic chat functionality
- TTS integration

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Blow AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - For exceptional speech recognition
- **Ollama** - For making local LLMs accessible
- **Google Gemini** - For powerful cloud AI capabilities
- **Edge TTS** - For natural text-to-speech synthesis
- **FastAPI** - For the robust backend framework
- **The Open Source Community** - For continuous inspiration and support

---

## 📧 Contact & Support

- **GitHub Issues:** [Report a bug](https://github.com/yourusername/blow-ai-voice-assistant/issues)
- **Email:** support@blowai.example.com
- **Discord:** [Join our community](https://discord.gg/blowai)
- **Twitter:** [@BlowAI](https://twitter.com/blowai)

---

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐ on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/blow-ai-voice-assistant&type=Date)](https://star-history.com/#yourusername/blow-ai-voice-assistant&Date)

---

<div align="center">

**Made with ❤️ by the Blow AI Team**

[⬆ Back to Top](#-blow-ai---advanced-voice-assistant)

</div>
