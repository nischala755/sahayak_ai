<p align="center">
  <img src="https://img.shields.io/badge/SAHAYAK-AI-blue?style=for-the-badge&logo=openai&logoColor=white" alt="SAHAYAK AI"/>
</p>

<h1 align="center">🎓 SAHAYAK AI</h1>
<h3 align="center">Just In Time Classroom Coaching Engine</h3>

<p align="center">
  <em>Real-time AI-powered pedagogical rescue for government school teachers during live classroom breakdowns</em>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-deployment">Deployment</a> •
  <a href="#-api-documentation">API Docs</a> •
  <a href="#-architecture">Architecture</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white" alt="MongoDB"/>
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=flat&logo=google&logoColor=white" alt="Gemini AI"/>
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white" alt="Tailwind"/>
</p>

---

## 🌟 Overview

**SAHAYAK AI** is a comprehensive real-time classroom coaching platform that transforms how government school teachers handle challenging classroom situations. By leveraging advanced AI (Google Gemini 2.5 Flash) and seamless voice/text input, SAHAYAK eliminates the isolation teachers face during live teaching breakdowns.

SAHAYAK operates through a sophisticated multi-layer processing system that:
- Ingests teacher's voice/text descriptions of classroom problems
- Extracts context (subject, grade, topic, urgency)
- Generates instant AI-powered teaching rescue playbooks
- Tracks patterns for personalized recommendations
- Provides dashboards for teachers, CRPs, and DIETs

> *"Every Teacher Deserves a Coach. Every Classroom Deserves Success."*

---

## ✨ Features

### 🆘 Core SOS Features

| Feature | Description |
|---------|-------------|
| **Voice SOS Input** | Speak your classroom problem using Web Speech API |
| **Text SOS Input** | Type detailed problem descriptions |
| **Multi-Language Support** | English, Hindi, Kannada, and regional languages |
| **Context Auto-Detection** | Automatically identifies subject, grade, and topic |
| **Urgency Classification** | Detects high/medium/low urgency situations |

### 🤖 AI-Powered Playbook Generation

| Feature | Description |
|---------|-------------|
| **Gemini 2.5 Flash Integration** | Latest Google AI for pedagogical coaching |
| **Instant Playbooks** | Generate rescue strategies in 3-5 seconds |
| **Immediate Actions** | "Do RIGHT NOW" steps for crisis moments |
| **Recovery Steps** | Detailed step-by-step teaching recovery |
| **Alternative Strategies** | Backup approaches if primary fails |
| **Success Indicators** | Know when your strategy is working |
| **Cultural Context** | India-specific examples and approaches |

### 📊 Context Extraction Engine

| Feature | Description |
|---------|-------------|
| **Subject Detection** | Math, Science, English, Hindi, Social Studies, EVS |
| **Grade Recognition** | Classes 1-10 identification |
| **Topic Extraction** | Specific topic identification from descriptions |
| **Issue Classification** | Concept confusion, discipline, engagement, etc. |
| **Student Count Detection** | Class size understanding |

### 🧠 Classroom Memory System

| Feature | Description |
|---------|-------------|
| **Pattern Detection** | Identifies recurring classroom issues |
| **Successful Strategies** | Tracks what worked for personalization |
| **Subject Analytics** | Subject-wise issue distribution |
| **Time Patterns** | Peak problem hours identification |
| **Improvement Tracking** | Teacher growth over time |

### 👥 Role-Based Dashboards

| Role | Features |
|------|----------|
| **Teacher Dashboard** | Personal stats, recent SOS, quick actions |
| **CRP Dashboard** | Cluster-wide analytics, teacher support needs |
| **DIET Dashboard** | District-level patterns, resource allocation |

### 🔐 Security & Authentication

| Feature | Description |
|---------|-------------|
| **JWT Authentication** | Secure token-based auth |
| **Role-Based Access** | Teacher, CRP, DIET roles |
| **Password Hashing** | BCrypt encryption |
| **CORS Protection** | Configured cross-origin security |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **MongoDB** (local or Atlas)
- **Google Gemini API Key**

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/nischala755/sahayak_ai.git
cd sahayak_ai

# 2. Navigate to backend
cd backend

# 3. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 6. Start MongoDB (if local)
# Make sure MongoDB is running on localhost:27017

# 7. Start the backend server
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# 1. Open new terminal, navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

### Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/docs |
| **Quick SOS Demo** | http://localhost:5173/sos |

---

## 📝 Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# Application
APP_NAME=SAHAYAK AI
APP_ENV=development
DEBUG=true
API_VERSION=v1

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=sahayak_ai

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key-here

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy and paste into your `.env` file

---

## 🏗️ Architecture

