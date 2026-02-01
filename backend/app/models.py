from datetime import datetime, date
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: bool = Field(default=True)
    
    ingredients: List["Ingredient"] = Relationship(back_populates="user")

class Ingredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    expiry_date: Optional[date] = None
    added_at: datetime = Field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None # Link to the uploaded image if we want to store it
    
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="ingredients")

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    steps: str # JSON or Markdown
    ingredients_list: str # What it actually uses
    video_url: Optional[str] = None
    video_title: Optional[str] = None
    
    user_id: int = Field(foreign_key="user.id")
