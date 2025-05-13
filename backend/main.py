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
        weather = WeatherService().get_weather(city)
        aqi = AQIService().get_aqi(city)
        
        packing = get_packing_suggestions(
            city=city,
            temperature=weather["temp"],
            aqi=aqi["aqi"]
        )
        
        # Only use fallback if there's an error
        if "error" in packing:
            print(f"\n[WARNING] Packing service error: {packing['error']}")  # Log the error
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
        
    except Exception as e:
        print(f"\n[ERROR] API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))