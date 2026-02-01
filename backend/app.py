import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    PantryAnalysisResponse, 
    RecipeSuggestionRequest, RecipeSuggestionResponse,
    VideoSearchRequest, VideoSearchResponse, VideoResult
)
from backend.services.vision_service import VisionService
from backend.services.agent_service import AgentService
from backend.services.search_service import SearchService

app = FastAPI(title="Recipe Genie API")

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

@app.post("/api/analyze-pantry", response_model=PantryAnalysisResponse)
async def analyze_pantry(file: UploadFile = File(...)):
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Analyze
        try:
            ingredients = VisionService.analyze_image(tmp_path)
            # Remove generic "text-item" if it's just noise, or keep it.
            # Logic to clean up ingredients could be added here.
        finally:
            os.remove(tmp_path)
            
        return PantryAnalysisResponse(ingredients=ingredients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggest-recipes", response_model=RecipeSuggestionResponse)
async def suggest_recipes(request: RecipeSuggestionRequest):
    try:
        recipes = agent_service.brainstorm_recipes(request.ingredients, request.preferences)
        return RecipeSuggestionResponse(recipes=recipes)
    except Exception as e:
        # print stack trace for debugging
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

        # 3. Verification & Scoring (First Pass)
        candidates = []
        
        for video in raw_videos:
            # Fetch content (Transcript > Description)
            transcript = search_service.get_video_transcript(video['id'])
            description = video['description']
            content_for_llm = transcript if transcript else description
            source_type = "transcript" if transcript else "description"
            
            # Verify
            verification = agent_service.verify_video(
                video['title'], content_for_llm, 
                request.selected_recipe, request.ingredients
            )
            
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
