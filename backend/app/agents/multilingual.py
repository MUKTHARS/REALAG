import google.generativeai as genai
import json
import re
import time
from datetime import datetime
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage

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
        
        # LangChain memory for each session
        self.memories = {}
        
        # Define the chat prompt template with enhanced formatting instructions
        self.system_template = """You are a professional real estate agent in Dubai. You speak {language} fluently.
Your role is to help users find properties, answer real estate questions, and provide market insights.

**STRICT CONTENT POLICY - YOU MUST FOLLOW THESE RULES:**

1. **DUBAI REAL ESTATE FOCUS ONLY**: You are ONLY allowed to discuss topics related to Dubai real estate, properties, and related services.

2. **PROHIBITED TOPICS**: You MUST NOT respond to any questions about:
   - Cars, vehicles, automotive topics (Lamborghini, Ferrari, etc.)
   - Stock market, investments, cryptocurrencies
   - Politics, religion, or sensitive topics
   - Technology, gadgets, or electronics
   - Travel, tourism (unless related to property viewing)
   - Food, restaurants, entertainment
   - Sports, celebrities, or entertainment
   - Any topic not directly related to Dubai real estate

3. **REDIRECTION POLICY**: If asked about prohibited topics:
   - Politely decline to answer
   - Clearly state that you only discuss Dubai real estate
   - Redirect the conversation back to property-related topics
   - Do not provide any information, even if you know it

Current available properties context:
{properties_context}

Conversation History:
{history}

**CRITICAL RESPONSE FORMATTING RULES - MUST FOLLOW EXACTLY:**

1. **LANGUAGE REQUIREMENT**: You MUST respond entirely in {language}. Never mix languages in your response.

2. **CONTENT SCOPE**: Only discuss Dubai real estate topics. Redirect all other queries.

3. **RESPONSE STRUCTURE**: 
   - Use PROPER LINE BREAKS between paragraphs and sections
   - Use clear section headings
   - Use numbered lists for main items
   - Use bullet points with • symbol for features/projects
   - Leave ONE blank line between major sections
   - Use proper spacing for readability

4. **FORMATTING STYLE**:
   - For section headers: Use ALL CAPS or Title Case, followed by a blank line
   - For lists: Use proper indentation and line breaks
   - For paragraphs: Keep them concise with proper line breaks

**LANGUAGE-SPECIFIC GUIDELINES:**

ENGLISH:
- Use professional British English
- Format: Standard Western formatting with left-to-right text
- Use standard English punctuation and spacing

ARABIC:
- Use formal Modern Standard Arabic
- Format: Right-to-left text alignment
- Use proper Arabic punctuation (، ؛ .)
- Ensure proper Arabic character rendering

TAMIL:
- Use formal Tamil language
- Format: Left-to-right text alignment  
- Use proper Tamil punctuation
- Ensure proper Tamil character rendering

**REDIRECTION EXAMPLES FOR PROHIBITED TOPICS:**

If asked about cars: "I specialize exclusively in Dubai real estate and cannot provide information about vehicles. How can I assist you with property inquiries in Dubai today?"

If asked about stocks: "My expertise is limited to Dubai's property market. I'd be happy to discuss real estate investment opportunities instead."

If asked about travel: "I focus on helping clients with Dubai property matters. Are you looking for properties to visit or invest in?"

**CONTENT GUIDELINES:**
- Always use proper line breaks and spacing
- Make responses visually appealing and easy to read
- Use consistent formatting throughout
- Keep paragraphs short and focused
- Ensure good readability on both mobile and desktop
- MOST IMPORTANT: Respond ONLY in {language} and ONLY about Dubai real estate"""

        self.human_template = "{text}"

        self.chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_template),
            HumanMessagePromptTemplate.from_template(self.human_template)
        ])
        
    def detect_language(self, message, requested_language="auto"):
        """Detect language of the message with fallback, respecting requested language"""
        # If user specifically requested a language, use it
        if requested_language and requested_language != "auto":
            return requested_language.lower()
            
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
    
    def get_memory(self, session_id):
        """Get or create conversation memory for session"""
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferWindowMemory(
                k=10,  # Keep last 10 exchanges
                return_messages=True,
                memory_key="history",
                human_prefix="User",
                ai_prefix="Assistant"
            )
        return self.memories[session_id]
    
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
    
    def format_messages_for_prompt(self, memory):
        """Format memory messages for the prompt"""
        messages = memory.load_memory_variables({})['history']
        formatted_history = ""
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_history += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                formatted_history += f"Assistant: {msg.content}\n"
        
        return formatted_history.strip()
    
    def is_real_estate_related(self, message):
        """Check if the message is related to Dubai real estate"""
        message_lower = message.lower()
        
        # Real estate keywords
        real_estate_keywords = [
            'property', 'properties', 'real estate', 'realestate', 'house', 'apartment', 'villa',
            'studio', 'penthouse', 'duplex', 'townhouse', 'condo', 'flat', 'rent', 'buy', 'purchase',
            'sell', 'sale', 'investment', 'invest', 'price', 'cost', 'budget', 'aed', 'location',
            'area', 'sqft', 'square feet', 'bedroom', 'bathroom', 'amenities', 'facilities',
            'developer', 'construction', 'built', 'ready', 'offplan', 'community', 'compound',
            'view', 'facing', 'parking', 'balcony', 'terrace', 'garden', 'pool', 'gym', 'security',
            'maintenance', 'service', 'charge', 'fee', 'commission', 'agent', 'broker', 'agency',
            'dubai', 'uae', 'emirates', 'emirate', 'burj', 'marina', 'palm', 'jumeirah', 'deira',
            'downtown', 'business bay', 'sheikh zayed', 'szx', 'dubai hills', 'arabian ranches',
            'motor city', 'sports city', 'international city', 'discovery gardens', 'jlt', 'jumeirah lake',
            'dubai creek', 'dubai harbour', 'bluewaters', 'city walk', 'dubai design district', 'd3',
            'al barsha', 'al quoz', 'al safa', 'al wasl', 'al manara', 'umm suqeim', 'nad al sheba',
            'mirdif', 'meydan', 'ras al khor', 'dubai silicon oasis', 'dso', 'dubai investment park',
            'dip', 'dubai land', 'dubai south', 'dubai world central', 'dwc', 'expo', 'expo city',
            'rental', 'lease', 'tenancy', 'tenant', 'landlord', 'owner', 'mortgage', 'loan', 'finance',
            'down payment', 'deposit', 'contract', 'agreement', 'ejari', 'rera', 'dld', 'dubai land department',
            'transfer fee', 'registration', 'title deed', 'ownership', 'freehold', 'leasehold'
        ]
        
        # Prohibited topics keywords
        prohibited_keywords = [
            'car', 'vehicle', 'automotive', 'lamborghini', 'ferrari', 'porsche', 'bmw', 'mercedes', 'audi',
            'toyota', 'honda', 'nissan', 'ford', 'chevrolet', 'hyundai', 'kia', 'volkswagen', 'volvo',
            'stock', 'share', 'market', 'trading', 'investment', 'crypto', 'bitcoin', 'ethereum', 'forex',
            'currency', 'exchange', 'dollar', 'euro', 'pound', 'politics', 'government', 'election', 'vote',
            'religion', 'islam', 'christian', 'hindu', 'buddhist', 'jewish', 'god', 'prayer', 'worship',
            'technology', 'gadget', 'iphone', 'samsung', 'laptop', 'computer', 'software', 'hardware',
            'travel', 'tourism', 'vacation', 'holiday', 'flight', 'airline', 'hotel', 'resort', 'beach',
            'food', 'restaurant', 'cafe', 'cuisine', 'meal', 'dinner', 'lunch', 'breakfast', 'recipe',
            'sports', 'football', 'soccer', 'cricket', 'tennis', 'basketball', 'golf', 'fitness', 'exercise',
            'celebrity', 'movie', 'film', 'music', 'song', 'artist', 'actor', 'actress', 'entertainment',
            'weather', 'climate', 'temperature', 'rain', 'sun', 'health', 'medical', 'doctor', 'hospital',
            'education', 'school', 'university', 'college', 'course', 'study', 'learn', 'student'
        ]
        
        # Check if message contains real estate keywords
        has_real_estate_keywords = any(keyword in message_lower for keyword in real_estate_keywords)
        
        # Check if message contains prohibited keywords
        has_prohibited_keywords = any(keyword in message_lower for keyword in prohibited_keywords)
        
        # If it has prohibited keywords but no real estate context, it's not related
        if has_prohibited_keywords and not has_real_estate_keywords:
            return False
        
        # If it has real estate keywords, it's related
        if has_real_estate_keywords:
            return True
        
        # For very short or ambiguous messages, assume it might be real estate related
        # to allow for natural conversation flow
        if len(message.split()) <= 3:
            return True
            
        return False
    
    def enhance_response_formatting(self, text):
        """Enhance the formatting of the response for better readability"""
        if not text:
            return ""
        
        # Ensure proper line breaks between sections
        text = re.sub(r'(\n)([A-Z][^a-z]*?[A-Z][^a-z]*?:)', r'\1\2', text)
        
        # Add line breaks after headings
        text = re.sub(r'([A-Z][A-Z\s]+[A-Z])([A-Z][a-z])', r'\1\n\n\2', text)
        
        # Ensure bullet points have proper spacing
        text = re.sub(r'(•\s*)', r'\1', text)
        
        # Normalize multiple line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Ensure proper spacing after numbers in lists
        text = re.sub(r'(\d+\.)\s*([A-Z])', r'\1 \2', text)
        
        # Clean up any markdown artifacts
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Ensure the text starts with proper formatting
        if text and not text.startswith('\n'):
            text = text.lstrip()
        
        return text.strip()
    
    def generate_response(self, session_id, message, available_properties=None, requested_language="auto"):
        try:
            # Use requested language if provided, otherwise detect
            language = self.detect_language(message, requested_language)
            memory = self.get_memory(session_id)
            
            # Check if message is real estate related
            if not self.is_real_estate_related(message):
                # Return a polite redirection message
                redirection_responses = {
                    "english": """I specialize exclusively in Dubai real estate and cannot provide information on other topics.

How can I assist you with:
• Property search and recommendations in Dubai
• Real estate market insights
• Investment opportunities in Dubai properties
• Area information and community details

Please let me know how I can help with your Dubai property needs!""",

                    "arabic": """أتخصص حصريًا في عقارات دبي ولا يمكنني تقديم معلومات حول مواضيع أخرى.

كيف يمكنني مساعدتك في:
• البحث عن العقارات والتوصيات في دبي
• رؤى سوق العقارات
• فرص الاستثمار في عقارات دبي
• معلومات المناطق وتفاصيل المجتمعات

يرجى إخباري كيف يمكنني المساعدة في احتياجاتك العقارية في دبي!""",

                    "tamil": """நான் பிரத்தியேகமாக டுபாய் ரியல் எஸ்டேட்டில் நிபுணத்துவம் பெற்றுள்ளேன் மற்றும் பிற தலைப்புகள் குறித்து தகவல்களை வழங்க முடியாது.

டுபாயில் உள்ள பின்வரும் துறைகளில் நான் உங்களுக்கு எவ்வாறு உதவ முடியும்:
• வீடு தேடல் மற்றும் பரிந்துரைகள்
• ரியல் எஸ்டேட் சந்தை நுண்ணறிவுகள்
• டுபாய் வீடுகளில் முதலீட்டு வாய்ப்புகள்
• பகுதி தகவல்கள் மற்றும் கம்யூனிட்டி விவரங்கள்

தயவு செய்து டுபாயில் உங்கள் வீடு தேவைகளுக்கு நான் எவ்வாறு உதவ முடியும் என்று சொல்லுங்கள்!"""
                }
                
                response_text = redirection_responses.get(language, redirection_responses["english"])
                
                # Save to memory
                memory.chat_memory.add_user_message(message)
                memory.chat_memory.add_ai_message(response_text)
                
                return {
                    "response": response_text,
                    "language": language,
                    "preferences": {},
                    "session_id": session_id
                }
            
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
            
            # Get formatted conversation history from memory
            history_text = self.format_messages_for_prompt(memory)
            
            # Format the prompt using LangChain template with explicit language instruction
            formatted_prompt = self.chat_prompt.format(
                language=language,
                properties_context=properties_context,
                history=history_text,
                text=message
            )
            
            # Generate response using Gemini with safety settings
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
                formatted_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Get the response text safely and enhance formatting
            if response and hasattr(response, 'text'):
                response_text = self.enhance_response_formatting(response.text)
            else:
                response_text = self.get_structured_fallback_response(language, message)
            
            # Save to memory
            memory.chat_memory.add_user_message(message)
            memory.chat_memory.add_ai_message(response_text)
            
            return {
                "response": response_text,
                "language": language,
                "preferences": preferences,
                "session_id": session_id
            }
            
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            
            # Use requested language for fallback response
            fallback_language = self.detect_language(message, requested_language)
            return {
                "response": self.get_structured_fallback_response(fallback_language, message),
                "language": fallback_language,
                "preferences": {},
                "session_id": session_id
            }
    
    def get_structured_fallback_response(self, language, user_message):
        """Get structured fallback response with proper formatting in the correct language"""
        user_message_lower = user_message.lower()
        
        if "company" in user_message_lower or "developer" in user_message_lower or "real estate" in user_message_lower:
            # Company/developer related queries
            fallback_responses = {
                "english": """TOP REAL ESTATE COMPANIES IN DUBAI

Dubai's real estate sector features several prominent developers that have shaped the city's iconic skyline and transformed it into a global destination.

1. EMAAR PROPERTIES
Description: Emaar is one of the world's most valuable real estate development companies, known for iconic projects that have transformed Dubai's landscape and set new standards in urban living.

Key Projects:
• Burj Khalifa - World's tallest building and architectural marvel
• The Dubai Mall - One of the world's largest shopping and entertainment destinations
• Downtown Dubai - Premier mixed-use development in the heart of the city
• Dubai Marina - Stunning waterfront residential community
• Arabian Ranches - Exclusive luxury villa community

2. NAKHEEL PROPERTIES
Description: Nakheel is a world-leading master developer famous for innovative coastal developments that have redefined Dubai's geography and captured global attention.

Key Projects:
• Palm Jumeirah - Iconic palm-shaped artificial island
• The World Islands - Unique archipelago shaped like a world map
• Jumeirah Islands - Luxury waterfront residential clusters
• Discovery Gardens - Extensive residential community with themed gardens

3. DAMAC PROPERTIES
Description: DAMAC Properties specializes in luxury living and has partnered with international brands to deliver exclusive branded residences and high-end communities.

Key Projects:
• DAMAC Hills - Master-planned golf community with luxury villas
• AKOYA Oxygen - Nature-inspired residential development
• AYKON City - Landmark urban mixed-use project
• Multiple branded towers across prime locations

CONCLUSION
These leading developers have significantly contributed to Dubai's growth and reputation as a global real estate hub, offering diverse investment opportunities across residential, commercial, and hospitality sectors while continuously innovating the city's urban landscape.""",

                "arabic": """أفضل شركات العقارات في دبي

يشهد قطاع العقارات في دبي وجود عدة مطورين بارزين ساهموا في تشكيل أفق المدينة المميز وحولوها إلى وجهة عالمية.

1. إعمار للعقارات
الوصف: إعمار هي واحدة من أكثر شركات التطوير العقاري قيمة في العالم، تشتهر بمشاريعها الرائدة التي غيرت معالم دبي ووضعت معايير جديدة للحياة العصرية.

المشاريع الرئيسية:
• برج خليفة - أطول مبنى في العالم وتحفة معمارية
• دبي مول - أحد أكبر وجهات التسوق والترفيه في العالم
• داون تاون دبي - التطوير المتميز متعدد الاستخدامات في قلب المدينة
• دبي مارينا - مجتمع سكني ساحلي رائع
• Arabian Ranches - مجتمع فيلات فاخر وحصري

2. نخيل للعقارات
الوصف: نخيل هي مطور رائد عالمي تشتهر بالتطورات الساحلية المبتكرة التي أعادت تعريف جغرافيا دبي وجذبت الاهتمام العالمي.

المشاريع الرئيسية:
• نخلة جميرا - الجزيرة الاصطناعية iconic على شكل نخلة
• جزر العالم - أرخبيل فريد على شكل خريطة العالم
• جزر جميرا - مجمعات سكنية فاخرة على الواجهة المائية
• Discovery Gardens - مجتمع سكني واسع بحدائق ذات طابع خاص

3. داماك للعقارات
الوصف: تخصصت داماك للعقارات في الحياة الفاخرة وتعاونت مع علامات تجارية عالمية لتقديم مساكن حصرية ومجتمعات راقية.

المشاريع الرئيسية:
• داماك هيلز - مجتمع جولف مخطّط مع فيلات فاخرة
• AKOYA Oxygen - تطوير سكني مستوحى من الطبيعة
• AYKON City - مشروع حضري مميز متعدد الاستخدامات
• أبراج متعددة في مواقع متميزة

الخلاصة
ساهمت هذه الشركات الرائدة بشكل كبير في نمو دبي وسمعتها كمركز عقاري عالمي، حيث تقدم فرص استثمارية متنوعة عبر القطاعات السكنية والتجارية والضيافة مع الابتكار المستمر في المشهد الحضري للمدينة.""",

                "tamil": """டுபாயில் முக்கிய ரியல் எஸ்டேட் நிறுவனங்கள்

டுபாயின் ரியல் எஸ்டேட் துறை பல முன்னணி டெவலப்பர்களைக் கொண்டுள்ளது, அவர்கள் நகரின் அடையாளக் குறியான வான்வெளியை வடிவமைத்து அதை உலகளாவிய இலக்காக மாற்றியுள்ளனர்.

1. எமார் பிராபர்ட்டீஸ்
விளக்கம்: எமார் உலகின் மிகவும் மதிப்புமிக்க ரியல் எஸ்டேட் டெவலப்பமென்ட் நிறுவனங்களில் ஒன்றாகும், டுபாயின் இயற்கைக்காட்சியை மாற்றியமைத்து நகர்ப்புற வாழ்க்கையில் புதிய தரங்களை நிர்ணயித்த அடையாளத் திட்டங்களுக்கு பெயர் பெற்றது.

முக்கிய திட்டங்கள்:
• புர்ஜ் கலீபா - உலகின் உயரமான கட்டிடம் மற்றும் கட்டடக்கலை அதிசயம்
• தி டுபாய் மால் - உலகின் மிகப்பெரிய ஷாப்பிங் மற்றும் பொழுதுபோக்கு இடங்களில் ஒன்று
• டவுன்டவுன் டுபாய் - நகரின் இதயத்தில் உள்ள முதன்மை கலப்பு-பயன்பாட்டு மேம்பாடு
• டுபாய் மரீனா - அதிரடியான நீரோர குடியிருப்பு சமூகம்
• அரேபியன் ரான்சஸ் - பிரத்தியேக விதிவிலக்கு வில்லா சமூகம்

2. நகீல் பிராபர்ட்டீஸ்
விளக்கம்: நகீல் ஒரு உலகத் தலைமை மாஸ்டர் டெவலப்பர் ஆகும், இது டுபாயின் புவியியலை மறுவரையறை செய்து உலகளாவிய கவனத்தை ஈர்த்த புதுமையான கடலோர மேம்பாடுகளுக்கு பிரபலமானது.

முக்கிய திட்டங்கள்:
• பாம் ஜுமெய்ரா - பனை வடிவத்தில் அமைந்த அடையாள செயற்கைத் தீவு
• தி வேர்ல்ட் ஐலண்ட்ஸ் - உலக வரைபட வடிவில் உள்ள தனித்துவமான தீவுக்கூட்டம்
• ஜுமெய்ரா ஐலண்ட்ஸ் - விதிவிலக்கு நீரோர குடியிருப்பு கிளஸ்டர்கள்
• டிஸ்கவரி கார்டன்ஸ் - தீம் தோட்டங்களுடன் கூடிய விரிவான குடியிருப்பு சமூகம்

3. டாமாக் பிராபர்ட்டீஸ்
விளக்கம்: டாமாக் பிராபர்ட்டீஸ் விதிவிலக்கு வாழ்க்கை முறையில் நிபுணத்துவம் பெற்றது மற்றும் பிராண்டட் குடியிருப்புகள் மற்றும் உயர்-இன கம்யூனிட்டிகளை வழங்க சர்வதேச பிராண்டுகளுடன் இணைந்துள்ளது.

முக்கிய திட்டங்கள்:
• டாமாக் ஹில்ஸ் - விதிவிலக்கு வில்லாக்களுடன் கூடிய மாஸ்டர்-ப்ளான்டு கோல்ஃப் சமூகம்
• AKOYA Oxygen - இயற்கையில் ஈர்க்கப்பட்ட குடியிருப்பு மேம்பாடு
• AYKON City - அடையாள நகர்ப்புற கலப்பு-பயன்பாட்டு திட்டம்
• முதன்மை இடங்களில் பல பிராண்டட் கோபுரங்கள்

முடிவு
இந்த முன்னணி டெவலப்பர்கள் டுபாயின் வளர்ச்சி மற்றும் உலகளாவிய ரியல் எஸ்டேட் மையமாக அதன் நற்பெயரில் கணிசமாக பங்களித்துள்ளனர், குடியிருப்பு, வணிக மற்றும் விருந்தோம்பல் துறைகளில் மாறுபட்ட முதலீட்டு வாய்ப்புகளை வழங்குகின்றன, அதே நேரத்தில் நகரின் நகர்ப்புற காட்சியை தொடர்ந்து புதுமைப்படுத்துகின்றன."""
            }
        elif "property" in user_message_lower or "house" in user_message_lower or "apartment" in user_message_lower:
            # Property-related queries
            fallback_responses = {
                "english": """PROPERTY ASSISTANCE

I'd be happy to help you find properties in Dubai! To provide you with the best options, I need to understand your requirements better.

Please share these details:

1. Budget Range - What's your preferred budget in AED?
2. Property Type - Apartment, Villa, Studio, or Penthouse?
3. Location Preference - Any specific areas in Dubai?
4. Bedrooms - How many bedrooms do you need?
5. Key Priorities - What's most important to you?

POPULAR DUBAI AREAS:
• Downtown Dubai
• Dubai Marina
• Palm Jumeirah
• Business Bay
• Jumeirah
• Deira

Please provide your preferences, and I'll show you the best matching properties!""",

                "arabic": """المساعدة العقارية

سأكون سعيداً بمساعدتك في العثور على عقارات في دبي! لتقديم أفضل الخيارات لك، أحتاج إلى فهم متطلباتك بشكل أفضل.

يرجى مشاركة هذه التفاصيل:

1. نطاق الميزانية - ما هي ميزانيتك المفضلة بالدرهم الإماراتي؟
2. نوع العقار - شقة، فيلا، استوديو، أو بنتهاوس؟
3. تفضيل الموقع - أي مناطق محددة في دبي؟
4. غرف النوم - كم عدد غرف النوم التي تحتاجها؟
5. الأولويات الرئيسية - ما هو الأهم بالنسبة لك؟

مناطق دبي الشهيرة:
• داون تاون دبي
• دبي مارينا
• نخلة جميرا
• الخليج التجاري
• جميرا
• ديرة

يرجى تقديم تفضيلاتك، وسأظهر لك أفضل العقارات المطابقة!""",

                "tamil": """வீடு உதவி சேவை

டுபாயில் உள்ள வீடுகளை கண்டுபிடிக்க நான் உதவ மகிழ்ச்சியாக இருப்பேன்! உங்களுக்கு சிறந்த விருப்பங்களை வழங்க, உங்கள் தேவைகளை நன்றாக புரிந்து கொள்ள வேண்டும்.

தயவு செய்து இந்த விவரங்களைப் பகிரவும்:

1. பட்ஜெட் வரம்பு - AED-ல் உங்கள் விருப்பமான பட்ஜெட் என்ன?
2. வீடு வகை - அபார்ட்மெண்ட், வில்லா, ஸ்டுடியோ, அல்லது பென்ட்ஹவுஸ்?
3. இடம் முன்னுரிமை - டுபாயில் ஏதேனும் குறிப்பிட்ட பகுதிகள்?
4. படுக்கையறைகள் - உங்களுக்கு எத்தனை படுக்கையறைகள் தேவை?
5. முக்கிய முன்னுரிமைகள் - உங்களுக்கு எது மிக முக்கியமானது?

பிரபலமான டுபாய் பகுதிகள்:
• டவுன்டவுன் டுபாய்
• டுபாய் மரீனா
• பாம் ஜுமெய்ரா
• பிசினஸ் பே
• ஜுமெய்ரா
• டெய்ரா

தயவு செய்து உங்கள் விருப்பங்களை வழங்கவும், நான் உங்களுக்கு சிறந்த பொருந்தக்கூடிய வீடுகளைக் காண்பிப்பேன்!"""
            }
        else:
            # General greeting/fallback
            fallback_responses = {
                "english": """WELCOME TO DUBAI REAL ESTATE

I'm your professional real estate assistant, here to help you navigate Dubai's dynamic property market.

HOW I CAN ASSIST YOU:

1. Property Search and Recommendations
• Find apartments, villas, studios, and penthouses
• Match properties to your budget and preferences
• Provide area insights and market trends

2. Market Intelligence
• Current property prices and trends
• Investment opportunities
• Rental yield analysis

3. Area Expertise
• Downtown Dubai and Business Bay
• Dubai Marina and Palm Jumeirah
• Jumeirah and Deira areas

TO GET STARTED:
Please tell me what you're looking for - whether it's buying, renting, investing, or general market information!""",

                "arabic": """مرحباً بك في دبي للعقارات

أنا مساعدك العقاري المحترف، هنا لمساعدتك في التنقل في سوق العقارات الديناميكي في دبي.

كيف يمكنني مساعدتك:

1. البحث عن العقارات والتوصيات
• العثور على الشقق، الفلل، الاستوديوهات، والبنتهوسات
• مطابقة العقارات مع ميزانيتك وتفضيلاتك
• تقديم رؤى حول المناطق واتجاهات السوق

2. ذكاء السوق
• أسعار العقارات الحالية والاتجاهات
• فرص الاستثمار
• تحليل عوائد الإيجار

3. الخبرة في المناطق
• Downtown Dubai and Business Bay
• Dubai Marina and Palm Jumeirah
• مناطق جميرا وديرة

للبدء:
يرجى إخباري عما تبحث عنه - سواء كان الشراء، التأجير، الاستثمار، أو معلومات عامة عن السوق!""",

                "tamil": """டுபாய் ரியல் எஸ்டேட்டுக்கு வரவேற்கிறோம்

நான் உங்கள் தொழில்முறை ரியல் எஸ்டேட் உதவியாளன், டுபாயின் மாறும் சந்தை நிலைகளை நீங்கள் எளிதாக புரிந்து கொள்ள உதவ இங்கு உள்ளேன்.

நான் உங்களுக்கு எவ்வாறு உதவ முடியும்:

1. வீடு தேடல் மற்றும் பரிந்துரைகள்
• அபார்ட்மெண்ட்கள், வில்லாக்கள், ஸ்டுடியோக்கள் மற்றும் பென்ட்ஹவுஸ்களை கண்டறிதல்
• உங்கள் பட்ஜெட் மற்றும் விருப்பங்களுக்கு ஏற்ற வீடுகளை பொருத்துதல்
• பகுதி நுண்ணறிவுகள் மற்றும் சந்தை போக்குகளை வழங்குதல்

2. சந்தை நுண்ணறிவு
• தற்போதைய வீடு விலைகள் மற்றும் போக்குகள்
• முதலீட்டு வாய்ப்புகள்
• வாடகை வருவாய் பகுப்பாய்வு

3. பகுதி நிபுணத்துவம்
• டவுன்டவுன் டுபாய் மற்றும் பிசினஸ் பே
• டுபாய் மரீனா மற்றும் பாம் ஜுமெய்ரா
• ஜுமெய்ரா மற்றும் டெய்ரா பகுதிகள்

தொடங்குவதற்கு:
தயவு செய்து நீங்கள் என்ன தேடுகிறீர்கள் என்று சொல்லுங்கள் - அது வாங்குதல், வாடகை, முதலீடு, அல்லது பொது சந்தை தகவல்கள் என்பதை!"""
            }
        
        return fallback_responses.get(language, fallback_responses["english"])
    
    def clear_memory(self, session_id):
        """Clear conversation memory for a session"""
        if session_id in self.memories:
            del self.memories[session_id]