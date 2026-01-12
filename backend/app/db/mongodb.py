"""
============================================
SAHAYAK AI - MongoDB Connection
============================================

📌 WHAT IS THIS FILE?
Manages the MongoDB database connection using Motor (async driver)
and Beanie (ODM - Object Document Mapper).

🎓 LEARNING POINTS:
1. Motor: Async MongoDB driver - doesn't block while waiting for DB
2. Beanie: Maps Python classes to MongoDB documents (like SQLAlchemy for SQL)
3. Connection Pooling: Reuses connections for efficiency

Why Async?
- Handles many concurrent requests without waiting
- Perfect for I/O-bound operations like database calls
- Scales better for real-time applications
============================================
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional

from app.core.config import settings

# --------------------------------------------
# Database Client
# --------------------------------------------
# We store the client globally for connection reuse
_client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongodb():
    """
    Connect to MongoDB and initialize Beanie ODM.
    
    This function should be called when the application starts.
    It creates the database connection and registers all document models.
    
    🎓 LEARNING POINT:
    Motor uses connection pooling by default.
    This means it maintains a pool of connections and reuses them,
    which is more efficient than creating a new connection for each request.
    """
    global _client
    
    print(f"🔗 Connecting to MongoDB at {settings.mongodb_url}...")
    
    # Create the Motor client
    _client = AsyncIOMotorClient(
        settings.mongodb_url,
        maxPoolSize=10,  # Maximum connections in the pool
        minPoolSize=1,   # Minimum connections to keep open
    )
    
    # Get the database
    database = _client[settings.mongodb_db_name]
    
    # Import all document models
    # These are registered with Beanie so it knows how to map them
    from app.db.models.user import User
    from app.db.models.sos_request import SOSRequest
    from app.db.models.playbook import Playbook
    from app.db.models.memory import ClassroomMemory
    
    # Initialize Beanie with the database and document models
    await init_beanie(
        database=database,
        document_models=[
            User,
            SOSRequest,
            Playbook,
            ClassroomMemory,
        ]
    )
    
    print(f"✅ Connected to MongoDB database: {settings.mongodb_db_name}")


async def close_mongodb_connection():
    """
    Close the MongoDB connection.
    
    This should be called when the application shuts down
    to properly release database resources.
    """
    global _client
    
    if _client is not None:
        print("🔌 Closing MongoDB connection...")
        _client.close()
        _client = None
        print("✅ MongoDB connection closed")


def get_database():
    """
    Get the current database instance.
    
    Returns:
        Database: The MongoDB database object
    
    Raises:
        RuntimeError: If database is not connected
    """
    global _client
    
    if _client is None:
        raise RuntimeError(
            "Database not connected. Call connect_to_mongodb() first."
        )
    
    return _client[settings.mongodb_db_name]


def get_client():
    """
    Get the MongoDB client (for advanced operations).
    
    Returns:
        AsyncIOMotorClient: The Motor client
    """
    return _client
