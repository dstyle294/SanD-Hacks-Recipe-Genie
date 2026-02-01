import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

class AgentService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.7
        )

    def brainstorm_recipes(self, ingredients: list[str], preferences: str) -> list[str]:
        # Aligning with main.py/RecipeAgent.py workflow
        ingredients_str = ", ".join(ingredients) if isinstance(ingredients, list) else str(ingredients)
        
        prompt = (
            f"I have these ingredients: {ingredients_str}. "
            f"The user wants: {preferences}. "
            "Suggest 3 specific recipe names that successfully use THESE ingredients. "
            "STRICT CONSTRAINT: Do not suggest recipes that require other MAIN ingredients (like meats, veg, or heavy dairy) not listed here. "
            "Assume I have basic pantry staples (oil, salt, pepper, water, basic spices). "
            "Return ONLY a Python list of strings, e.g. ['Recipe A', 'Recipe B']."
        )
        response = self.llm.invoke(prompt).content
        try:
            start = response.find('[')
            end = response.find(']') + 1
            return eval(response[start:end])
        except:
            return [response]

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
        
        response = self.llm.invoke(prompt).content
        try:
            start = response.find('[')
            end = response.find(']') + 1
            return eval(response[start:end])
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
            response = self.llm.invoke(prompt).content
            clean_json = response.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_json)
        except:
            return {"valid": False, "reason": "LLM validation failed", "confidence_score": 0}

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
        return self.llm.invoke(prompt).content
