from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# AI Models Configuration
AI_MODELS = {
    "photography": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
    "film_directing": {"provider": "gemini", "model": "gemini-2.0-flash"},
    "media": {"provider": "gemini", "model": "gemini-2.0-flash"},
    "mathematics": {"provider": "openai", "model": "gpt-4o"},
    "default": {"provider": "openai", "model": "gpt-4o"}
}

# University Resources Database
UNIVERSITY_RESOURCES = {
    "photography": [
        {"name": "Harvard University", "url": "https://www.harvard.edu", "department": "Visual and Environmental Studies"},
        {"name": "Oxford University", "url": "https://www.ox.ac.uk", "department": "Ruskin School of Art"},
        {"name": "Stanford University", "url": "https://www.stanford.edu", "department": "Art & Art History"},
        {"name": "MIT", "url": "https://www.mit.edu", "department": "Architecture"},
        {"name": "Yale University", "url": "https://www.yale.edu", "department": "School of Art"},
        {"name": "ANU", "url": "https://www.anu.edu.au", "department": "School of Art & Design"},
        {"name": "Cambridge University", "url": "https://www.cam.ac.uk", "department": "History of Art"},
        {"name": "UCLA", "url": "https://www.ucla.edu", "department": "Arts and Architecture"},
        {"name": "NYU", "url": "https://www.nyu.edu", "department": "Tisch School of the Arts"},
        {"name": "Columbia University", "url": "https://www.columbia.edu", "department": "School of the Arts"},
        {"name": "Princeton University", "url": "https://www.princeton.edu", "department": "Art and Archaeology"},
        {"name": "University of Edinburgh", "url": "https://www.ed.ac.uk", "department": "Edinburgh College of Art"},
        {"name": "Royal College of Art", "url": "https://www.rca.ac.uk", "department": "Photography"}
    ],
    "film_directing": [
        {"name": "USC", "url": "https://www.usc.edu", "department": "School of Cinematic Arts"},
        {"name": "NYU", "url": "https://www.nyu.edu", "department": "Tisch School of the Arts"},
        {"name": "UCLA", "url": "https://www.ucla.edu", "department": "School of Theater, Film and Television"},
        {"name": "AFI", "url": "https://www.afi.com", "department": "American Film Institute"},
        {"name": "Columbia University", "url": "https://www.columbia.edu", "department": "School of the Arts"},
        {"name": "Harvard University", "url": "https://www.harvard.edu", "department": "Visual and Environmental Studies"},
        {"name": "Yale University", "url": "https://www.yale.edu", "department": "School of Drama"},
        {"name": "Stanford University", "url": "https://www.stanford.edu", "department": "Film Studies"},
        {"name": "ANU", "url": "https://www.anu.edu.au", "department": "School of Art & Design"},
        {"name": "Cambridge University", "url": "https://www.cam.ac.uk", "department": "Film Studies"},
        {"name": "Oxford University", "url": "https://www.ox.ac.uk", "department": "Film Studies"},
        {"name": "Northwestern University", "url": "https://www.northwestern.edu", "department": "Radio/Television/Film"},
        {"name": "University of Edinburgh", "url": "https://www.ed.ac.uk", "department": "Film Studies"}
    ],
    "mathematics": [
        {"name": "MIT", "url": "https://www.mit.edu", "department": "Mathematics"},
        {"name": "Harvard University", "url": "https://www.harvard.edu", "department": "Mathematics"},
        {"name": "Stanford University", "url": "https://www.stanford.edu", "department": "Mathematics"},
        {"name": "Princeton University", "url": "https://www.princeton.edu", "department": "Mathematics"},
        {"name": "Cambridge University", "url": "https://www.cam.ac.uk", "department": "Mathematics"},
        {"name": "Oxford University", "url": "https://www.ox.ac.uk", "department": "Mathematics"},
        {"name": "Caltech", "url": "https://www.caltech.edu", "department": "Mathematics"},
        {"name": "Yale University", "url": "https://www.yale.edu", "department": "Mathematics"},
        {"name": "Columbia University", "url": "https://www.columbia.edu", "department": "Mathematics"},
        {"name": "ANU", "url": "https://www.anu.edu.au", "department": "Mathematical Sciences Institute"},
        {"name": "University of Chicago", "url": "https://www.uchicago.edu", "department": "Mathematics"},
        {"name": "UC Berkeley", "url": "https://www.berkeley.edu", "department": "Mathematics"},
        {"name": "Imperial College London", "url": "https://www.imperial.ac.uk", "department": "Mathematics"}
    ]
}

