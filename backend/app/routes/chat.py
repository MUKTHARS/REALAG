from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatMessage, ChatResponse, ChatSessionResponse, ChatHistoryResponse
from app.agents.real_estate_agent import RealEstateAgentService
from app.config import settings
from app.models import Conversation, ChatSession
import logging
import uuid
from datetime import datetime  # Added missing import

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the agent service
agent_service = RealEstateAgentService(settings.GEMINI_API_KEY)

def generate_chat_title(message: str, language: str) -> str:
    """Generate a chat title from the first message"""
    if not message:
        return "New Chat"
    
    # Truncate and clean the message for title
    words = message.split()[:8]  # Take first 8 words
    title = ' '.join(words)
    
    # Remove special characters and truncate
    title = ''.join(char for char in title if char.isalnum() or char.isspace())
    
    if len(title) > 50:
        title = title[:47] + "..."
    
    return title.strip() or "New Chat"

def get_or_create_chat_session(db: Session, session_id: str, message: str, language: str):
    """Get existing chat session or create new one"""
    chat_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    
    if not chat_session:
        # Create new chat session
        title = generate_chat_title(message, language)
        chat_session = ChatSession(
            session_id=session_id,
            title=title,
            language=language,
            message_count=1,
            is_active=True
        )
        db.add(chat_session)
    else:
        # Update existing session
        chat_session.message_count += 1
        chat_session.updated_at = datetime.utcnow()
        chat_session.is_active = True
    
    db.commit()
    db.refresh(chat_session)
    return chat_session

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing chat message for session: {message.session_id}, language: {message.language}")
        
        if not message.message or not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate session ID if not provided
        if not message.session_id:
            message.session_id = str(uuid.uuid4())
        
        # Create or update chat session for sidebar
        chat_session = get_or_create_chat_session(db, message.session_id, message.message, message.language)
        
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

# NEW: Endpoints for chat history sidebar
@router.get("/chat-sessions", response_model=ChatHistoryResponse)
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    try:
        # Get active chat sessions ordered by most recent
        sessions = db.query(ChatSession).filter(
            ChatSession.is_active == True
        ).order_by(
            ChatSession.updated_at.desc()
        ).offset(skip).limit(limit).all()
        
        total_count = db.query(ChatSession).filter(
            ChatSession.is_active == True
        ).count()
        
        return {
            "sessions": sessions,
            "total_count": total_count
        }
        
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching chat sessions")

@router.get("/chat-sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(session_id: str, db: Session = Depends(get_db)):
    try:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching chat session")

@router.delete("/chat-sessions/{session_id}")
async def delete_chat_session(session_id: str, db: Session = Depends(get_db)):
    try:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Soft delete by marking as inactive
        session.is_active = False
        db.commit()
        
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting chat session")

@router.put("/chat-sessions/{session_id}/title")
async def update_chat_session_title(
    session_id: str, 
    title: str,
    db: Session = Depends(get_db)
):
    try:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        
        session.title = title.strip()
        db.commit()
        
        return {"message": "Chat session title updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chat session title: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating chat session title")