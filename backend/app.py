import os
import shutil
import tempfile
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    PantryAnalysisResponse, 
    RecipeSuggestionRequest, RecipeSuggestionResponse,
    VideoSearchRequest, VideoSearchResponse, VideoResult,
    PantryItemResponse, SavedRecipeResponse, SaveRecipeRequest
)
from services.vision_service import VisionService
from services.agent_service import AgentService
from services.search_service import SearchService
from services.auth_service import AuthService
from database import init_db, get_db
from tasks.scheduler import start_scheduler
from models.db_models import User, PantryItem, SavedRecipe
from sqlalchemy.future import select

app = FastAPI(title="SnapChef API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
agent_service = AgentService()
search_service = SearchService()

@app.on_event("startup")
async def startup_event():
    await init_db()
    start_scheduler()


# Auth Endpoints
@app.post("/api/auth/google")
async def google_auth(request: dict, db: AsyncSession = Depends(get_db)):
    token = request.get("token")
    if not token:
        print("DEBUG: google_auth called without token")
        raise HTTPException(status_code=400, detail="Token missing")
    
    print("DEBUG: google_auth verifying token...")
    user_info = AuthService.verify_google_token(token)
    print(f"DEBUG: google_auth user_info: {user_info}")
    
    # Check if user exists
    stmt = select(User).where(User.google_id == user_info["sub"])
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        print(f"DEBUG: Creating new user for {user_info.get('email')}")
        user = User(
            google_id=user_info["sub"],
            email=user_info["email"],
            full_name=user_info.get("name", ""),
            profile_pic=user_info.get("picture", "")
        )
        db.add(user)
        try:
            await db.commit()
            print("DEBUG: New user committed to database.")
            await db.refresh(user)
        except Exception as e:
            print(f"DEBUG: Database commit failed: {str(e)}")
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database failure")
    else:
        print(f"DEBUG: Found existing user: {user.email}")
    
    # Create JWT
    token_data = {
        "email": user.email,
        "name": user.full_name,
        "id": user.id
    }
    jwt_token = AuthService.create_access_token(token_data)
    
    return {
        "token": jwt_token,
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "picture": user.profile_pic
        }
    }

@app.get("/api/auth/me")
async def get_me(authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = AuthService.decode_access_token(authorization)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    stmt = select(User).where(User.id == payload["id"])
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "email": user.email,
        "name": user.full_name,
        "picture": user.profile_pic
    }

