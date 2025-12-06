# 📈 Stock Price Tracker

A full-stack web application to search, track, and manage NSE stock prices with a portfolio builder.

## 🚀 Features

- **Stock Search**: Search for NSE stocks by symbol or name
- **Live Prices**: Fetch real-time stock prices from Google Finance
- **Favorites**: Save your favorite stocks
- **Portfolio Builder**: Build and track a portfolio with holdings
- **Auto Refresh**: Enable auto-refresh to get updated prices
- **Dark Mode**: Toggle between light and dark themes
- **Responsive UI**: Works on desktop and mobile devices

## 📁 Project Structure

```
stocks/
├── app/
│   ├── main.py          # FastAPI backend with static file serving
│   ├── models.py        # Pydantic models
│   └── services.py      # Stock price fetching & search logic
├── static/
│   └── index.html       # Frontend UI (HTML/CSS/JS)
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
└── nse_tickers_search.json  # NSE stock reference data
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 🏃 Running Locally

```bash
python -m uvicorn app.main:app --reload
```

Visit: `http://localhost:8000`

## 📡 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **GET** | `/` | Frontend UI (index.html) |
| **GET** | `/health` | Health check |
| **GET** | `/stocks` | List popular NSE stocks |
| **GET** | `/stocks/search?query=RELIANCE` | Search stocks by name/symbol |
| **GET** | `/price/{symbol}:NSE` | Get stock price (e.g., `/price/RELIANCE:NSE`) |

## 🌐 Deployment (Render)

### Option 1: Auto-Deploy via render.yaml
1. Push to GitHub
2. Connect repo to Render
3. Render auto-detects `render.yaml`
4. Deploy automatically

### Option 2: Manual Setup on Render
1. Create new Web Service
2. Configure:
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Deploy

Visit your Render URL to see frontend + API working together!

## 🔑 Key Technologies

- **Backend**: FastAPI (Python web framework)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data**: Google Finance API, NSE reference database
- **Deployment**: Render

## ✨ Architecture

Both frontend and backend run in **one service**:
- Frontend (HTML/CSS/JS) served from `/static/` folder
- Backend API routes handle `/stocks`, `/price`, etc.
- Same domain = No CORS issues
- Single Render service handles everything

## 🧪 Testing API Locally

```bash
# Health check
curl http://localhost:8000/health

# Get popular stocks
curl http://localhost:8000/stocks

# Search stocks
curl "http://localhost:8000/stocks/search?query=RELIANCE"

# Get stock price
curl http://localhost:8000/price/RELIANCE:NSE
```

## 🐛 Troubleshooting

**Frontend not loading?**
- Check that `/static/index.html` exists
- Verify `python-multipart` in requirements.txt

**API calls failing?**
- Check browser console (F12) for errors
- Ensure backend is running: `python -m uvicorn app.main:app --reload`

**Deployment issues on Render?**
- Check Render dashboard logs
- Verify start command includes `--port $PORT`

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Contributing

Feel free to fork, modify, and submit pull requests!

## 📧 Support

For issues and questions, please check the GitHub repository.
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
