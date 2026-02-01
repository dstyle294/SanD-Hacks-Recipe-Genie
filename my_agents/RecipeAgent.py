from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage




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