```
sahayak_ai/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── core/              # Configuration & security
│   │   │   ├── config.py      # Environment settings
│   │   │   ├── security.py    # JWT & password hashing
│   │   │   └── dependencies.py # Auth middleware
│   │   ├── db/                # Database layer
│   │   │   ├── mongodb.py     # MongoDB connection
│   │   │   └── models/        # Beanie document models
│   │   │       ├── user.py
│   │   │       ├── sos_request.py
│   │   │       ├── playbook.py
│   │   │       └── memory.py
│   │   ├── services/          # Business logic
│   │   │   ├── gemini_service.py    # AI integration
│   │   │   ├── context_engine.py    # Context extraction
│   │   │   └── pedagogy_engine.py   # Playbook generation
│   │   ├── api/v1/            # API endpoints
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── sos.py         # SOS requests
│   │   │   └── dashboard.py   # Analytics
│   │   └── schemas/           # Pydantic schemas
│   ├── requirements.txt
│   └── .env
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.jsx            # Main app with routing
│   │   ├── api/client.js      # Axios API client
│   │   ├── components/        # Reusable components
│   │   │   └── layout/
│   │   │       └── DashboardLayout.jsx
│   │   └── pages/             # Application pages
│   │       ├── Landing.jsx
│   │       ├── Login.jsx
│   │       ├── Register.jsx
│   │       ├── Dashboard.jsx
│   │       ├── SOSPage.jsx
│   │       └── History.jsx
│   ├── tailwind.config.js
│   └── package.json
│
└── .gitignore
```

---

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |
| GET | `/api/v1/auth/me` | Get current user profile |

### SOS Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sos/` | Submit SOS request (authenticated) |
| POST | `/api/v1/sos/quick` | Quick SOS (anonymous demo) |
| GET | `/api/v1/sos/` | Get SOS history |
| GET | `/api/v1/sos/{id}` | Get SOS with playbook |
| POST | `/api/v1/sos/{id}/feedback` | Submit feedback |

### Dashboard Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/teacher` | Teacher dashboard data |
| GET | `/api/v1/dashboard/crp` | CRP analytics (CRP/DIET only) |
| GET | `/api/v1/dashboard/diet` | District analytics (DIET only) |
| GET | `/api/v1/dashboard/overview` | Public stats |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health status |
| GET | `/` | API information |

---

## 🌐 Deployment

### Backend Deployment (Render)

1. **Create Render Account**: Go to [render.com](https://render.com)

2. **Create New Web Service**:
   - Connect your GitHub repository
   - Select the `backend` folder as root directory

3. **Configure Build Settings**:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**:
   - `MONGODB_URL`: Your MongoDB Atlas connection string
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `SECRET_KEY`: A secure random string
   - `CORS_ORIGINS`: Your frontend URL

5. **Deploy**: Click "Create Web Service"

### Frontend Deployment (Vercel)

1. **Create Vercel Account**: Go to [vercel.com](https://vercel.com)

2. **Import Project**:
   - Connect your GitHub repository
   - Select the `frontend` folder as root directory

3. **Configure Build Settings**:
   ```
   Framework Preset: Vite
   Build Command: npm run build
   Output Directory: dist
   ```

4. **Add Environment Variables**:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

5. **Deploy**: Click "Deploy"

### MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free cluster
3. Create a database user
4. Whitelist IP addresses (0.0.0.0/0 for development)
5. Get connection string and add to environment variables

---

## 🧪 Testing

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Quick SOS (no auth required)
curl -X POST "http://localhost:8000/api/v1/sos/quick?raw_input=Students%20dont%20understand%20fractions"
```

### Run in Browser

1. Open http://localhost:5173
2. Click "Try Quick SOS" or navigate to `/sos`
3. Type or speak your classroom problem
4. View the AI-generated playbook

---

## 🤝 Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19, Vite, Tailwind CSS, Framer Motion |
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **Database** | MongoDB, Beanie ODM, Motor |
| **AI** | Google Gemini 2.5 Flash |
| **Auth** | JWT, BCrypt, Python-Jose |
| **HTTP** | Axios, HTTPX |

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Google Gemini** for powerful AI capabilities
- **FastAPI** for the excellent Python framework
- **React** and **Tailwind CSS** for the beautiful UI
- **MongoDB** for flexible document storage

---

<p align="center">
  <strong>"Every Teacher Deserves a Coach. Every Classroom Deserves Success."</strong>
</p>

<p align="center">
  Made with ❤️ for Government School Teachers of India
</p>

<p align="center">
  <a href="https://github.com/nischala755/sahayak_ai">⭐ Star this repo</a> •
  <a href="https://github.com/nischala755/sahayak_ai/issues">🐛 Report Bug</a> •
  <a href="https://github.com/nischala755/sahayak_ai/issues">✨ Request Feature</a>
</p>
