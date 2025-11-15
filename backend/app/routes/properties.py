from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Property
from pydantic import BaseModel
from typing import List, Optional
import datetime

router = APIRouter()

class PropertyCreate(BaseModel):
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

class PropertyResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    location: str
    property_type: str
    bedrooms: int
    bathrooms: int
    area_sqft: float
    amenities: List[str]
    images: List[str]
    available_from: Optional[datetime.datetime]
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

@router.post("/properties", response_model=PropertyResponse)
async def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db)
):
    property_obj = Property(
        **property_data.dict(),
        available_from=property_data.available_from or datetime.datetime.utcnow()
    )
    db.add(property_obj)
    db.commit()
    db.refresh(property_obj)
    return property_obj

@router.get("/properties", response_model=List[PropertyResponse])
async def get_properties(
    location: Optional[str] = None,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    bedrooms: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Property)
    
    if location:
        query = query.filter(Property.location.ilike(f"%{location}%"))
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if min_price:
        query = query.filter(Property.price >= min_price)
    if max_price:
        query = query.filter(Property.price <= max_price)
    if bedrooms:
        query = query.filter(Property.bedrooms >= bedrooms)
    
    properties = query.all()
    return properties

@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_obj