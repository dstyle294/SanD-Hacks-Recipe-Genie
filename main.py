# main.py
from my_agents.RecipeAgent import SmartKitchenChain # or whatever your main function is called
from my_eyepop.ObjDet import getItems

def main():
    print("🚀 Starting Agentic Chef...")
    
    # 1. Test Vision
    ingredients = getItems()


    # 2. Test Agent
    print("👨‍🍳 sending to Chef...")
    agent = SmartKitchenChain()

    recipes = agent.chat(f"I have these ingredients: {ingredients}. Suggest ten common recipes, just give me the names of them.")

    response = agent.chat(f"Using these recipes: {recipes} , come up with search prompts on youtube to find cooking tutorials.")
    print(response)

if __name__ == "__main__":
    main()