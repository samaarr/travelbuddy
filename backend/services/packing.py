import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/gpt2"  # Using confirmed working model
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def get_packing_suggestions(city: str, temperature: float, aqi: int) -> dict:
    prompt = f"""
    Generate a travel packing list for {city} with:
    - Temperature: {temperature}°C
    - Air Quality Index: {aqi}/5
    Return ONLY a JSON format response with:
    {{
        "packing_list": ["item1", "item2", "item3", "item4", "item5"],
        "travel_tips": ["tip1", "tip2", "tip3"]
    }}
    Do not include any additional text or explanations.
    """
    
    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=15
        )
        
        if response.status_code == 401:
            return {"error": "Invalid API token"}
        if response.status_code == 503:
            return {"error": "Model loading, try again later"}
            
        # Extract and clean the response
        result = response.json()[0]['generated_text']
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        json_str = result[json_start:json_end]
        
        # Convert to dictionary
        try:
            return eval(json_str)
        except:
            return {"error": "Could not parse packing suggestions"}
            
    except requests.exceptions.Timeout:
        return {"error": "Service timeout"}
    except Exception as e:
        return {"error": f"Packing service error: {str(e)}"}