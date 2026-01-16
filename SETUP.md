# 🎓 SAHAYAK AI - Quick Setup Guide

> **Real-time AI Classroom Coaching Engine for Government School Teachers**

---

## 🌐 Live Demo (Recommended)

| Component | URL |
|-----------|-----|
| **Frontend** | https://sahayak-ai-xi.vercel.app |
| **Backend API** | https://sahayak-ai-p720.onrender.com |
| **Quick SOS** | https://sahayak-ai-xi.vercel.app/sos |
| **API Docs** | https://sahayak-ai-p720.onrender.com/docs |

### Try It Now (No Login Required)
1. Go to **https://sahayak-ai-xi.vercel.app/sos**
2. Select language: **English** | **हिंदी** | **ಕನ್ನಡ**
3. Type: "Students don't understand fractions"
4. Click **"Get AI Rescue Playbook"**
5. View instant teaching strategy with YouTube links!

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎤 **Voice/Text Input** | Speak or type classroom problems |
| 🤖 **AI Playbooks** | Instant rescue strategies via Gemini |
| 🌐 **Multi-Language** | English, Hindi, Kannada support |
| 📺 **YouTube Links** | Educational video recommendations |
| 📚 **NCERT References** | Chapter & page references |
| 💡 **Teaching Tips** | Quick actionable tips |
| 📱 **WhatsApp Share** | Share playbooks instantly |
| 🔊 **Voice Readout** | Text-to-speech playback |
| 🖨️ **Print** | Print-friendly format |

---

## 💻 Local Setup

### Prerequisites
- Python 3.11+ | Node.js 18+ | MongoDB | [Gemini API Key](https://aistudio.google.com/)

### Backend
```bash
git clone https://github.com/nischala755/sahayak_ai.git
cd sahayak_ai/backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
# Create .env with: MONGODB_URL, GEMINI_API_KEY, SECRET_KEY
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install && npm run dev
```

### Access
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Docs | http://localhost:8000/docs |

---

## 🧪 Test API

```bash
# Health check
curl https://sahayak-ai-p720.onrender.com/health

# Generate playbook
curl -X POST "https://sahayak-ai-p720.onrender.com/api/v1/sos/quick?raw_input=Students%20dont%20understand%20fractions&language=Hindi"
```

---

## 📁 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI, Python, Beanie ODM |
| Database | MongoDB Atlas |
| AI | Google Gemini 2.5 Flash |
| Deployment | Vercel + Render |

---

> *"Every Teacher Deserves a Coach. Every Classroom Deserves Success."*

**GitHub**: https://github.com/nischala755/sahayak_ai