# Define Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_message: str
    ai_response: str
    subject: Optional[str] = None
    ai_model_used: str
    sources: List[Dict[str, str]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    session_id: str
    subject: Optional[str] = None

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    total_messages: int = 0

class UniversityResource(BaseModel):
    name: str
    url: str
    department: str
    subject: str

def detect_subject(message: str) -> str:
    """Detect the subject based on keywords in the message"""
    message_lower = message.lower()
    
    photo_keywords = ["photo", "photography", "camera", "lens", "exposure", "aperture", "iso", "composition", "lighting", "portrait", "landscape"]
    film_keywords = ["film", "cinema", "director", "directing", "movie", "screenplay", "cinematography", "editing", "production", "script"]
    math_keywords = ["math", "mathematics", "algebra", "calculus", "geometry", "statistics", "equation", "formula", "theorem", "proof", "integral", "derivative"]
    
    photo_score = sum(1 for keyword in photo_keywords if keyword in message_lower)
    film_score = sum(1 for keyword in film_keywords if keyword in message_lower)
    math_score = sum(1 for keyword in math_keywords if keyword in message_lower)
    
    if photo_score > film_score and photo_score > math_score:
        return "photography"
    elif film_score > math_score:
        return "film_directing"
    elif math_score > 0:
        return "mathematics"
    else:
        return "default"

def get_ai_model_for_subject(subject: str) -> Dict[str, str]:
    """Get the appropriate AI model for a given subject"""
    return AI_MODELS.get(subject, AI_MODELS["default"])

def get_sources_for_subject(subject: str) -> List[Dict[str, str]]:
    """Get university sources for a given subject"""
    if subject in UNIVERSITY_RESOURCES:
        return [{"name": res["name"], "url": res["url"], "department": res["department"]} 
                for res in UNIVERSITY_RESOURCES[subject][:5]]  # Return top 5 sources
    return []

def create_educational_system_message(subject: str, sources: List[Dict[str, str]]) -> str:
    """Create a specialized system message for educational content"""
    base_message = """You are an educational assistant specializing in providing factual, unbiased information for Year 11 and Year 12 students. Your role is to:

1. Provide accurate, educational content appropriate for senior high school level
2. Always maintain objectivity and avoid bias
3. Reference trusted university sources when possible
4. Explain concepts clearly and progressively
5. Encourage critical thinking and deeper understanding

"""
    
    if subject == "photography":
        subject_message = """You are particularly knowledgeable about:
- Photography techniques and composition
- Camera settings and equipment
- History of photography
- Visual storytelling and artistic expression
- Technical aspects of image creation"""
    elif subject == "film_directing":
        subject_message = """You are particularly knowledgeable about:
- Film directing techniques and theory
- Cinematography and visual storytelling
- Film history and analysis
- Production processes and workflows
- Media studies and criticism"""
    elif subject == "mathematics":
        subject_message = """You are particularly knowledgeable about:
- Mathematical concepts and problem-solving
- Algebra, calculus, and geometry
- Statistical analysis and data interpretation
- Mathematical proofs and reasoning
- Real-world applications of mathematics"""
    else:
        subject_message = "You provide comprehensive educational support across multiple subjects."
    
    sources_message = "\n\nRefer to these trusted university sources when relevant:\n"
    for source in sources:
        sources_message += f"- {source['name']} ({source['department']}): {source['url']}\n"
    
    return base_message + subject_message + sources_message + "\n\nAlways cite sources when referencing specific information from universities."

@api_router.post("/chat", response_model=ChatMessage)
async def chat_with_ai(request: ChatRequest):
    try:
        # Detect subject if not provided
        subject = request.subject or detect_subject(request.message)
        
        # Get appropriate AI model and sources
        model_config = get_ai_model_for_subject(subject)
        sources = get_sources_for_subject(subject)
        
        # Create system message
        system_message = create_educational_system_message(subject, sources)
        
        # Get API key
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        # Initialize chat with appropriate model
        chat = LlmChat(
            api_key=api_key,
            session_id=request.session_id,
            system_message=system_message
        ).with_model(model_config["provider"], model_config["model"])
        
        # Send message and get response
        user_message = UserMessage(text=request.message)
        ai_response = await chat.send_message(user_message)
        
        # Create chat message record
        chat_message = ChatMessage(
            session_id=request.session_id,
            user_message=request.message,
            ai_response=ai_response,
            subject=subject,
            ai_model_used=f"{model_config['provider']}/{model_config['model']}",
            sources=sources
        )
        
        # Store in database
        await db.chat_messages.insert_one(chat_message.dict())
        
        # Update session
        await db.chat_sessions.update_one(
            {"id": request.session_id},
            {
                "$set": {"last_active": datetime.utcnow()},
                "$inc": {"total_messages": 1}
            },
            upsert=True
        )
        
        return chat_message
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@api_router.post("/sessions", response_model=ChatSession)
async def create_session():
    """Create a new chat session"""
    session = ChatSession()
    await db.chat_sessions.insert_one(session.dict())
    return session

@api_router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(session_id: str):
    """Get all messages for a session"""
    messages = await db.chat_messages.find({"session_id": session_id}).sort("timestamp", 1).to_list(1000)
    return [ChatMessage(**msg) for msg in messages]

@api_router.get("/resources/{subject}", response_model=List[UniversityResource])
async def get_subject_resources(subject: str):
    """Get university resources for a specific subject"""
    if subject.lower() not in UNIVERSITY_RESOURCES:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    resources = UNIVERSITY_RESOURCES[subject.lower()]
    return [UniversityResource(
        name=res["name"],
        url=res["url"],
        department=res["department"],
        subject=subject
    ) for res in resources]

@api_router.get("/")
async def root():
    return {"message": "Educational Study App API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()