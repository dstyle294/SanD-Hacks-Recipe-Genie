from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    google_id = Column(String, unique=True, index=True)
    profile_pic = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    pantry_items = relationship("PantryItem", back_populates="user")
    saved_recipes = relationship("SavedRecipe", back_populates="user")

class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ingredient_name = Column(String, index=True)
    scan_date = Column(DateTime, default=datetime.utcnow)
    days_until_expiry = Column(Integer)
    urgency = Column(String) # high, medium, low
    storage = Column(String) # refrigerate, pantry, freezer
    
    user = relationship("User", back_populates="pantry_items")

class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_name = Column(String)
    ingredients = Column(JSON) # List of ingredients used
    video_url = Column(String)
    thumbnail = Column(String)
    accessible_guide = Column(String)
    saved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_recipes")
