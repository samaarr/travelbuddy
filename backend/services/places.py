

class PlacesService:
    PLACES_DATA = {
    "tokyo": ["Shibuya Crossing", "Tokyo Tower"],
    "paris": ["Eiffel Tower", "Louvre Museum"]
    }   
    def get_places(self, city: str):
        return PLACES_DATA.get(city.lower(), ["No places data available"])