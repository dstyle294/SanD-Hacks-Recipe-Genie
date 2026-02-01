import os
import time
import json
from dotenv import load_dotenv
from eyepop import EyePopSdk
from eyepop.worker.worker_types import Pop, InferenceComponent

load_dotenv()
api_key = os.getenv("EYEPOP_API_KEY")

class VisionService:
    @staticmethod
    def analyze_image(image_path: str) -> list[str]:
        if not api_key:
            raise RuntimeError("EYEPOP_API_KEY not found in environment")

        prompt = (
            "Analyze the image. "
            "Ignore people, faces, hands, body parts, and human features. "
            "Ignore background objects not related to items or products. "
            "If the image is a bill or receipt, list the items on the bill. "
            "If the image is of a shelf or store display, list the products visible. "
            "If the image is of a single product, list that product only. "
            "If the image is unclear or contains no items, respond with NO OBJECTS DETECTED. "
            "Otherwise, detect and list only physical items or products visible. "
            "Do not include humans or body parts as objects. "
            "Use clear class labels only. "
            "If unsure, set classLabel to null."
        )

        with EyePopSdk.workerEndpoint(api_key=api_key) as endpoint:
            # 1. Object Detection
            endpoint.set_pop(
                Pop(components=[
                    InferenceComponent(
                        id=1,
                        ability="eyepop.image-contents:latest",
                        params={"prompts": [{"prompt": prompt}]}
                    )
                ])
            )

            result = VisionService._safe_predict(endpoint, image_path)
            filtered_items = VisionService._filter_classes(result)

            # 2. Text Fallback Logic
            if VisionService._needs_text_fallback(filtered_items):
                print("🔁 Running text detection fallback...")
                endpoint.set_pop(
                    Pop(components=[
                        InferenceComponent(
                            id=2,
                            ability="eyepop.text-detection:latest",
                            params={
                                "prompts": [
                                    {
                                        "prompt": (
                                            "Detect readable text in the image. "
                                            "If this is a bill or receipt, extract item names only. "
                                            "Ignore totals, prices, tax, people, and background text."
                                        )
                                    }
                                ]
                            }
                        )
                    ])
                )
                text_result = VisionService._safe_predict(endpoint, image_path)
                text_items = VisionService._normalize_text_result(text_result)
                
                # Merge
                combined = filtered_items + text_items
                seen = set()
                final_items = []
                for item in combined:
                    key = item["classlabel"]
                    if key and key not in seen:
                        seen.add(key)
                        final_items.append(item)
                filtered_items = final_items

        # Extract just the labels
        ingredients = [item['classlabel'] for item in filtered_items if item.get('classlabel')]
        return ingredients

    @staticmethod
    def _safe_predict(endpoint, image_path, retries=1):
        try:
            return endpoint.upload(image_path).predict()
        except Exception as e:
            if retries > 0:
                print("⚠️ EyePop error, retrying once after delay...")
                time.sleep(3)
                return VisionService._safe_predict(endpoint, image_path, retries - 1)
            raise e

    @staticmethod
    def _filter_classes(eyepop_result):
        filtered = []
        for c in eyepop_result.get("classes", []):
            filtered.append({
                "category": c.get("category"),
                "classlabel": c.get("classLabel"),
                "confidence": float(c.get("confidence", 0))
            })
        return filtered

    @staticmethod
    def _needs_text_fallback(filtered_items, min_conf=0.7):
        if not filtered_items:
            return True
        avg_conf = sum(i["confidence"] for i in filtered_items) / len(filtered_items)
        return avg_conf < min_conf

    @staticmethod
    def _normalize_text_result(text_result):
        items = []
        for c in text_result.get("classes", []):
            label = c.get("classLabel")
            if label:
                items.append({
                    "category": "text-item",
                    "classlabel": label,
                    "confidence": float(c.get("confidence", 0))
                })
        return items
