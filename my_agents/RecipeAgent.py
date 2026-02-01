from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import json, os




class SmartKitchenChain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite", 
            api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.7
        )
        # Store conversation history manually
        self.chat_history = []
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

    def chat(self, user_input):
        # Add user message to history
        self.chat_history.append(HumanMessage(content=user_input))
        
        # Get response from LLM with full history
        response = self.llm.invoke(self.chat_history)
        
        # Add AI response to history
        self.chat_history.append(response)
        
        return response.content
  
    def search_youtube(self, query, max_results=3):
        """Tools: Searches YouTube for a specific query"""
        print(f"🔎 Searching YouTube for: '{query}'...")
        request = self.youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results
        )
        response = request.execute()
        
        videos = []
        for item in response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            description = item['snippet'].get('description', '')
            url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({
                "title": title, 
                "url": url, 
                "id": video_id, 
                "description": description
            })
        return videos

    def get_video_transcript(self, video_id):
        """Tools: Fetches transcript to let Gemini 'read' the video"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            # Combine into a single string for the LLM
            full_text = " ".join([entry['text'] for entry in transcript])
            return full_text[:10000] # Limit char count to save context window
        except Exception:
            return None

    def verify_video_relevance(self, video, recipe_name, ingredients):
        """
        Verifies if the video actually matches the recipe name and ingredients
        using Title + Transcript (or Description if Transcript missing)
        """
        transcript = self.get_video_transcript(video['id'])
        
        # Prepare context
        if transcript:
            context = f"Transcript start: \n{transcript[:2000]}..."
        else:
            context = f"Video Description: \n{video.get('description', 'No description available.')}"
            
        prompt = (
            f"I am evaluating a recipe video titled '{video['title']}'. "
            f"The user is looking for a recipe for: {recipe_name}. "
            f"Known ingredients available: {ingredients}. "
            f"Here is the content info: \n\n{context}\n\n"
            "Does this video seem to be teaching how to make that specific recipe (or very close)? "
            "Return JSON with 'valid' (boolean) and 'reason' (string)."
        )
        
        try:
            response = self.llm.invoke(prompt).content
            clean_json = response.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_json)
        except:
            return {"valid": False, "reason": "LLM validation failed"}

    def generate_accessible_recipe(self, video):
        """
        Generates a step-by-step text recipe from the video transcript/desc,
        tailored for accessibility (clear, descriptive).
        """
        transcript = self.get_video_transcript(video['id'])
        
        if transcript:
            source_material = f"Transcript: {transcript}"
            instruction_extra = "based primarily on this video transcript"
        else:
            source_material = f"Description: {video.get('description', '')}"
            instruction_extra = "based on the video title and description, using your general culinary knowledge for missing details"

        prompt = (
            f"Create a clear, step-by-step recipe {instruction_extra}. "
            f"Video Title: {video['title']}\n"
            f"{source_material}\n\n"
            "The reader might be visually impaired, so focus on:"
            "1. Clear, descriptive instructions."
            "2. Mentioning sensory cues (smell, sound, texture) if possible."
            "3. List ingredients first."
            "4. Numbered steps."
            "Output the recipe in clean Markdown format."
        )
        
        return self.llm.invoke(prompt).content
