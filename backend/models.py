from pydantic import BaseModel
from typing import List, Optional

# --- Request Models ---

class PantryAnalysisResponse(BaseModel):
    ingredients: List[str]

class RecipeSuggestionRequest(BaseModel):
    ingredients: List[str]
    preferences: Optional[str] = "Quick and easy"

class RecipeSuggestionResponse(BaseModel):
    recipes: List[str]

class SearchFilters(BaseModel):
    channel: Optional[str] = None
    cuisine: Optional[str] = None

class VideoSearchRequest(BaseModel):
    selected_recipe: str
    ingredients: List[str]
    filters: Optional[SearchFilters] = None

# --- Response Models ---

class VideoResult(BaseModel):
    title: str
    url: str
    thumbnail: str
    channel: str
    views: str
    smart_score: float
    accessible_guide: Optional[str] = None
    match_reason: Optional[str] = None

class VideoSearchResponse(BaseModel):
    videos: List[VideoResult]
