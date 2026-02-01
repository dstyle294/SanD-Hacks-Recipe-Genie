import os
import json
import cv2
import time
from datetime import datetime
from dotenv import load_dotenv
from eyepop import EyePopSdk
from eyepop.worker.worker_types import Pop, InferenceComponent

# -------------------- SETUP --------------------

load_dotenv()
api_key = os.getenv("EYEPOP_API_KEY")

if not api_key:
    raise RuntimeError("EYEPOP_API_KEY not found in environment")

# -------------------- CAMERA CAPTURE --------------------

def capture_image(save_dir="./images"):
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera")

    print("📷 Camera opened. Press SPACE to capture, ESC to cancel.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Camera - Press SPACE to Capture", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            cap.release()
            cv2.destroyAllWindows()
            raise RuntimeError("Camera capture cancelled")

        if key == 32:  # SPACE
            filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            image_path = os.path.join(save_dir, filename)
            cv2.imwrite(image_path, frame)

            cap.release()
            cv2.destroyAllWindows()
            print(f"✅ Image saved to {image_path}")
            return image_path
def safe_predict(endpoint, image_path, retries=1):
    """
    Safe EyePop predict with ONE retry (free-trial safe)
    """
    try:
        return endpoint.upload(image_path).predict()
    except Exception as e:
        if retries > 0:
            print("⚠️ EyePop error, retrying once after delay...")
            time.sleep(3)
            return safe_predict(endpoint, image_path, retries - 1)
        raise e

# -------------------- FILTERING --------------------

def filter_classes(eyepop_result):
    filtered = []
    for c in eyepop_result.get("classes", []):
        filtered.append({
            "category": c.get("category"),
            "classlabel": c.get("classLabel"),
            "confidence": float(c.get("confidence", 0))
        })
    return filtered

# -------------------- MAIN --------------------

example_image_path = capture_image()

objectOfInterest = input(
    "Enter object of interest (bill, receipt, bottle, clothing, etc): "
).strip().lower()

if objectOfInterest in ["bill", "receipt", "invoice"]:
    questionList = "List the items in the bill"
else:
    questionList = f"List the detected {objectOfInterest} objects"

prompt = (
    f"Analyze the image of the {objectOfInterest}. "
    f"{questionList}. "
    "If you are unable to answer, set the classLabel to null."
)

print(f"\n🧠 Using prompt:\n{prompt}\n")

os.makedirs("./output", exist_ok=True)

with EyePopSdk.workerEndpoint(api_key=api_key) as endpoint:

    endpoint.set_pop(
        Pop(components=[
            InferenceComponent(
                id=1,
                ability="eyepop.image-contents:latest",
                params={
                    "prompts": [{"prompt": prompt}]
                }
            )
        ])
    )

    result = safe_predict(endpoint, example_image_path)


# -------------------- OUTPUT --------------------

with open("./output/raw_eyepop.json", "w") as f:
    json.dump(result, f, indent=4)

filtered_items = filter_classes(result)

print("✅ Filtered Output:")
print(json.dumps(filtered_items, indent=4))
