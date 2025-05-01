from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from services.weather import WeatherService
from services.aqi import AQIService
from services.packing import get_packing_suggestions  # Import the new packing service

# Get absolute path to frontend directory
frontend_path = "/Users/samarpatil/travelbuddy/frontend"

app = FastAPI()

@app.get("/")
async def serve_index():
    return FileResponse(frontend_path + "/index.html")

app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/api/{city}")
async def get_guide(city: str):
    try:
        # Get weather and AQI data
        weather = WeatherService().get_weather(city)
        aqi = AQIService().get_aqi(city)
        
        # Get packing suggestions
        packing = get_packing_suggestions(
            city=city,
            temperature=weather["temp"],
            aqi=aqi["aqi"]
        )
        
        # Fallback if packing service fails
        if "error" in packing:
            packing = {
                "packing_list": [
                    "Light clothing",
                    "Sunscreen",
                    "Water bottle",
                    "Umbrella",
                    "Comfortable shoes"
                ],
                "travel_tips": [
                    f"Stay hydrated in {weather['temp']}°C weather",
                    f"Check air quality alerts (Current AQI: {aqi['aqi']})",
                    "Plan indoor activities when AQI is high"
                ]
            }

            
        
        return {
            "weather": weather,
            "aqi": aqi,
            "packing": packing
        }
        
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Service error: {str(e)}"
        )