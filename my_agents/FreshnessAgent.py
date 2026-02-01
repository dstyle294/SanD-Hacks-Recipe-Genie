# my_agents/FreshnessAgent.py

SHELF_LIFE = {
    "banana": 5,
    "apple": 14,
    "tomato": 7,
    "strawberry": 2,
    "eggs": 21,
    "cheese": 10,
    "milk": 5,
    "bread": 3
}

def estimate_freshness(item_name, visual_confidence):
    base_days = SHELF_LIFE.get(item_name.lower(), 3)

    # Degrade shelf life if confidence is low
    degradation = 1 - visual_confidence
    remaining_days = max(1, round(base_days * (1 - degradation)))

    if remaining_days <= 1:
        status = "use immediately"
    elif remaining_days <= 3:
        status = "eat soon"
    else:
        status = "fresh"

    return {
        "item": item_name,
        "freshness_status": status,
        "estimated_days": f"{max(1, remaining_days-1)}–{remaining_days+1}",
        "confidence": "medium",
        "note": "Estimated from visual cues and typical shelf life"
    }
