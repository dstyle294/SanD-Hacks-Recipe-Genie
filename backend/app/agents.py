import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from eyepop import EyePopSdk
from eyepop.worker.worker_types import Pop, InferenceComponent

class VisionAgent:
    def __init__(self):
        self.eyepop_api_key = os.getenv("EYEPOP_API_KEY", "").strip()
        
    async def detect_ingredients(self, image_path: str) -> List[str]:
        if not self.eyepop_api_key:
            msg = "Missing EyePop API Key."
            print(msg)
            raise ValueError(msg)
            
        print(f"Uploading to EyePop... (Worker Endpoint)")
        
        prompt = (
            "Analyze the image. "
            "Ignore people, faces, hands, body parts, and human features. "
            "Ignore background objects not related to items or products. "
            "If the image is a bill or receipt, list the items on the bill. "
            "If the image is of a shelf or store display, list the products visible. "
            "If the image is of a single product, list that product only. "
            "If the image is unclear or contains no items, respond with NO OBJECTS DETECTED. "
            "Otherwise, detect and list only physical items or products visible. "
            "Do not include humans or body parts as objects. "
            "Use clear class labels only. "
            "If unsure, set classLabel to null."
        )

        try:
            # Synchronous SDK usage wrapped in async function
            # Alternatively run in executor if blocking is an issue, but for now direct call
            with EyePopSdk.workerEndpoint(api_key=self.eyepop_api_key) as endpoint:
                endpoint.set_pop(
                    Pop(components=[
                        InferenceComponent(
                            id=1,
                            ability="eyepop.image-contents:latest",
                            params={"prompts": [{"prompt": prompt}]}
                        )
                    ])
                )
                
                result = endpoint.upload(image_path).predict()
                
                # Parse result
                ingredients = []
                # Check 'classes' or 'objects' depending on result structure from this model
                # The user's snippet checks 'classes' from result
                for c in result.get("classes", []):
                    label = c.get("classLabel")
                    if label:
                        ingredients.append(label.lower())
                
                # Also check 'objects' just in case
                for item in result.get('objects', []):
                    if 'classLabel' in item:
                        ingredients.append(item['classLabel'].lower())
                    elif 'label' in item:
                        ingredients.append(item['label'].lower())

                print(f"EyePop detected: {ingredients}")
                if not ingredients:
                    print(f"Full EyePop Result for debugging: {result}")
                    
                return list(set(ingredients))
        except Exception as e:
            print(f"EyePop Error: {e}")
            raise e

