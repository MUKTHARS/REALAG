from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, properties
from app.database import engine
from app.models import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables with better error handling
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")
    # Try to get more detailed error information
    import traceback
    logger.error(traceback.format_exc())

app = FastAPI(
    title="Real Estate Agent API",
    version="1.0.0",
    description="Multilingual Real Estate Agent with Gemini AI"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1")
app.include_router(properties.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Real Estate Agent API", 
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}