from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
import requests

from config import JOKE_API_URL, WEATHER_API_URL, WEATHER_API_KEY


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Category(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    books = "books"


class Item(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: Category
    count: int


items = {
    1: Item(id=1, name="Laptop", description="High-performance laptop", price=1200.00, category=Category.electronics, count=10),
    2: Item(id=2, name="T-Shirt", description="Cotton t-shirt", price=20.00, category=Category.clothing, count=50),
    3: Item(id=3, name="Book", description="Mystery novel", price=15.00, category=Category.books, count=30),
}


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI app!"}


@app.get("/items")
async def get_items():
    return {"items": items}


@app.get("/items/{item_id}")
async def get_item(item_id: int) -> Item:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return items[item_id]


@app.get("/joke")
async def get_joke():
    try:
        res = requests.get(JOKE_API_URL, timeout=10)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 404:
            raise HTTPException(status_code=404, detail="Joke not found")
        else:
            raise HTTPException(status_code=502, detail="Could not fetch joke")
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not fetch joke")


@app.get("/weather")
async def get_weather(city: str):
    if not WEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Weather API key not set")

    params = {"key": WEATHER_API_KEY, "q": city}

    try:
        res = requests.get(WEATHER_API_URL, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return {
                "city": data["location"]["name"],
                "weather": data["current"]["condition"]["text"],
                "temperature_c": data["current"]["temp_c"],
            }
        elif res.status_code in (400, 404):
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        else:
            raise HTTPException(status_code=502, detail="Could not fetch weather")
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not fetch weather")
