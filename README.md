# Stock Price API

A FastAPI application to fetch stock prices from Google Finance.

## Project Structure

```
stocks/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── services.py      # Stock price fetching logic
│   └── models.py        # Pydantic models
├── stockdata.py         # Original script
└── requirements.txt     # Python dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Check if the API is running

### Single Stock Price
- **GET** `/price/{symbol}` - Get price for a single stock
  - Parameters:
    - `symbol` (required): Stock symbol (e.g., `RELIANCE:NSE`)
    - `debug` (optional): Enable debug mode

Example:
```
GET /price/RELIANCE:NSE
```

### Multiple Stock Prices (POST)
- **POST** `/prices` - Get prices for multiple stocks
  - Request body:
    ```json
    {
      "symbols": ["RELIANCE:NSE", "TCS:NSE", "ETERNAL:NSE"]
    }
    ```

### NSE Stock Prices (Query)
- **GET** `/prices/nse/{symbols}` - Get prices for NSE stocks (comma-separated)

Example:
```
GET /prices/nse/RELIANCE,TCS,ETERNAL
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Example Usage

Using curl:
```bash
# Get single stock price
curl http://localhost:8000/price/RELIANCE:NSE

# Get multiple stock prices
curl -X POST http://localhost:8000/prices \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["RELIANCE:NSE", "TCS:NSE", "ETERNAL:NSE"]}'

# Get NSE stocks
curl http://localhost:8000/prices/nse/RELIANCE,TCS,ETERNAL
```

Using Python:
```python
import requests

# Single price
response = requests.get("http://localhost:8000/price/RELIANCE:NSE")
print(response.json())

# Multiple prices
response = requests.post(
    "http://localhost:8000/prices",
    json={"symbols": ["RELIANCE:NSE", "TCS:NSE", "ETERNAL:NSE"]}
)
print(response.json())
```
