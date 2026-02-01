# main.py
import os
import json
from dotenv import load_dotenv

# Import your custom modules
from my_agents.RecipeAgent import SmartKitchenChain 
from my_eyepop.ObjDet import getItems # Assuming this returns a list like ['tomato', 'eggs']

# Load env (Ensure GOOGLE_API_KEY is set)
load_dotenv()

def main():
    print("🚀 Starting Agentic Chef...")
    
    # 1. Vision Layer
    # ingredients = getItems() 
    ingredients = ['eggs', 'cheese', 'chives'] # Mocking for test if EyePop isn't connected
    # print(f"👀 Detected: {ingredients}")

    # 2. Initialize Agent
    agent = SmartKitchenChain()

    # 3. User Preferences
    cuisine = input("What kind of cuisine/time constraints? ")
    # cuisine = "Quick breakfast, under 10 minutes" # Mock input
    
    print("\n👨‍🍳 Step 1: Brainstorming Recipes...")
    # Ask Gemini for names only to keep it clean
    recipe_names_response = agent.chat(
        f"I have these ingredients: {ingredients}. "
        f"The user wants: {cuisine}. "
        "Suggest 3 specific recipe names. Return ONLY a Python list of strings, e.g. ['Recipe A', 'Recipe B']."
    )
    print(f"💡 Ideas: {recipe_names_response}")

    # Clean up the string response to get a real list
    try:
        # Sometimes LLMs add text, we try to strip it
        start = recipe_names_response.find('[')
        end = recipe_names_response.find(']') + 1
        recipe_list = eval(recipe_names_response[start:end])
    except:
        recipe_list = [recipe_names_response]

    print("Which recipe did you like: ")
    
    for i, recipe in enumerate(recipe_list):
        print(f"({i}) {recipe}")
      
    try:
        pref_recipe_idx = int(input("Enter number: "))
        selected_recipe = recipe_list[pref_recipe_idx]
    except (ValueError, IndexError):
        print("Invalid selection, using the first option.")
        selected_recipe = recipe_list[0]

    # 4. Search (No Validation Step)
    print(f"\n🎥 Step 2: Finding Tutorials for {selected_recipe}...")
    
    verified_videos = []
    
    # Generate a search query
    search_query = f"{selected_recipe} recipe tutorial"
    
    # 4. Search & Validate
    print(f"\n🎥 Step 2: Finding Tutorials for {selected_recipe}...")
    
    verified_videos = []
    
    # Generate a search query
    search_query = f"{selected_recipe} recipe tutorial"
    
    # Search YouTube (Fetch more to allow for rejection)
    videos = agent.search_youtube(search_query, max_results=5)
    
    print("   Verifying content and generating accessible recipes...")

    for video in videos:
        # 1. Verify
        # print(f"   Checking: {video['title']}...")
        verification = agent.verify_video_relevance(video, selected_recipe, ingredients)
        
        if verification and verification.get('valid'):
            print(f"   ✅ Verified: {video['title']}")
            
            # 2. Generate Guide
            print("      Generating accessible recipe...")
            text_recipe = agent.generate_accessible_recipe(video)
            
            verified_videos.append({
                "recipe": selected_recipe,
                "title": video['title'],
                "url": video['url'],
                "note": verification.get('reason'),
                "plan": text_recipe
            })
            
            # Stop after we have 2 good ones
            if len(verified_videos) >= 2:
                break
        else:
            reason = verification.get('reason') if verification else "Unknown"
            print(f"   ❌ Rejected: {video['title']} ({reason})")

    # 5. Final Output
    print("\n" + "="*40)
    print("       🥗 FINAL MENU       ")
    print("="*40)
    
    if not verified_videos:
        print("Could not find verified videos for these ingredients.")
    else:
        for v in verified_videos:
            print(f"\n🍲 {v['recipe']}")
            print(f"📺 Video: {v['title']}")
            print(f"🔗 Link: {v['url']}")
            print(f"📝 Why: {v['note']}")
            print("-" * 20)
            print(f"📖 Accessible Recipe:\n{v['plan']}")
            print("="*40)

if __name__ == "__main__":
    main()