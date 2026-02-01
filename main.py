import os
from dotenv import load_dotenv

from my_agents.RecipeAgent import SmartKitchenChain
from my_agents.FreshnessAgent import estimate_freshness
from my_eyepop.ObjDet import getItems

load_dotenv()

def main():
    print("\n🚀 Starting Agentic Chef")
    print("=" * 40)

    # 1. Vision Layer
    detected_items = getItems()

    if not detected_items:
        print("❌ No food items detected.")
        return

    print("\n👀 Detected ingredients:")
    for item in detected_items:
        print(f" - {item['name']}")

    # 2. Freshness Estimation
    freshness_results = [
        estimate_freshness(item["name"], item["confidence"])
        for item in detected_items
    ]

    print("\n🥦 Freshness estimation (not a legal expiration):")
    for f in freshness_results:
        print(
            f" - {f['item'].capitalize():<10} → "
            f"{f['freshness_status'].upper():<14} "
            f"(~{f['estimated_days']} days)"
        )

    print(
        "\n⚠️ Freshness is estimated using visual cues and typical shelf-life patterns.\n"
        "   This system does NOT determine food safety or legal expiration.\n"
    )

    # 3. Prioritize ingredients that should be used first
    freshness_priority = {"use immediately": 0, "eat soon": 1, "fresh": 2}
    freshness_results.sort(key=lambda x: freshness_priority[x["freshness_status"]])

    prioritized_ingredients = [f["item"] for f in freshness_results]

    # 4. Initialize Recipe Agent
    agent = SmartKitchenChain()

    cuisine = input("🍽️ What kind of cuisine or time constraint? ")

    print("\n👨‍🍳 Generating recipes prioritizing items to use first...\n")

    recipe_names_response = agent.chat(
        f"I have these ingredients ranked by urgency: {prioritized_ingredients}. "
        "Assume basic kitchen staples (oil, salt, etc.) but NO extra ingredients. "
        f"The user wants: {cuisine}. "
        "Suggest 3 specific recipe names. Return ONLY a Python list."
    )

    try:
        recipe_list = eval(recipe_names_response)
    except:
        recipe_list = [recipe_names_response]

    print("💡 Recipe ideas:")
    for i, r in enumerate(recipe_list):
        print(f" ({i}) {r}")

    try:
        selected = int(input("\nSelect a recipe number: "))
        selected_recipe = recipe_list[selected]
    except:
        selected_recipe = recipe_list[0]

    print(f"\n🎥 Finding tutorials for: {selected_recipe}\n")

    videos = agent.search_youtube(f"{selected_recipe} recipe tutorial", max_results=5)

    verified_videos = []

    for video in videos:
        verification = agent.verify_video_relevance(
            video,
            selected_recipe,
            prioritized_ingredients
        )

        if verification and verification.get("valid"):
            print(f"✅ Verified: {video['title']}")
            text_recipe = agent.generate_accessible_recipe(video)

            verified_videos.append({
                "title": video["title"],
                "url": video["url"],
                "note": verification.get("reason"),
                "plan": text_recipe
            })

        if len(verified_videos) >= 2:
            break

    print("\n" + "=" * 40)
    print("🥗 FINAL SUGGESTIONS")
    print("=" * 40)

    for v in verified_videos:
        print(f"\n🍲 {selected_recipe}")
        print(f"📺 {v['title']}")
        print(f"🔗 {v['url']}")
        print(f"📝 {v['note']}")
        print("\n📖 Recipe:\n")
        print(v["plan"])
        print("-" * 40)

if __name__ == "__main__":
    main()
