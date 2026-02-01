from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage


import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from eyepop import ObjDet

getItems()


class SmartKitchenChain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            api_key="AIzaSyB5gvPkY2fL2qZQmpK2sqKBzHzPXNFZHl8",
            temperature=0.7
        )
        # Store conversation history manually
        self.chat_history = []

    def chat(self, user_input):
        # Add user message to history
        self.chat_history.append(HumanMessage(content=user_input))
        
        # Get response from LLM with full history
        response = self.llm.invoke(self.chat_history)
        
        # Add AI response to history
        self.chat_history.append(response)
        
        return response.content

# Usage

agent = SmartKitchenChain()


recipes = agent.chat(f"I have these ingredients: {ingredients}. Suggest ten common recipes, just give me the names of them.")

response = agent.chat(f"Using these recipes: {recipes} , come up with search prompts on youtube to find cooking tutorials.")
print(response)