class RecipeAgent:
    def __init__(self):
        # Primary Gemini API
        self.primary_llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.4
        )
        
        # Backup Gemini API
        backup_key = os.getenv('GEMINI_BACKUP_API_KEY')
        self.backup_gemini = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=backup_key,
            temperature=0.4
        ) if backup_key else None
        
        # Grok API (using OpenAI-compatible interface)
        self.grok_api_key = os.getenv('GROK_API_KEY')
        
    def _invoke_with_fallback(self, prompt: str) -> str:
        """Try multiple AI providers in sequence until one succeeds"""
        providers = [
            ("Primary Gemini", self.primary_llm),
            ("Backup Gemini", self.backup_gemini),
            ("Grok AI", None)  # Will handle Grok separately
        ]
        
        for name, llm in providers:
            if llm is None and name != "Grok AI":
                continue
                
            try:
                if name == "Grok AI" and self.grok_api_key:
                    print(f"Trying {name}...")
                    return self._invoke_grok(prompt)
                elif llm:
                    print(f"Trying {name}...")
                    response = llm.invoke(prompt)
                    print(f"✓ {name} succeeded")
                    return response.content
                else:
                    print(f"Skipping {name} (not configured)")
            except Exception as e:
                import traceback
                print(f"✗ {name} failed: {str(e)}")
                traceback.print_exc()
                continue
        
        raise Exception("All AI providers failed")
    
    def _invoke_grok(self, prompt: str) -> str:
        """Call Grok AI using OpenAI-compatible API"""
        import httpx
        
        response = httpx.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4
            },
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def get_expiry_dates(self, ingredients: List[str]) -> Dict[str, int]:
        prompt = (
            f"Given these food ingredients: {', '.join(ingredients)}. "
            "Predict a realistic shelf life (in days from today) for each ingredient IF stored normally (refrigerated for perishables, room temp for staples). "
            "BE SPECIFIC AND VARIED. Do not return the same number for all ingredients unless they are identical categories. "
            "Examples: Milk (5-7), Bread (3-5), Canned Beans (365), Fresh Spinach (3-4). "
            "Return ONLY a JSON object where keys are ingredient names and values are integers (days)."
            f"Current context: Today is {datetime.now().strftime('%Y-%m-%d')}."
        )
        try:
            content = self._invoke_with_fallback(prompt)
            # Simple cleaning for JSON
            content = content.replace('```json', '').replace('```', '').strip()
            result = json.loads(content)
            # Ensure all values are integers
            return {str(k): int(v) for k, v in result.items()}
        except Exception as e:
            print(f"All AI providers failed (Expiry): {e}")
            # Fallback with some variety
            fallbacks = {"milk": 5, "bread": 4, "meat": 3, "egg": 14, "vegetable": 5, "fruit": 5}
            return {ing: fallbacks.get(ing.lower(), 7) for ing in ingredients}

    async def generate_recipes(self, ingredients: List[Dict[str, Any]], preferences: str, use_pantry: bool = False) -> List[Dict[str, Any]]:
        if not ingredients:
            return []
            
        ing_names = [i["name"] for i in ingredients]
        # Calculate expiring soon for real-world logic
        today = datetime.now().date()
        expiring_soon = []
        for i in ingredients:
            try:
                if i.get("expiry") and (datetime.fromisoformat(i["expiry"]).date() - today).days <= 3:
                    expiring_soon.append(i["name"])
            except:
                continue
        
        pantry_context = "You can ALSO assume the user has basic pantry staples like salt, pepper, oil, water, and flour." if use_pantry else "You CANNOT use any ingredient not in the list."
        
        prompt = (
            f"I have these EXACT ingredients: {', '.join(ing_names)}. "
            f"Ingredients expiring soon: {', '.join(expiring_soon)}. "
            f"{pantry_context} "
            f"User preferences: {preferences}. "
            "STRICT CONSTRAINT: You must ONLY use the provided ingredients and basic pantry staples (if allowed). "
            "DO NOT include recipes that require other main ingredients (e.g. do not suggest Chicken Parmesan if I only have Tomato and Cheese). "
            "If a recipe usually requires an ingredient I don't have, find a substitute from my list or skip that recipe. "
            "Generate 5 recipes. For each recipe, provide: \n"
            "1. 'title'\n"
            "2. 'description' (3-4 lines)\n"
            "3. 'image_prompt' (detailed description for AI image generation)\n"
            "4. 'health_score' (A number 1-100 based on nutritional value and healthiness. Higher is better.)\n"
            "5. 'nutrition' (object with 'calories' (kcal), 'protein' (g), 'carbs' (g), 'fat' (g) - estimated per serving)\n"
            "Return the list as valid JSON.\n"
            "Example: [{'title': 'Recipe Name', 'description': '...', 'image_prompt': '...', 'health_score': 85, 'nutrition': {'calories': 350, 'protein': 25, 'carbs': 40, 'fat': 12}}]"
        )
        try:
            content = self._invoke_with_fallback(prompt)
            content = content.replace('```json', '').replace('```', '').strip()
            recipes = json.loads(content)
            
            # Post-process to add real images
            search_agent = SearchAgent()
            for rec in recipes:
                try:
                    # 1. Try DuckDuckGo Search (Proxied)
                    rec['image_url'] = await search_agent.find_recipe_image(rec['title'])
                    
                    # 2. If search returned the placeholder, try catching the YouTube thumbnail instead
                    if "placehold.co" in rec['image_url']:
                        best_video = await search_agent.find_best_video(rec['title'])
                        if best_video.get('thumbnail'):
                            rec['image_url'] = best_video['thumbnail']
                except Exception as img_err:
                    print(f"Failed to fetch image for {rec['title']}: {img_err}")
                    rec['image_url'] = f"https://placehold.co/800x600/black/gold?text={rec['title'].replace(' ', '+')}"
            
            return recipes
        except Exception as e:
            print(f"All AI providers failed (Recipes): {e}")
            return []

    async def generate_final_recipe(self, selected_recipe: str, video_context: str) -> str:
        prompt = (
            f"You are a master chef and precise transcriber. Convert the following transcript/video context into a structured, detailed recipe: \n"
            f"{video_context}\n\n"
            "STRICT CONSTRAINTS:\n"
            "1. FOLLOW THE TRANSCRIPT CONTENT EXACTLY. If the video describes a different dish than the title, follow the video contents.\n"
            "2. DO NOT add 'Chef's Notes', 'Inspiration', or 'Zero Waste Tips'.\n"
            "3. DO NOT suggest alternative recipes.\n"
            "4. The output must be valid Markdown containing: Title, Ingredients (as described in video), and Step-by-step instructions.\n"
            "5. If there is no transcript available, use the title and video stats to infer the best possible recipe for that specific video style."
        )
        try:
            return self._invoke_with_fallback(prompt)
        except Exception as e:
            return f"Error generating recipe: {str(e)}"


