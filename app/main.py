from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.services import (
    fetch_google_finance_price,
    get_nse_indices,
    search_nse_stocks,
    load_nse_json_data
)
from app.models import StockPrice

app = FastAPI(
    title="Stock Price API",
    description="API to fetch stock prices from Google Finance with NSE stock search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load JSON data on startup
def get_popular_stocks_cached():
    """Get popular stocks from JSON data without external API calls."""
    stocks = get_nse_indices()
    return stocks


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/stocks", tags=["Stocks"])
def get_all_stocks():
    """
    Get list of all popular NSE stocks available for search.
    Data is loaded from local JSON file (no external API calls).
    Returns top 25 stocks.
    """
    stocks = get_popular_stocks_cached()
    return {
        "stocks": stocks,
        "source": "local JSON file",
        "total": len(stocks)
    }


@app.get("/stocks/search", tags=["Stocks"])
def search_stocks(query: str = ""):
    """
    Search for NSE stocks by name or symbol.
    Uses reliable NSE stock reference database.
    
    - **query**: Search query (matches symbol or name, case-insensitive)
    """
    query_lower = query.lower().strip()
    
    if not query_lower:
        # Return first 6 popular stocks if no query
        stocks = get_popular_stocks_cached()
        return {"stocks": stocks[:6]}
    
    # Search using NSE stocks reference database
    results = search_nse_stocks(query)
    return {"stocks": results}


@app.get("/price/{symbol}", tags=["Stocks"], response_model=StockPrice)
def get_stock_price(symbol: str, debug: bool = False):
    """
    Get stock price for a single symbol.
    
    - **symbol**: Stock symbol (e.g., 'RELIANCE:NSE')
    - **debug**: Enable debug mode to get more information
    """
    price = fetch_google_finance_price(symbol, debug=debug)
    return StockPrice(symbol=symbol, price=price)


# Mount static files directory
BASE_DIR = Path(__file__).parent.parent
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
