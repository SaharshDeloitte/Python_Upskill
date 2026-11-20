# FastAPI Sample App

Simple FastAPI app with sample item endpoints, a random joke endpoint, and a weather endpoint.

## Prerequisites

- Python 3.9+
- Internet connection (for /joke and /weather)

## Setup

1. Install dependencies.

```bat
pip install fastapi uvicorn pydantic requests python-dotenv
```


## Run

Start the app from this folder:

```bat
uvicorn main:app --reload
```

Server URL: http://127.0.0.1:8000


## Endpoints

- GET /
	- Returns welcome message.

- GET /items
	- Returns all sample items.

- GET /items/{item_id}
	- Returns one item by id.
	- Example: /items/1

- GET /joke
	- Fetches one random joke from official-joke-api.

- GET /weather?city={city}
	- Fetches weather from WeatherAPI.
	- Example: /weather?city=London
	- Response includes city, weather description, and temperature in Celsius.

- POST /summary
	- Returns a short summary from input text.
	- Uses Anthropic model for summarization.
	- Uses ANTHROPIC_API_KEY configured on server.
	- Optional model override with ANTHROPIC_MODEL (default: claude-haiku-5-5).
	- Body example:

```json
{
	"text": "FastAPI is simple. It is fast. It is beginner friendly."
}
```

	- cURL example:

```bat
curl -X POST "http://127.0.0.1:8000/summary" ^
  -H "Content-Type: application/json" ^
	-d "{\"text\":\"FastAPI is simple. It is fast. It is beginner friendly.\"}"
```

