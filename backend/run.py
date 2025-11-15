import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    
    print(f"Starting Real Estate Agent Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database URL: {os.getenv('DATABASE_URL')}")
    print(f"Gemini API Key: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not Set'}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )