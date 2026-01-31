from ultralytics import YOLO
from collections import Counter
import cv2

def scan_pantry(image_path):
    # 1. Load the model
    # 'yolo11x.pt' is the largest/most accurate standard model. 
    # Use 'yolo11n.pt' if you want it to run faster but with less accuracy.
    print("Loading model...")
    model = YOLO('yolo11x.pt') 

    # 2. Run detection on the image
    print(f"Scanning image: {image_path}...")
    results = model(image_path)

    # 3. Process the results
    detected_items = []
    
    # results is a list (in case you pass multiple images), so we take the first one
    result = results[0]
    
    # Iterate through all detected boxes
    for box in result.boxes:
        # Get the class ID (a number representing the object type)
        class_id = int(box.cls[0])
        
        # Get the human-readable name using the model's names dictionary
        item_name = result.names[class_id]
        detected_items.append(item_name)

    # 4. Summarize the findings
    if not detected_items:
        print("\n--- Result ---")
        print("No items detected. Try checking the lighting or angle.")
        return

    # Count duplicates (e.g., make "bottle, bottle, bottle" into "3 bottles")
    inventory = Counter(detected_items)

    print("\n--- Pantry Inventory ---")
    for item, count in inventory.items():
        print(f"- {count} {item}(s)")

    # Optional: Save/Show the image with bounding boxes drawn on it
    result.save(filename='pantry_result.jpg')
    print("\nCheck 'pantry_result.jpg' to see exactly what was detected.")

# --- RUN THE SCRIPT ---
# Replace 'my_pantry.jpg' with the actual path to your photo
if __name__ == "__main__":
    # You can use a local file path or a URL
    scan_pantry("examples/grocery_haul.jpg")