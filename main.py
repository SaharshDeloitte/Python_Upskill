from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
import requests

from config import (
    JOKE_API_URL,
    WEATHER_API_URL,
    WEATHER_API_KEY,
    ANTHROPIC_API_URL,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
)


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


class SummaryRequest(BaseModel):
    text: str


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


@app.post("/summary")
async def summarize_text(payload: SummaryRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured")

    prompt_text = (
        "Create a short and clear summary for a beginner.\n"
        "Keep it short (about 2-3 sentences).\n"
        "Keep simple words and keep the main meaning.\n"
        "Do not use bullet points. Return plain text only.\n\n"
        f"Text:\n{text}\n\n"
        "Summary:"
    )

    request_body = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 250,
        "messages": [
            {"role": "user", "content": prompt_text},
        ],
    }

    request_headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        res = requests.post(
            ANTHROPIC_API_URL,
            headers=request_headers,
            json=request_body,
            timeout=20,
        )

        if res.status_code == 200:
            data = res.json()
            text_blocks = data.get("content", [])
            summary_parts = [
                block.get("text", "").strip()
                for block in text_blocks
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            summary_text = "\n".join(part for part in summary_parts if part)
            if not summary_text:
                raise HTTPException(status_code=502, detail="Empty summary returned by Anthropic")
            return {
                "summary": summary_text,
                "model": ANTHROPIC_MODEL,
                "source": "anthropic",
            }
        if res.status_code == 400:
            raise HTTPException(status_code=400, detail="Invalid summary request")

    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not fetch summary")
