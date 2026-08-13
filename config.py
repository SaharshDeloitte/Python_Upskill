import os
from dotenv import load_dotenv

load_dotenv()

JOKE_API_URL = "https://official-joke-api.appspot.com/random_joke"
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
