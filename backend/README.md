# SAHAYAK AI - Backend

> 🎓 Just In Time Classroom Coaching Engine - A real-time AI platform for pedagogical rescue

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and set your Gemini API key:
```
GEMINI_API_KEY=your-api-key-here
```

### 3. Start MongoDB

Make sure MongoDB is running locally:
```bash
# Windows (if installed as service, it should auto-start)
# Or start manually:
mongod
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Open API Documentation

Visit: **http://localhost:8000/docs**

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # 🚀 FastAPI application
│   ├── core/
│   │   ├── config.py        # ⚙️ Environment settings
│   │   ├── security.py      # 🔐 JWT authentication
│   │   └── dependencies.py  # 🔧 FastAPI dependencies
│   ├── db/
│   │   ├── mongodb.py       # 🗄️ Database connection
│   │   └── models/          # 📋 Beanie document models
│   ├── services/
│   │   ├── gemini_service.py    # 🤖 Gemini AI integration
│   │   ├── context_engine.py    # 🔍 Context extraction
│   │   └── pedagogy_engine.py   # 📚 Playbook generation
│   ├── api/v1/
│   │   ├── auth.py          # 👤 Authentication endpoints
│   │   ├── sos.py           # 🆘 SOS/Playbook endpoints
│   │   └── dashboard.py     # 📊 Analytics endpoints
│   └── schemas/
│       └── schemas.py       # 📝 Pydantic schemas
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔌 API Endpoints

### 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get token |
| GET | `/api/v1/auth/me` | Get current user |

### 🆘 SOS - Classroom Emergency
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sos/` | Submit SOS and get playbook |
| POST | `/api/v1/sos/quick` | Quick SOS (no auth needed) |
| GET | `/api/v1/sos/` | Get your SOS history |
| GET | `/api/v1/sos/{id}` | Get specific SOS + playbook |
| POST | `/api/v1/sos/{id}/feedback` | Submit feedback |

### 📊 Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/teacher` | Teacher dashboard |
| GET | `/api/v1/dashboard/crp` | CRP analytics (requires CRP role) |
| GET | `/api/v1/dashboard/diet` | DIET analytics (requires DIET role) |
| GET | `/api/v1/dashboard/overview` | Public system stats |

---

## 🧪 Testing the API

### Quick Test (No Auth Needed)

Use the `/api/v1/sos/quick` endpoint:

```bash
curl -X POST "http://localhost:8000/api/v1/sos/quick?raw_input=Students%20in%20my%20class%205%20are%20not%20understanding%20fractions"
```

### With Authentication

1. Register:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"teacher@school.gov.in","password":"pass123","name":"Test Teacher"}'
```

2. Use the returned token for authenticated requests.

---

## 🎓 Technology Learning Notes

### Why FastAPI?
- Automatic OpenAPI documentation
- Async support for high performance
- Type hints for validation
- Dependency injection system

### Why MongoDB + Beanie?
- Flexible document structure
- Async operations
- Python class-based models

### Why Gemini AI?
- Advanced reasoning capabilities
- Multilingual support (Hindi, Kannada, etc.)
- Cost-effective for educational use

---

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Database name | `sahayak_ai` |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `SECRET_KEY` | JWT signing key | Change in production! |
| `CORS_ORIGINS` | Allowed frontend URLs | `["http://localhost:3000"]` |

---

## 🐛 Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running: `mongod`
- Check the connection string in `.env`

**Gemini AI Not Working:**
- Verify your API key is correct
- The system will use fallback responses until configured

**CORS Errors:**
- Add your frontend URL to `CORS_ORIGINS` in `.env`

---

## 📄 License

MIT License - Built for Shikshalokam
