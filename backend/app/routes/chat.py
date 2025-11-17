from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatMessage, ChatResponse
from app.agents.real_estate_agent import RealEstateAgentService
from app.config import settings
from app.models import Conversation
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the agent service
agent_service = RealEstateAgentService(settings.GEMINI_API_KEY)

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing chat message for session: {message.session_id}, language: {message.language}")
        
        if not message.message or not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Process the message through the agent service with language preference
        result = agent_service.process_message(
            db, 
            message.session_id, 
            message.message,
            message.language
        )
        
        logger.info(f"Successfully processed chat message. Response language: {result['language']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        # Return a fallback response instead of raising exception
        return {
            "response": "I apologize for the inconvenience. I'm currently experiencing technical difficulties. Please try again in a moment.",
            "language": message.language if message.language != "auto" else "english",
            "session_id": message.session_id or "unknown",
            "timestamp": "2024-01-01T00:00:00Z"
        }

@router.get("/conversations/{session_id}")
async def get_conversation_history(session_id: str, db: Session = Depends(get_db)):
    try:
        conversations = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.created_at.asc()).all()
        
        return conversations
        
    except Exception as e:
        logger.error(f"Error fetching conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching conversation history")