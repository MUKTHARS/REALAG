from pydantic import BaseModel
from typing import Optional, List
import datetime

class PropertyBase(BaseModel):
    title: str
    description: str
    price: float
    location: str
    property_type: str
    bedrooms: int
    bathrooms: int
    area_sqft: float
    amenities: List[str] = []
    images: List[str] = []
    available_from: Optional[datetime.datetime] = None

class PropertyCreate(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "auto"

class ChatResponse(BaseModel):
    response: str
    language: str
    session_id: str
    timestamp: str


class ChatSessionBase(BaseModel):
    session_id: str
    title: str
    language: str
    message_count: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

class ChatSessionResponse(ChatSessionBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    total_count: int

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime.datetime

class Config:
        from_attributes = True