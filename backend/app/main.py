from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

from .database import create_db_and_tables, get_session, engine
from .models import User, Ingredient, Recipe
from .auth import get_current_user, create_access_token, get_password_hash, verify_password, verify_google_token
from .agents import VisionAgent, RecipeAgent, SearchAgent

app = FastAPI(title="Recipe Genie AI")

# CORS setup for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents
vision_agent = VisionAgent()
recipe_agent = RecipeAgent()
search_agent = SearchAgent()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Add/Update dummy user
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == "guest@example.com")).first()
        hashed_pwd = get_password_hash("password")
        if not user:
            user = User(email="guest@example.com", hashed_password=hashed_pwd, full_name="Guest Chef")
            session.add(user)
        else:
            # Force update password hash in case hashing algorithm changed
            user.hashed_password = hashed_pwd
            session.add(user)
        session.commit()

@app.post("/register")
async def register(user_data: Dict[str, str], session: Session = Depends(get_session)):
    hashed_pwd = get_password_hash(user_data["password"])
    user = User(email=user_data["email"], hashed_password=hashed_pwd, full_name=user_data.get("full_name"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created"}

@app.post("/token")
async def login(form_data: Dict[str, str], session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data["username"])).first()
    if not user or not verify_password(form_data["password"], user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    
    # Check for expiring items
    expiring_soon = session.exec(
        select(Ingredient).where(
            Ingredient.user_id == user.id,
            Ingredient.expiry_date <= date.today() + timedelta(days=3),
            Ingredient.expiry_date >= date.today()
        )
    ).all()
    
    notifications = [f"{ing.name} is expiring soon ({ing.expiry_date})!" for ing in expiring_soon]
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "notifications": notifications
    }

@app.post("/auth/google")
async def google_auth(token_data: Dict[str, str], session: Session = Depends(get_session)):
    try:
        google_data = verify_google_token(token_data["id_token"])
        email = google_data["email"]
        
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            user = User(email=email, full_name=google_data.get("name", "Google User"))
            session.add(user)
            session.commit()
            session.refresh(user)
            
        access_token = create_access_token(data={"sub": user.email})
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "email": user.email,
                "full_name": user.full_name
            }
        }
    except Exception as e:
        print(f"ERROR in google_auth endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-ingredients")
async def upload_ingredients(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Save file temporarily or process directly
    import os
    file_path = os.path.abspath(f"temp_{file.filename}")
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Step 1: EyePop Detection
        detected_names = await vision_agent.detect_ingredients(file_path)
        
        # Step 2: Gemini Expiry dates
        expiry_map = await recipe_agent.get_expiry_dates(detected_names)
        
        # Step 3: Save to DB
        ingredients_added = []
        for name in detected_names:
            days = expiry_map.get(name, 7)
            expiry_date = date.today() + timedelta(days=int(days))
            new_ing = Ingredient(name=name, expiry_date=expiry_date, user_id=current_user.id)
            session.add(new_ing)
            ingredients_added.append({"name": name, "expiry": expiry_date})
        
        session.commit()
        return {"ingredients": ingredients_added}
    except Exception as e:
        print(f"Error in upload_ingredients: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/generate-recipes")
async def generate_recipes(
    payload: Dict[str, Any], 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get all ingredients for this user
    ingredients = session.exec(select(Ingredient).where(Ingredient.user_id == current_user.id)).all()
    ing_list = [{"name": i.name, "expiry": i.expiry_date.isoformat()} for i in ingredients]
    
    if not ing_list:
        raise HTTPException(status_code=400, detail="No ingredients found. Upload a photo first.")
    
    preferences = payload.get("text", "")
    use_pantry = payload.get("use_pantry", False)
    
    recipes = await recipe_agent.generate_recipes(ing_list, preferences, use_pantry)
    

        
    return {"recipes": recipes}

@app.post("/select-recipe")
async def select_recipe(
    recipe_data: Dict[str, Any], 
    current_user: User = Depends(get_current_user)
):
    # Step 1: Find best video
    best_video = await search_agent.find_best_video(recipe_data["title"])
    
    # Step 2: Generate final detailed recipe
    final_recipe_md = await recipe_agent.generate_final_recipe(recipe_data["title"], best_video["context"])
    
    return {
        "video": best_video,
        "recipe_markdown": final_recipe_md
    }

@app.get("/recipe-image")
async def get_recipe_image(query: str):
    """Fetch a real image URL for a recipe using DuckDuckGo"""
    image_url = await search_agent.find_recipe_image(query)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=image_url)
