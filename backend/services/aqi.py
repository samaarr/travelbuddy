import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class AQIService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")  # Same key as weather service
        if not self.api_key:
            raise RuntimeError("Missing OPENWEATHER_API_KEY in .env")
        self.base_url = "https://api.openweathermap.org/data/2.5/air_pollution"
        
        # Debug: Verify key is loaded
        print(f"AQI Service Initialized. Using API Key: {self.api_key[:5]}...")

    def _get_coordinates(self, city: str):
        """Helper method to get coordinates for a city"""
        geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={self.api_key}"
        try:
            response = requests.get(geocode_url, timeout=5)
            data = response.json()
            if not data:
                raise HTTPException(
                    status_code=404,
                    detail=f"City '{city}' not found"
                )
            return data[0]['lat'], data[0]['lon']
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Geocoding failed: {str(e)}"
            )

    def get_aqi(self, city: str):
        """
        Fetches AQI data using OpenWeatherMap Air Pollution API
        Returns: 
            {
                "aqi": int (1-5), 
                "level": "Good/Fair/Moderate/Poor/Very Poor",
                "components": {
                    "co": float,
                    "no": float,
                    "no2": float,
                    "o3": float,
                    "so2": float,
                    "pm2_5": float,
                    "pm10": float,
                    "nh3": float
                }
            }
        """
        try:
            # Step 1: Get coordinates for the city
            lat, lon = self._get_coordinates(city)
            print(f"\n[DEBUG] Coordinates for {city}: lat={lat}, lon={lon}")

            # Step 2: Fetch AQI data
            url = f"{self.base_url}?lat={lat}&lon={lon}&appid={self.api_key}"
            print(f"[DEBUG] AQI Request URL: {url.replace(self.api_key, '***')}")
            
            response = requests.get(url, timeout=10)
            print(f"[DEBUG] Response status: {response.status_code}")

            if not response.content:
                raise HTTPException(
                    status_code=502,
                    detail="Empty response from AQI API"
                )

            data = response.json()
            print(f"[DEBUG] Raw API Response: {data}")

            # Step 3: Handle API errors
            if response.status_code != 200:
                error_msg = data.get('message', 'Unknown error')
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AQI API error: {error_msg}"
                )

            # Step 4: Extract and format data
            aqi_data = data['list'][0]
            aqi_value = aqi_data['main']['aqi']
            
            return {
                "aqi": aqi_value,
                "level": self._categorize_aqi(aqi_value),
                "components": aqi_data['components']
            }

        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=502,
                detail=f"AQI API request failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error processing AQI data: {str(e)}"
            )

    def _categorize_aqi(self, aqi: int) -> str:
        """Categorizes AQI value according to OpenWeatherMap's scale"""
        scale = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        return scale.get(aqi, "Unknown")