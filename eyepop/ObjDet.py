import os
from eyepop import EyePopSdk
from eyepop.worker.worker_types import Pop, InferenceComponent, ComponentParams
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("EYEPOP_API_KEY")
print(f"Using API key: {api_key}")

script_dir = os.path.dirname(os.path.abspath(__file__))
example_image_path = os.path.join(script_dir, 'images', 'pantry.jpg')

questionList = (
    "Can you list the items? ,"
)

objectOfInterest = 'Groceries'

def getItems(image_path=example_image_path, objectOfInterest=objectOfInterest, questionList=questionList):
    with EyePopSdk.workerEndpoint(
        api_key=api_key
    ) as endpoint:
        prompt = f"Analyze the image of {objectOfInterest} provided and  " + questionList + "If you are unable to answer it then set its classLabel to null"

        print (f"Using prompt: {prompt}")

        endpoint.set_pop(
        Pop(components=[
                InferenceComponent(
                    id=1,
                    ability='eyepop.image-contents:latest',
                    params={"prompts": [
                                {
                                    "prompt": prompt
                                }
                            ] }
                )
            ])
        )

        result = endpoint.upload(example_image_path).predict()
    return json.dumps(result, indent=4)