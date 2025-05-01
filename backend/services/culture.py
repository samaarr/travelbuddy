class CultureService:
    def get_tips(self, destination: str):
        cultural_data = {
            "tokyo": {
                "greeting": "Bow slightly when greeting",
                "dining": "Never pass food with chopsticks to chopsticks"
            },
            "paris": {
                "greeting": "Cheek kisses are common among friends",
                "dining": "Keep hands on the table during meals"
            }
        }
        city_key = destination.lower()
        return cultural_data.get(city_key, {"error": "No cultural data available"})