class SearchAgent:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

    async def find_best_video(self, recipe_title: str) -> Dict[str, Any]:
        # 1. Search Query
        search_query = f"best {recipe_title} recipe tutorial"
        request = self.youtube.search().list(
            q=search_query,
            part='snippet',
            type='video',
            maxResults=3,
            order='relevance'
        )
        response = request.execute()
        
        video_candidates = []
        for item in response['items']:
            video_id = item['id']['videoId']
            # Get video stats for view count
            stats_request = self.youtube.videos().list(
                part='statistics',
                id=video_id
            )
            stats_response = stats_request.execute()
            views = int(stats_response['items'][0]['statistics'].get('viewCount', 0))
            
            # Fetch transcript if possible
            transcript_text = "No transcript available."
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                # Truncate transcript to ~10k chars to avoid hitting provider limits
                transcript_text = " ".join([t['text'] for t in transcript_list])[:10000]
            except Exception as e:
                print(f"Could not fetch transcript for {video_id}: {e}")
            
            # YouTube Thumbnail is a great fallback for the recipe image
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            context = f"Title: {item['snippet']['title']}\nViews: {views}\nTranscript Content: {transcript_text}\n"
            
            video_candidates.append({
                "id": video_id,
                "title": item['snippet']['title'],
                "views": views,
                "context": context,
                "thumbnail": thumbnail_url
            })
            
        # 2. Simply pick the most viewed video
        if video_candidates:
            best_video = max(video_candidates, key=lambda v: v['views'])
            return best_video
        
        # Fallback if no videos found
        return {
            "id": "",
            "title": f"How to make {recipe_title}",
            "views": 0,
            "context": f"Recipe: {recipe_title}"
        }

    async def find_recipe_image(self, recipe_title: str) -> str:
        """Find a real image for the recipe using DuckDuckGo"""
        print(f"Searching image for: {recipe_title}")
        try:
            with DDGS() as ddgs:
                # Search for images with the recipe title
                # Try fetching a few to ensure we get a working link
                results = list(ddgs.images(
                    keywords=f"{recipe_title} cooked food high quality",
                    max_results=3,
                    safesearch="on"
                ))
                
                if results:
                    for res in results:
                        if res.get('image'):
                             # Use weserv proxy to bypass hotlinking protection
                             raw_url = res['image']
                             return f"https://images.weserv.nl/?url={raw_url}&w=800&h=600&fit=cover"
    
        except Exception as e:
            print(f"Image Search Error for {recipe_title}: {e}")
            
        # Fallback if search fails
        return f"https://placehold.co/800x600/black/gold?text={recipe_title.replace(' ', '+')}"