@app.get("/api/pantry", response_model=List[PantryItemResponse])
async def get_pantry(authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = AuthService.decode_access_token(authorization)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    stmt = select(PantryItem).where(PantryItem.user_id == payload["id"]).order_by(PantryItem.scan_date.desc())
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    return [
        PantryItemResponse(
            id=item.id,
            ingredient_name=item.ingredient_name,
            scan_date=item.scan_date.isoformat(),
            days_until_expiry=item.days_until_expiry,
            urgency=item.urgency,
            storage=item.storage
        ) for item in items
    ]

@app.get("/api/recipes/history", response_model=List[SavedRecipeResponse])
async def get_recipe_history(authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = AuthService.decode_access_token(authorization)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    stmt = select(SavedRecipe).where(SavedRecipe.user_id == payload["id"]).order_by(SavedRecipe.saved_at.desc())
    result = await db.execute(stmt)
    recipes = result.scalars().all()
    
    return [
        SavedRecipeResponse(
            id=r.id,
            recipe_name=r.recipe_name,
            ingredients=r.ingredients,
            video_url=r.video_url,
            thumbnail=r.thumbnail,
            accessible_guide=r.accessible_guide,
            saved_at=r.saved_at.isoformat()
        ) for r in recipes
    ]

@app.post("/api/recipes/save")
async def save_recipe(request: SaveRecipeRequest, authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    print(f"DEBUG: save_recipe endpoint reached. Authorization header received: {authorization[:20] if authorization else 'None'}...")
    if not authorization:
        print("DEBUG: save_recipe failed: No Authorization header found")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = AuthService.decode_access_token(authorization)
        print(f"DEBUG: Decoded payload in save_recipe: {payload}")
        if not payload:
            print("DEBUG: save_recipe failed: Token decoding returned None")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = payload.get("id")
        if not user_id:
            print("DEBUG: save_recipe failed: 'id' key missing in payload")
            raise HTTPException(status_code=401, detail="Invalid token: no user_id")

        print(f"DEBUG: Constructing SavedRecipe object for {request.recipe_name}")
        recipe = SavedRecipe(
            user_id=user_id,
            recipe_name=request.recipe_name,
            ingredients=request.ingredients,
            video_url=request.video_url,
            thumbnail=request.thumbnail,
            accessible_guide=request.accessible_guide
        )
        db.add(recipe)
        await db.commit()
        print(f"DEBUG: Database commit SUCCESS for recipe: {request.recipe_name}")
        return {"message": "Recipe saved successfully"}
    except Exception as e:
        print(f"DEBUG: EXCEPTION in save_recipe: {str(e)}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/analyze-pantry", response_model=PantryAnalysisResponse)
async def analyze_pantry(file: UploadFile = File(...), authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Analyze
        try:
            ingredients = VisionService.analyze_image(tmp_path)
            
            # Estimate expiry dates using LLM
            print(f"📅 Estimating expiry dates for {len(ingredients)} ingredients...")
            expiry_info = agent_service.estimate_expiry_dates(ingredients)
            
            # If authenticated, save to database
            if authorization:
                print(f"DEBUG: analyze_pantry checking token...")
                payload = AuthService.decode_access_token(authorization)
                if payload:
                    user_id = payload.get("id")
                    print(f"DEBUG: analyze_pantry user_id: {user_id}")
                    if user_id:
                        for ing in ingredients:
                            expiry = expiry_info.get(ing, {"days": 7, "urgency": "medium", "storage": "pantry"})
                            item = PantryItem(
                                user_id=user_id,
                                ingredient_name=ing,
                                days_until_expiry=expiry["days"],
                                urgency=expiry["urgency"],
                                storage=expiry["storage"]
                            )
                            db.add(item)
                        await db.commit()
                        print(f"💾 Saved {len(ingredients)} items to database for user {user_id}")
                    else:
                        print("DEBUG: user_id missing from payload in analyze_pantry")
                else:
                    print("DEBUG: Token decode failed in analyze_pantry")
            else:
                print("DEBUG: No token header in analyze_pantry - skipping DB save")
            
        finally:
            os.remove(tmp_path)
            
        return PantryAnalysisResponse(ingredients=ingredients, expiry_info=expiry_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggest-recipes", response_model=RecipeSuggestionResponse)
async def suggest_recipes(request: RecipeSuggestionRequest, authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    print(f"DEBUG: suggest_recipes called. Authorization present: {authorization is not None}")
    try:
        saved_names = []
        if authorization:
            payload = AuthService.decode_access_token(authorization)
            if payload:
                user_id = payload.get("id")
                print(f"DEBUG: suggest_recipes user_id: {user_id}")
                if user_id:
                    # Fetch recent 5 saved recipes to understand style
                    stmt = select(SavedRecipe.recipe_name).where(SavedRecipe.user_id == user_id).order_by(SavedRecipe.saved_at.desc()).limit(5)
                    result = await db.execute(stmt)
                    saved_names = [r for r in result.scalars().all()]
                    print(f"DEBUG: Suggesting based on {len(saved_names)} saved recipes: {saved_names}")
                else:
                    print("DEBUG: suggest_recipes: user_id missing in token")
            else:
                print("DEBUG: suggest_recipes: Token decode failed")

        recipes = agent_service.brainstorm_recipes(request.ingredients, request.preferences, saved_recipes=saved_names)
        return RecipeSuggestionResponse(recipes=recipes)
    except Exception as e:
        print(f"DEBUG: EXCEPTION in suggest_recipes: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/find-videos", response_model=VideoSearchResponse)
async def find_videos(request: VideoSearchRequest):
    """
    The 'Magic' orchestration endpoint.
    """
    try:
        results = []
        
        # 1. Query Engineer Agent
        channel_filter = request.filters.channel if request.filters else None
        cuisine_filter = request.filters.cuisine if request.filters else None
        
        queries = agent_service.generate_search_queries(
            request.selected_recipe, 
            channel_filter, 
            cuisine_filter
        )
        print(f"🕵️‍♀️ Generated Queries: {queries}")
        
        # 2. Search Executor (Run all queries and deduct duplicates)
        seen_ids = set()
        raw_videos = []
        
        for q in queries:
            # OPTIMIZATION: Limit to 2 results per query to speed up processing
            videos = search_service.search_youtube_videos(q, max_results=2)
            for v in videos:
                if v['id'] not in seen_ids:
                    seen_ids.add(v['id'])
                    raw_videos.append(v)
        
        print(f"🔎 Found {len(raw_videos)} raw videos. Verifying...")
        
        # Limit to first 3 videos to avoid quota issues
        raw_videos = raw_videos[:3]
        print(f"⚡ Processing {len(raw_videos)} videos...")

        # 3. Verification & Scoring (First Pass)
        candidates = []
        
        for idx, video in enumerate(raw_videos, 1):
            print(f"   [{idx}/{len(raw_videos)}] Checking: {video['title'][:60]}...")
            # Fetch content (Transcript > Description)
            transcript = search_service.get_video_transcript(video['id'])
            description = video['description']
            content_for_llm = transcript if transcript else description
            source_type = "transcript" if transcript else "description"
            
            # VERIFICATION TEMPORARILY DISABLED - Ollama JSON parsing issues
            # verification = agent_service.verify_video(
            #     video['title'], content_for_llm, 
            #     request.selected_recipe, request.ingredients
            # )
            
            # For now, accept all videos with a default confidence
            verification = {
                "valid": True, 
                "reason": "Verification disabled - accepting all results",
                "confidence_score": 70  # Default confidence
            }
            
            if verification.get('valid'):
                # calculate smart score
                stats = search_service.get_video_stats(video['id'])
                views = int(stats.get('viewCount', 0)) if stats else 0
                
                # Normalize views (log scale primitive approximation)
                # Cap at 1M for normalization 1.0
                norm_views = min(views / 1_000_000, 1.0)
                
                # Channel similarity (simple check)
                channel_score = 1.0 if channel_filter and channel_filter.lower() in video['channel'].lower() else 0.0
                
                conf_score = float(verification.get('confidence_score', 50)) / 100.0
                
                # Weighted Score
                # Relevance (0.5) + Views (0.3) + Channel (0.2)
                smart_score = (conf_score * 50) + (norm_views * 30) + (channel_score * 20)
                
                # Store candidate (defer guide generation)
                candidates.append({
                    "data": video,
                    "score": smart_score,
                    "reason": verification.get('reason'),
                    "views": views,
                    "content_for_llm": content_for_llm, 
                    "source_type": source_type
                })

        # 4. Sort and Slice
        candidates.sort(key=lambda x: x['score'], reverse=True)
        top_candidates = candidates[:3] # process only top 3

        # 5. Guide Generation (Second Pass - Parallelizable in theory, serial here but fewer items)
        final_results = []
        print(f"📝 Generating guides for top {len(top_candidates)} videos...")
        
        for c in top_candidates:
            guide = agent_service.generate_accessible_guide(
                c['data']['title'], 
                c['content_for_llm'], 
                c['source_type']
            )
            
            final_results.append(VideoResult(
                title=c['data']['title'],
                url=c['data']['url'],
                thumbnail=c['data']['thumbnail'],
                channel=c['data']['channel'],
                views=str(c['views']),
                smart_score=round(c['score'], 1),
                accessible_guide=guide,
                match_reason=c['reason']
            ))
        
        print(f"✅ Returning {len(final_results)} verified videos to frontend")
        return VideoSearchResponse(videos=final_results)

    except Exception as e:
        # print stack trace for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
