import os
from google import genai
from google.genai import types

def load_api_key():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("API_KEY="):
                    val = line.split("API_KEY=", 1)[1]
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        return val[1:-1]
                    return val
    return os.environ.get("API_KEY") or os.environ.get("GEMINI_API_KEY")

api_key = load_api_key()
print("API Key found:", api_key is not None)
if api_key:
    client = genai.Client(api_key=api_key)
    try:
        # Define Google Search tool
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        # Configure config with tools
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        print("Client initialized successfully.")
        
        # Test content generation with search grounding on gemini-2.5-flash
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="What is the time complexity of the Two Sum problem using a hash map?",
            config=config
        )
        print("API Call Success!")
        print("Response text length:", len(response.text))
        print("Response preview:")
        print(response.text[:200])
    except Exception as e:
        print("Error during API initialization or call:", e)
else:
    print("API Key is missing.")
