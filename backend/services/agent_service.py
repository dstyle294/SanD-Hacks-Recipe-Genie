import os
import json
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

class AgentService:
    def __init__(self):
        # Try Ollama first, fallback to Gemini if it fails
        self.primary_llm = None
        self.fallback_llms = []
        
        # Primary: Ollama (free, local)
        try:
            self.primary_llm = ChatOllama(
                model="llama3.2",
                temperature=0.7,
                base_url="http://localhost:11434",
                timeout=5  # Quick timeout to detect if Ollama is down
            )
            print("✅ Using Ollama (llama3.2) as primary LLM")
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
        
        # Fallback: Gemini models (if API key exists)
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            gemini_models = [
                "gemini-2.5-flash-preview",
                "gemini-3-flash-preview", 
                "gemini-2.5-flash-lite",
                "gemini-1.5-flash",  # Stable fallback
            ]
            for model in gemini_models:
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=model,
                        api_key=gemini_key,
                        temperature=0.7
                    )
                    self.fallback_llms.append((model, llm))
                except:
                    pass
            if self.fallback_llms:
                print(f"✅ Gemini fallback configured with {len(self.fallback_llms)} models")
        
        if not self.primary_llm and not self.fallback_llms:
            raise RuntimeError("No LLM available! Install Ollama or set GEMINI_API_KEY")
    
    def _invoke_with_fallback(self, prompt: str) -> str:
        """Try primary LLM first, then fallback to Gemini models."""
        # Try Ollama first
        if self.primary_llm:
            try:
                response = self.primary_llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                print(f"⚠️ Ollama failed: {e}, trying Gemini fallback...")
        
        # Try Gemini fallbacks
        for model_name, llm in self.fallback_llms:
            try:
                print(f"   Trying Gemini: {model_name}...")
                response = llm.invoke(prompt)
                text = response.content if hasattr(response, 'content') else str(response)
                print(f"   ✅ Success with {model_name}")
                return text
            except Exception as e:
                print(f"   ❌ {model_name} failed: {str(e)[:100]}")
                continue
        
        raise RuntimeError("All LLMs failed (Ollama + all Gemini models)")

    def brainstorm_recipes(self, ingredients: list[str], preferences: str, saved_recipes: Optional[list[str]] = None) -> list[dict]:
        # Aligning with main.py/RecipeAgent.py workflow
        ingredients_str = ", ".join(ingredients) if isinstance(ingredients, list) else str(ingredients)
        
        saved_context = ""
        if saved_recipes:
            saved_context = f"The user has previously saved these recipes: {', '.join(saved_recipes)}. Use these to understand their taste and style, but do not suggest them again. "

        prompt = (
            f"I have these ingredients: {ingredients_str}. "
            f"The user wants: {preferences}. "
            f"{saved_context}"
            "Suggest 3 specific recipe names that successfully use THESE ingredients. "
            "For each recipe, provide estimated nutritional information (calories, protein, carbs, fat) and a health score (0-100).\n\n"
            "Return a JSON object with a 'recipes' key containing a list of objects. Each object should have:\n"
            "- 'name': (string)\n"
            "- 'nutritional_info': {'calories': int, 'protein': int, 'carbs': int, 'fat': int}\n"
            "- 'health_score': int (0-100)\n\n"
            "Example format: {\"recipes\": [{\"name\": \"Salad\", \"nutritional_info\": {\"calories\": 200, \"protein\": 5, \"carbs\": 10, \"fat\": 15}, \"health_score\": 95}]}"
            "STRICT CONSTRAINT: Do not suggest recipes that require other MAIN ingredients not listed here.\n"
            "Return ONLY valid JSON, no other text."
        )
        text_content = self._invoke_with_fallback(prompt)
        print(f"🤖 LLM Response: {text_content[:200]}...")
        
        try:
            # Clean and extract JSON
            clean_json = text_content.replace('```json', '').replace('```', '').strip()
            if '{' in clean_json:
                start = clean_json.find('{')
                end = clean_json.rfind('}') + 1
                clean_json = clean_json[start:end]
            
            data = json.loads(clean_json)
            recipes = data.get("recipes", [])
            print(f"✅ Parsed {len(recipes)} recipes with nutritional info")
            return recipes
        except Exception as e:
            print(f"❌ Parse Error: {e}")
            # Fallback to simple list if JSON fails (though schema expects dict now)
            return [{"name": "Error suggestions - Check logs", "nutritional_info": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}, "health_score": 0}]
    
    def estimate_expiry_dates(self, ingredients: list[str]) -> dict[str, dict]:
        """
        Estimate typical shelf life and urgency for each ingredient.
        Returns dict with ingredient name as key and expiry info as value.
        """
        prompt = (
            f"For each of these ingredients: {', '.join(ingredients)}\n\n"
            "Estimate the typical shelf life assuming they were purchased fresh today. "
            "Consider common storage conditions (refrigerated for perishables, pantry for dry goods).\n\n"
            "Return a JSON object where each ingredient name is a key, and the value is an object with:\n"
            "- 'days': estimated days until expiry (number)\n"
            "- 'urgency': 'high' (use within 3 days), 'medium' (3-7 days), or 'low' (7+ days)\n"
            "- 'storage': storage method ('refrigerate', 'pantry', 'freezer')\n\n"
            "Example: {\"tomatoes\": {\"days\": 5, \"urgency\": \"medium\", \"storage\": \"refrigerate\"}}\n"
            "Return ONLY valid JSON, no other text."
        )
        
        try:
            text_content = self._invoke_with_fallback(prompt)
            print(f"📅 Expiry estimation response: {text_content[:200]}")
            
            # Clean and extract JSON
            clean_json = text_content.replace('```json', '').replace('```', '').strip()
            if '{' in clean_json:
                start = clean_json.find('{')
                end = clean_json.rfind('}') + 1
                clean_json = clean_json[start:end]
            
            expiry_data = json.loads(clean_json)
            print(f"✅ Parsed expiry data for {len(expiry_data)} ingredients")
            return expiry_data
        except Exception as e:
            print(f"❌ Expiry estimation error: {e}")
            # Return default estimates
            return {
                ing: {"days": 7, "urgency": "medium", "storage": "pantry"} 
                for ing in ingredients
            }

    def generate_search_queries(self, recipe: str, channel_filter: str = None, cuisine_filter: str = None) -> list[str]:
        """
        Query Engineer Agent: Generates optimized search queries.
        """
        prompt = (
            f"I need to find a YouTube video tutorial for the recipe: '{recipe}'.\n"
        )
        if channel_filter:
            prompt += f"Constraint: The video MUST be from the channel '{channel_filter}' (or very similar).\n"
        if cuisine_filter:
            prompt += f"Constraint: The style/cuisine should be '{cuisine_filter}'.\n"
        
        prompt += (
            "Generate 3 highly optimized YouTube search queries to find the best result. "
            "Consider accessibility, clarity, and the filters provided. "
            "Return ONLY a Python list of strings."
        )
        
        text_content = self._invoke_with_fallback(prompt)
        try:
            start = text_content.find('[')
            end = text_content.find(']') + 1
            return eval(text_content[start:end])
        except:
            return [f"{recipe} recipe"]

    def verify_video(self, video_title: str, video_content: str, recipe_name: str, ingredients: list[str]) -> dict:
        """
        Verification Agent: Checks if the video actually teaches the recipe.
        video_content: can be transcript or description.
        """
        prompt = (
            f"I am evaluating a recipe video titled '{video_title}'. "
            f"The user is looking for a recipe for: {recipe_name}. "
            f"The User ONLY has these ingredients available: {ingredients} (plus basic staples like oil/spices/water). "
            f"Here is the content info (transcript start or description): \n\n{video_content[:2000]}...\n\n"
            "1. Does this video seem to be teaching how to make that specific recipe?\n"
            "2. CRITICAL: Does the recipe in the video require MAJOR ingredients that are missing from the user's list? (Ignore minor garnishes or optional items).\n"
            "Return JSON with 'valid' (boolean - set to false if major ingredients missing), 'reason' (string), and 'confidence_score' (number 0-100)."
        )
        
        try:
            response = self.llm.invoke(prompt)
            # Extract text content properly
            text_content = response.content if hasattr(response, 'content') else str(response)
            print(f"\n🔍 Verifying: {video_title[:60]}")
            print(f"📄 LLM Response (first 300 chars): {text_content[:300]}")
            
            clean_json = text_content.replace('```json', '').replace('```', '').strip()
            
            # Try to find JSON object in the response
            if '{' in clean_json:
                start = clean_json.find('{')
                end = clean_json.rfind('}') + 1
                clean_json = clean_json[start:end]
            
            result = json.loads(clean_json)
            print(f"✅ Parsed: valid={result.get('valid')}, score={result.get('confidence_score')}")
            return result
        except Exception as e:
            print(f"❌ Verification Error for '{video_title[:60]}': {e}")
            print(f"   Raw response: {text_content[:200] if 'text_content' in locals() else 'N/A'}")
            return {"valid": False, "reason": f"LLM validation failed: {str(e)}", "confidence_score": 0}

    def generate_accessible_guide(self, video_title: str, content: str, source_type: str = "transcript") -> str:
        prompt = (
            f"Create a clear, step-by-step recipe based on this content ({source_type}). "
            f"Video Title: {video_title}\n"
            f"Content: {content[:10000]}\n\n"
            "The reader might be visually impaired, so focus on:"
            "1. Clear, descriptive instructions."
            "2. Mentioning sensory cues (smell, sound, texture)."
            "3. List ingredients first."
            "4. Numbered steps."
            "Output the recipe in clean Markdown format."
        )
        return self._invoke_with_fallback(prompt)
