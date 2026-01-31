"""
============================================
SAHAYAK AI - Main Application
============================================

📌 WHAT IS THIS FILE?
The main entry point for the FastAPI backend.
This sets up the application, middleware, and routes.

🎓 LEARNING POINTS:
1. FastAPI app is created here
2. Lifespan events handle startup/shutdown
3. CORS allows frontend to call the API
4. All routers are included here

To run:
    cd backend
    uvicorn app.main:app --reload --port 8000

Then visit: http://localhost:8000/docs
============================================
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.mongodb import connect_to_mongodb, close_mongodb_connection
from app.api.v1.router import api_router
from app.services.gemini_service import gemini_service
from app.services.redis_cache import redis_cache


# ============================================
# Lifespan Events
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    🎓 LEARNING POINT:
    Lifespan is the modern way to handle startup/shutdown in FastAPI.
    - Code before `yield` runs at startup
    - Code after `yield` runs at shutdown
    """
    # Startup
    print("🚀 Starting SAHAYAK AI Backend...")
    print(f"📌 Environment: {settings.app_env}")
    print(f"📌 Debug Mode: {settings.debug}")
    
    # Connect to MongoDB
    await connect_to_mongodb()
    
    # Check Gemini
    if gemini_service.is_available():
        print("✅ Gemini AI is ready")
    else:
        print("⚠️ Gemini AI not configured - using fallback responses")
    
    # Connect to Redis cache
    await redis_cache.connect()
    
    print("✅ SAHAYAK AI Backend is ready!")
    print("📚 API Docs: http://localhost:8000/docs")
    
    yield  # Application runs here
    
    # Shutdown
    print("\n🔌 Shutting down SAHAYAK AI Backend...")
    await redis_cache.disconnect()
    await close_mongodb_connection()
    print("✅ Shutdown complete")


# ============================================
# Create FastAPI Application
# ============================================

app = FastAPI(
    title="SAHAYAK AI",
    description="""
# 🎓 SAHAYAK AI - Just In Time Classroom Coaching Engine

A real-time AI-powered platform that provides instant pedagogical rescue 
to government school teachers during live classroom breakdowns.

## 🆘 Core Features

- **Voice/Text SOS** - Teachers describe their classroom problem
- **AI Playbook Generation** - Instant teaching rescue strategies
- **Context Extraction** - Automatic detection of subject, grade, topic
- **Classroom Memory** - Learning from past interactions
- **Dashboards** - Analytics for teachers, CRPs, and DIETs

## 🚀 Quick Start

1. **Register** a teacher account via `/api/v1/auth/register`
2. **Login** to get your access token
3. **Submit SOS** via `/api/v1/sos/` with your classroom problem
4. **Get Playbook** - Instant AI-generated teaching strategies!

## 📖 Try the Demo

Use the `/api/v1/sos/quick` endpoint for anonymous testing.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================
# CORS Middleware
# ============================================

# Allow all origins for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)


# ============================================
# Include Routers
# ============================================

app.include_router(api_router)


# ============================================
# Health & Root Endpoints
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "SAHAYAK AI",
        "tagline": "Just In Time Classroom Coaching Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the status of all system components.
    Good for monitoring and load balancer checks.
    """
    from app.db.mongodb import get_client
    
    # Check MongoDB connection
    mongodb_status = False
    try:
        client = get_client()
        if client:
            await client.admin.command('ping')
            mongodb_status = True
    except Exception:
        pass
    
    return {
        "status": "healthy" if mongodb_status else "degraded",
        "app_name": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
        "components": {
            "mongodb": "connected" if mongodb_status else "disconnected",
            "gemini_ai": "available" if gemini_service.is_available() else "fallback_mode",
            "redis_cache": "connected" if redis_cache.is_available() else "disabled",
        }
    }


@app.get("/cache/stats", tags=["Health"])
async def get_cache_stats():
    """
    Get Redis cache statistics.
    
    Returns cache hit/miss rates, connection status, and key counts.
    Useful for monitoring cache effectiveness.
    """
    return await redis_cache.get_cache_stats()


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler."""
    print(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error. Please try again.",
        }
    )


# ============================================
# For Development
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
