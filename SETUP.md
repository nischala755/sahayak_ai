# 🎓 SAHAYAK AI - Setup Instructions for Judges

> **Real-time AI Classroom Coaching Engine for Government School Teachers**

---

## 🌐 Deployed Version (Recommended for Judges)

| Component | URL |
|-----------|-----|
| **Frontend** | https://sahayak-ai.vercel.app |
| **Backend API** | https://sahayak-ai-backend.onrender.com |
| **API Documentation** | https://sahayak-ai-backend.onrender.com/docs |

### Quick Demo (No Login Required)
1. Visit the frontend URL
2. Click **"Try Quick SOS"** or go to `/sos`
3. Enter any classroom problem (e.g., "Students don't understand fractions")
4. Click **"Get AI Rescue Playbook"**
5. View the AI-generated teaching strategy!

---

## 💻 Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)
- Google Gemini API Key ([Get free key](https://aistudio.google.com/))

### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/nischala755/sahayak_ai.git
cd sahayak_ai

# 2. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
# Edit .env with your credentials:
#   - MONGODB_URL=mongodb://localhost:27017
#   - GEMINI_API_KEY=your-key-here
#   - SECRET_KEY=any-random-string

# 5. Start backend server
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access Points
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

---

## 🔑 Required API Keys

| Service | Purpose | Get From |
|---------|---------|----------|
| Gemini API | AI playbook generation | [aistudio.google.com](https://aistudio.google.com/) |
| MongoDB | Database (Atlas or local) | [mongodb.com/atlas](https://mongodb.com/atlas) |

---

## 📁 Project Structure

```
sahayak_ai/
├── backend/               # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py       # Entry point
│   │   ├── core/         # Config, Security, Auth
│   │   ├── db/           # MongoDB models
│   │   ├── services/     # AI & Business logic
│   │   └── api/v1/       # REST endpoints
│   └── requirements.txt
│
├── frontend/              # React Vite Frontend
│   ├── src/
│   │   ├── pages/        # UI pages
│   │   ├── components/   # Reusable components
│   │   └── api/          # API client
│   └── package.json
│
└── README.md
```

---

## ✨ Key Features to Evaluate

1. **Voice/Text SOS Input** - `/sos` page supports both
2. **AI Playbook Generation** - Uses Google Gemini 2.5 Flash
3. **Context Auto-Detection** - Extracts subject, grade, topic
4. **Instant Response** - Playbooks generated in 3-5 seconds
5. **Teacher Dashboard** - Stats and history (requires login)
6. **Role-Based Access** - Teacher, CRP, DIET roles

---

## 🧪 Test the API Directly

```bash
# Health check
curl https://sahayak-ai-backend.onrender.com/health

# Quick SOS (no auth needed)
curl -X POST "https://sahayak-ai-backend.onrender.com/api/v1/sos/quick?raw_input=Students%20dont%20understand%20fractions"
```

---

## 📞 Support

- **GitHub**: https://github.com/nischala755/sahayak_ai
- **Issues**: Create an issue on the repository

---

> *"Every Teacher Deserves a Coach. Every Classroom Deserves Success."*
