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

    cuisine = input("What kind of cuisine would you want?")

    

    recipes = agent.chat(f"I have these ingredients: {ingredients}. Suggest ten common recipes, just give me the names of them.")

    response = agent.chat(f"Using these recipes: {recipes} , come up with search prompts on youtube to find cooking tutorials. If it's not possible to cook anything with these items, respond with 'Cannot make anything with these ingredients'")
    print(response)

if __name__ == "__main__":
    main()