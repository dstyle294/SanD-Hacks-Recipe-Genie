import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

class SearchService:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

    def search_youtube_videos(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Searches YouTube for a specific query and returns detailed video info.
        """
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
            snippet = item['snippet']
            
            videos.append({
                "id": video_id,
                "title": snippet['title'],
                "description": snippet.get('description', ''),
                "channel": snippet['channelTitle'],
                "thumbnail": snippet['thumbnails']['high']['url'],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                # "publishTime": snippet['publishTime'] # Could be useful for scoring later
            })
        return videos
    
    def get_video_stats(self, video_id: str) -> dict:
        """
        Fetches view count and other stats for scoring.
        """
        try:
            request = self.youtube.videos().list(
                part="statistics",
                id=video_id
            )
            response = request.execute()
            if response['items']:
                return response['items'][0]['statistics']
        except:
            pass
        return {}

    def get_video_transcript(self, video_id: str) -> str:
        """
        Fetches transcript. Returns None if not available.
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript])
            return full_text[:15000] # Limit context
        except Exception:
            return None
