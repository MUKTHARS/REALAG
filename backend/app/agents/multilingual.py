import google.generativeai as genai
import json
import re
from datetime import datetime

class MultilingualRealEstateAgent:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is required")
        
        # Configure for Google AI Studio
        genai.configure(api_key=api_key)
        
        # For Google AI Studio, use the correct model name
        try:
            # List available models to see what's accessible
            available_models = genai.list_models()
            print("Available models:")
            gemini_models = []
            for model in available_models:
                if 'gemini' in model.name.lower() and 'generateContent' in model.supported_generation_methods:
                    gemini_models.append(model.name)
                    print(f"- {model.name} (supports generateContent: True)")
            
            if gemini_models:
                # Use a more reliable model - prefer flash models for speed
                model_name = None
                for model in gemini_models:
                    if 'flash' in model.lower():
                        model_name = model
                        break
                if not model_name and gemini_models:
                    model_name = gemini_models[0]
                
                self.model = genai.GenerativeModel(model_name)
                print(f"Successfully initialized model: {model_name}")
            else:
                # Fallback to common model names
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    print("Using gemini-1.5-flash")
                except:
                    try:
                        self.model = genai.GenerativeModel('gemini-1.0-pro')
                        print("Using gemini-1.0-pro")
                    except:
                        self.model = genai.GenerativeModel('models/gemini-pro')
                        print("Using models/gemini-pro")
                        
        except Exception as e:
            print(f"Error initializing model: {e}")
            # Final fallback
            self.model = genai.GenerativeModel('gemini-pro')
        
        self.conversation_histories = {}
        
    def detect_language(self, message):
        """Detect language of the message with fallback"""
        if not message or not message.strip():
            return "english"
            
        try:
            # Simple rule-based language detection as fallback
            arabic_chars = set('ء-ي')
            tamil_chars = set('அ-ஹ')
            
            if any(char in arabic_chars for char in message):
                return "arabic"
            elif any(char in tamil_chars for char in message):
                return "tamil"
            else:
                return "english"
                
        except Exception as e:
            print(f"Language detection fallback error: {e}")
            return "english"
    
    def get_conversation_history(self, session_id):
        if session_id not in self.conversation_histories:
            self.conversation_histories[session_id] = []
        return self.conversation_histories[session_id]
    
    def extract_preferences(self, message, language):
        """Simple rule-based preference extraction as fallback"""
        preferences = {
            "budget_min": None,
            "budget_max": None,
            "preferred_locations": [],
            "property_types": [],
            "bedrooms": None,
            "amenities": []
        }
        
        message_lower = message.lower()
        
        # Extract budget
        if 'budget' in message_lower or 'aed' in message_lower or 'price' in message_lower:
            numbers = re.findall(r'\d+', message)
            if numbers:
                if len(numbers) >= 2:
                    preferences["budget_min"] = int(numbers[0]) * 1000
                    preferences["budget_max"] = int(numbers[1]) * 1000
                else:
                    preferences["budget_min"] = int(numbers[0]) * 1000
        
        # Extract locations
        locations = ['downtown', 'palm jumeirah', 'deira', 'business bay', 'dubai marina', 'jumeirah']
        for location in locations:
            if location in message_lower:
                preferences["preferred_locations"].append(location)
        
        # Extract property types
        property_types = ['apartment', 'villa', 'studio', 'penthouse', 'house']
        for prop_type in property_types:
            if prop_type in message_lower:
                preferences["property_types"].append(prop_type)
        
        # Extract bedrooms
        bedroom_keywords = ['bedroom', 'bed', 'bhk']
        for keyword in bedroom_keywords:
            if keyword in message_lower:
                numbers = re.findall(r'\d+', message_lower)
                if numbers:
                    preferences["bedrooms"] = int(numbers[0])
        
        # Extract amenities
        amenities = ['pool', 'gym', 'parking', 'security', 'beach', 'garden']
        for amenity in amenities:
            if amenity in message_lower:
                preferences["amenities"].append(amenity)
        
        return preferences
    
    def generate_response(self, session_id, message, available_properties=None):
        try:
            language = self.detect_language(message)
            history = self.get_conversation_history(session_id)
            
            # Extract user preferences
            preferences = self.extract_preferences(message, language)
            
            # Prepare properties context
            properties_context = "No properties available"
            if available_properties and len(available_properties) > 0:
                properties_context = "\n".join([
                    f"Property {i+1}: {p.get('title', 'No title')} in {p.get('location', 'Unknown location')}, "
                    f"{p.get('bedrooms', 'N/A')}BR, AED {p.get('price', 'N/A')}, {p.get('property_type', 'Unknown type')}"
                    for i, p in enumerate(available_properties[:5])
                ])
            
            # Prepare conversation history
            history_text = "\n".join([f"User: {h['user']}\nAssistant: {h['assistant']}" for h in history[-5:]])
            
            # Generate response using Gemini with better prompt
            prompt = f"""
            You are a professional real estate agent in Dubai. You speak {language} fluently.
            Your role is to help users find properties, answer real estate questions, and provide market insights.
            
            Current available properties context:
            {properties_context}
            
            Conversation History (last 5 messages):
            {history_text if history_text else "No previous conversation"}
            
            User's current message: {message}
            
            Instructions:
            - Respond in {language} language
            - Be helpful, professional, and provide relevant information about Dubai real estate
            - If the user is looking for properties, suggest relevant ones from the available properties
            - If no properties match exactly, suggest similar alternatives
            - Ask clarifying questions if needed
            - Provide market insights when relevant
            - Keep responses conversational and engaging
            
            Assistant: """
            
            # Generate content with safety settings disabled to avoid blocking
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Get the response text safely
            if response and hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = f"I understand you're looking for real estate in Dubai. I'd be happy to help you find properties. Could you tell me more about your requirements like budget, preferred locations, and property type?"
            
            # Update conversation history
            history.append({
                "user": message,
                "assistant": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only last 10 messages
            if len(history) > 10:
                history = history[-10:]
            
            self.conversation_histories[session_id] = history
            
            return {
                "response": response_text,
                "language": language,
                "preferences": preferences,
                "session_id": session_id
            }
            
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            # More detailed error logging
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            
            # Fallback response
            fallback_responses = {
                "english": "Welcome to Dubai Real Estate! I can help you find properties in Dubai. Please tell me about your requirements - budget, preferred locations, and property type.",
                "arabic": "مرحباً بك في دبي للعقارات! يمكنني مساعدتك في العثور على عقارات في دبي. يرجى إخباري بمتطلباتك - الميزانية والمواقع المفضلة ونوع العقار.",
                "tamil": "டுபாய் ரியல் எஸ்டேட்டுக்கு வரவேற்கிறோம்! டுபாயில் உள்ள வீடுகளை கண்டுபிடிக்க நான் உதவ முடியும். தயவு செய்து உங்கள் தேவைகளைச் சொல்லுங்கள் - பட்ஜெட், விருப்பமான இடங்கள் மற்றும் வீடு வகை."
            }
            
            return {
                "response": fallback_responses.get(language, fallback_responses["english"]),
                "language": language,
                "preferences": {},
                "session_id": session_id
            }