from pydantic import BaseModel
from typing import List, Optional

# --- Request Models ---

class IngredientInfo(BaseModel):
    name: str
    days: int
    urgency: str  # 'high', 'medium', 'low'
    storage: str  # 'refrigerate', 'pantry', 'freezer'

class PantryAnalysisResponse(BaseModel):
    ingredients: List[str]
    expiry_info: Optional[dict] = None  # Maps ingredient name to expiry details

class RecipeSuggestionRequest(BaseModel):
    ingredients: List[str]
    preferences: Optional[str] = "Quick and easy"

class NutritionalInfo(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int

class RecipeInfo(BaseModel):
    name: str
    nutritional_info: NutritionalInfo
    health_score: int # 0-100

class RecipeSuggestionResponse(BaseModel):
    recipes: List[RecipeInfo]

class SearchFilters(BaseModel):
    channel: Optional[str] = None
    cuisine: Optional[str] = None

class VideoSearchRequest(BaseModel):
    selected_recipe: str
    ingredients: List[str]
    filters: Optional[SearchFilters] = None

class SaveRecipeRequest(BaseModel):
    recipe_name: str
    ingredients: List[str]
    video_url: str
    thumbnail: str
    accessible_guide: Optional[str] = None

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

class PantryItemResponse(BaseModel):
    id: int
    ingredient_name: str
    scan_date: str
    days_until_expiry: int
    urgency: str
    storage: str

class SavedRecipeResponse(BaseModel):
    id: int
    recipe_name: str
    ingredients: List[str]
    video_url: str
    thumbnail: str
    accessible_guide: Optional[str]
    saved_at: str
