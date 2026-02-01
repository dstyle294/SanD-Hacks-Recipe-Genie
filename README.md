# SanD-Hacks-Recipe-Genie
✅ FEATURES IMPLEMENTED
📷 OpenCV (cv2) Features
1️⃣ Live Camera Capture

Uses system webcam (cv2.VideoCapture(0))

Real-time preview window

Keyboard-controlled capture:

SPACE → capture image

ESC → cancel capture

2️⃣ Local Image Storage (Temporary)

Captured images saved locally as .jpg

Timestamp-based filenames prevent collisions

3️⃣ Blur Detection (Pre-Inference Quality Gate)

Uses Laplacian variance to measure sharpness

Automatically rejects blurry images

Blur threshold configurable (threshold=100.0)

No EyePop call if image is blurry

4️⃣ Automatic Cleanup of Blurry Images

Blurry images are immediately deleted

Prevents disk clutter

Prevents accidental reuse

Improves privacy

🧠 EyePop Computer Vision Features
5️⃣ Object & Item Detection

Uses:

eyepop.image-contents:latest


Detects physical items/products in the image

6️⃣ Prompt-Driven Semantic Filtering

The prompt explicitly:

Ignores:

People

Faces

Hands

Body parts

Human features

Ignores unrelated background objects

Focuses only on:

Products

Items

Shelf goods

Receipt items

7️⃣ Automatic Context Inference (No User Input)

The system auto-handles:

Receipts / bills → item listing

Shelves → product listing

Single products → single item output

No manual “object of interest” input required

8️⃣ OCR / Text Detection Fallback

Uses:

eyepop.text-detection:latest


Triggered only when:

No objects detected, OR

Average confidence < 0.7

9️⃣ Receipt-Aware OCR Prompting

Text detection prompt:

Extracts item names only

Ignores:

Totals

Prices

Tax

Background text

People

🔟 Smart Multi-Stage Inference

Object detection first (cheaper, semantic)

OCR only when needed (fallback)

Prevents unnecessary API calls (free-trial safe)

🔁 Inference Safety & Reliability
1️⃣1️⃣ Safe Predict Wrapper

Automatic retry on EyePop failure

Single retry only (rate-limit safe)

Graceful error handling

🧹 Data Hygiene & Privacy
1️⃣2️⃣ Automatic Image Deletion

Images deleted:

If blurry

After inference completes

No long-term storage of user images

1️⃣3️⃣ Structured Output Filtering

Raw EyePop output is filtered to:

{
  "category": "...",
  "classlabel": "...",
  "confidence": 0.00
}


Removes bounding boxes

Removes metadata noise

Clean, agent-ready format

1️⃣4️⃣ Deduplication Logic

Items deduplicated by classlabel

Prevents duplicate entries from:

OCR + object detection overlap

📁 File & Output Management
1️⃣5️⃣ Raw Output Preservation

Full EyePop response saved to:

./output/raw_eyepop.json


Useful for:

Debugging

Auditing

Future re-processing

🧩 System Design Features
1️⃣6️⃣ Modular Pipeline Architecture

Clear separation of:

Capture

Quality check

Vision inference

OCR fallback

Cleanup

Output formatting

This makes the code:

Extensible

Agent-friendly

Production-ready

🚀 Integration-Ready Features (Already Supported)

These are enabled by design, even if not wired yet:

1️⃣7️⃣ Agent-Compatible Output

Output format is ideal for:

agntcy agents

LLM reasoning

Orchestration pipelines

1️⃣8️⃣ Cost-Aware Design

Zero EyePop calls on blurry images

OCR only when necessary

One retry maximum

🧠 Summary (High-Level)

You’ve built a system that can:

✔ Capture images
✔ Reject bad input automatically
✔ Detect products & items
✔ Read receipts when needed
✔ Ignore humans and noise
✔ Produce clean structured output
✔ Clean up all temporary data
✔ Integrate cleanly with agent frameworks