import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing OPENWEATHER_API_KEY in .env")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Debug: Verify key is loaded (prints first 5 chars for security)
        print(f"Weather API Key: {self.api_key[:5]}...")

    def get_weather(self, city: str):
        """Get current weather data with comprehensive error handling"""
        try:
            # 1. Build and log request URL (without exposing full key)
            url = f"{self.base_url}/weather?q={city}&appid={self.api_key[:5]}...&units=metric"
            print(f"\n[DEBUG] Weather API Request: {url.replace(self.api_key, '***')}")
            
            # 2. Make the API request
            response = requests.get(
                f"{self.base_url}/weather?q={city}&appid={self.api_key}&units=metric",
                timeout=10
            )
            
            # 3. Check for empty/invalid responses
            if not response.content:
                raise HTTPException(
                    status_code=502,
                    detail="Weather API returned empty response"
                )
                
            # 4. Parse JSON with validation
            try:
                data = response.json()
                print(f"[DEBUG] Raw API Response: {data}")  # Debug output
            except ValueError as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Invalid JSON from API: {str(e)}"
                )
            
            # 5. Handle known API errors
            if response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid OpenWeather API key - check https://openweathermap.org/faq#error401"
                )
                
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"City '{city}' not found"
                )
                
            # 6. Validate response structure
            required_keys = ["main", "weather"]
            for key in required_keys:
                if key not in data:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Malformed API response: Missing '{key}' field"
                    )
            
            # 7. Return formatted data
            return {
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }
            
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=504,
                detail="Weather API request timed out"
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=502,
                detail=f"Weather API connection failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )