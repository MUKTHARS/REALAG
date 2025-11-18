from .multilingual import MultilingualRealEstateAgent
from sqlalchemy.orm import Session
from app.models import Property, UserPreference, Conversation
import json
from datetime import datetime

class RealEstateAgentService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        self.agent = MultilingualRealEstateAgent(api_key)
    
    def process_message(self, db: Session, session_id: str, message: str, requested_language: str = "auto", user_id: int = None):
        try:
            # Get available properties from database
            properties = self.get_available_properties(db)
            
            # Generate response using Gemini with requested language
            result = self.agent.generate_response(
                session_id, 
                message, 
                properties,
                requested_language
            )
            
            # Save conversation with user_id
            conversation = Conversation(
                session_id=session_id,
                user_id=user_id,  # Link to specific user
                user_message=message,
                agent_response=result["response"],
                language=result["language"],
                conversation_data={"preferences": result.get("preferences", {})}
            )
            db.add(conversation)
            
            # Update user preferences if new preferences detected
            if result.get("preferences"):
                self.update_user_preferences(db, session_id, result["preferences"], result["language"])
            
            db.commit()
            
            return {
                "response": result["response"],
                "language": result["language"],
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error in process_message: {e}")
            # Return a fallback response
            return {
                "response": "I'm experiencing technical difficulties. Please try again in a moment.",
                "language": requested_language if requested_language != "auto" else "english",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_available_properties(self, db: Session):
        try:
            properties = db.query(Property).filter(
                Property.available_from <= datetime.utcnow()
            ).all()
            
            return [
                {
                    "id": prop.id,
                    "title": prop.title or "No Title",
                    "description": prop.description or "",
                    "price": float(prop.price) if prop.price else 0,
                    "location": prop.location or "Unknown Location",
                    "property_type": prop.property_type or "Unknown Type",
                    "bedrooms": prop.bedrooms or 0,
                    "bathrooms": prop.bathrooms or 0,
                    "area_sqft": float(prop.area_sqft) if prop.area_sqft else 0,
                    "amenities": prop.amenities or [],
                    "images": prop.images or []
                }
                for prop in properties
            ]
        except Exception as e:
            print(f"Error getting properties: {e}")
            return []
    
    def update_user_preferences(self, db: Session, session_id: str, preferences: dict, language: str):
        try:
            # Find existing preferences or create new
            existing = db.query(UserPreference).filter(UserPreference.session_id == session_id).first()
            
            if existing:
                # Update existing preferences
                for key, value in preferences.items():
                    if value is not None:
                        setattr(existing, key, value)
            else:
                # Create new preferences
                new_prefs = UserPreference(
                    session_id=session_id,
                    language=language,
                    **{k: v for k, v in preferences.items() if v is not None}
                )
                db.add(new_prefs)
                
        except Exception as e:
            print(f"Error updating preferences: {e}")