import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, List, Dict
import json
import os
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

# Cache for NSE stocks
_nse_stocks_cache = None
_cache_timestamp = None
_json_data = None


def load_nse_json_data() -> Optional[Dict]:
    """
    Load NSE tickers data from JSON file.
    Returns the parsed JSON data with all stocks, symbol index, and name index.
    """
    global _json_data
    
    if _json_data is not None:
        return _json_data
    
    try:
        # Try multiple possible paths
        possible_paths = [
            "nse_tickers_search.json",
            "../nse_tickers_search.json",
            "../../nse_tickers_search.json",
            os.path.join(os.path.dirname(__file__), "..", "nse_tickers_search.json"),
            os.path.join(Path(__file__).parent.parent, "nse_tickers_search.json"),
        ]
        
        json_file = None
        for path in possible_paths:
            if os.path.exists(path):
                json_file = path
                break
        
        if json_file is None:
            print("Warning: nse_tickers_search.json not found in expected locations")
            return None
        
        with open(json_file, 'r', encoding='utf-8') as f:
            _json_data = json.load(f)
        
        print(f"✓ Loaded NSE data from JSON: {len(_json_data.get('tickers', []))} stocks")
        return _json_data
        
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return None


def fetch_google_finance_price(symbol: str, timeout: int = 10, debug: bool = False) -> Optional[float]:
    """
    Fetch visible price from Google Finance for a symbol like 'RELIANCE:NSE'.
    Uses hardcoded selectors and returns the first parsable numeric token.
    """
    url = f"https://www.google.com/finance/quote/{symbol}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Hardcoded selectors that usually contain the displayed price
        el = soup.select_one("div[data-last-price]") or soup.select_one("div.YMlKec") or soup.select_one("div[data-attrid='Price'] span")
        if not el:
            if debug:
                print("price element not found")
            return None

        txt = el.get_text()
        if debug:
            print("FOUND ->", txt.strip()[:120])

        # Regex to match Indian price format: 1,525.30 or 1525 or 152.50
        m = re.search(r"[\d,]+(?:\.\d{2})?", txt)
        if not m:
            return None

        try:
            price_str = m.group(0).replace(",", "")
            return float(price_str)
        except Exception:
            return None
    except Exception as e:
        if debug:
            print(f"Error fetching price: {e}")
        return None


def fetch_nse_equity_list() -> List[Dict]:
    """
    Fetch the list of all NSE stocks from JSON file.
    Returns stocks with caching to avoid reloading the file.
    """
    global _nse_stocks_cache, _cache_timestamp
    import time
    
    try:
        current_time = time.time()
        
        # Use cache if available and less than 12 hours old
        if _nse_stocks_cache is not None and _cache_timestamp is not None:
            if current_time - _cache_timestamp < 43200:  # 12 hours cache
                print(f"Using cached NSE stocks data ({len(_nse_stocks_cache)} stocks)")
                return _nse_stocks_cache
        
        print("Loading NSE stocks from JSON file...")
        
        # Load from JSON file
        json_data = load_nse_json_data()
        
        if json_data and "tickers" in json_data:
            tickers = json_data["tickers"]
            
            # Convert to the expected format
            stocks = [
                {
                    "symbol": ticker["symbol"],
                    "name": ticker["name"]
                }
                for ticker in tickers
            ]
            
            print(f"Successfully loaded {len(stocks)} NSE stocks from JSON")
            
            # Cache the results
            _nse_stocks_cache = stocks
            _cache_timestamp = current_time
            
            return stocks
        else:
            print("JSON data not found, using fallback list")
            return get_fallback_stocks()
        
    except Exception as e:
        print(f"Error fetching NSE equity list: {e}")
        return get_fallback_stocks()
def search_nse_stocks(query: str) -> List[Dict]:
    """
    Search for NSE stocks using JSON data with optimized indexes.
    Supports symbol search and partial name search.
    Uses nameIndex and symbolIndex for faster lookups.
    """
    if not query or len(query.strip()) < 1:
        return []
    
    query_lower = query.lower().strip()
    
    try:
        # Load JSON data
        json_data = load_nse_json_data()
        
        if not json_data or "tickers" not in json_data:
            print("JSON data not available, falling back to fetch_nse_equity_list")
            nse_stocks = fetch_nse_equity_list()
            return _search_in_list(query_lower, nse_stocks)
        
        # Get all tickers
        tickers = json_data.get("tickers", [])
        symbol_index = json_data.get("symbolIndex", {})
        name_index = json_data.get("nameIndex", {})
        
        results_set = set()
        
        # 1. Try exact symbol match first (fastest)
        query_upper = query.upper()
        if query_upper in symbol_index:
            ticker_id = symbol_index[query_upper]
            if ticker_id < len(tickers):
                results_set.add(ticker_id)
        
        # 2. Try partial symbol match
        for symbol, ticker_id in symbol_index.items():
            if query_lower in symbol.lower():
                results_set.add(ticker_id)
                if len(results_set) >= 20:  # Limit to avoid too many results
                    break
        
        # 3. Try partial name match
        for name, ticker_ids in name_index.items():
            if query_lower in name:
                for ticker_id in ticker_ids:
                    results_set.add(ticker_id)
                    if len(results_set) >= 20:
                        break
        
        # Convert results to list
        results = []
        for ticker_id in sorted(results_set):
            if ticker_id < len(tickers):
                ticker = tickers[ticker_id]
                results.append({
                    "symbol": ticker["symbol"],
                    "name": ticker["name"]
                })
        
        print(f"Found {len(results)} results for query: {query}")
        return results[:10]  # Return top 10 results
        
    except Exception as e:
        print(f"Error searching NSE stocks: {e}")
        # Fallback to simple search
        nse_stocks = fetch_nse_equity_list()
        return _search_in_list(query_lower, nse_stocks)


def _search_in_list(query_lower: str, nse_stocks: List[Dict]) -> List[Dict]:
    """
    Helper function to search in a list of stocks.
    Used as fallback when JSON indexes are not available.
    """
    if not nse_stocks:
        print("No NSE stocks available for search")
        return []
    
    # Search in NSE stocks
    results = []
    for stock in nse_stocks:
        symbol = stock.get("symbol", "").lower()
        name = stock.get("name", "").lower()
        
        if query_lower in symbol or query_lower in name:
            results.append(stock)
            
            # Limit results to 10
            if len(results) >= 10:
                break
    
    return results


def get_nse_indices() -> List[Dict]:
    """
    Get popular NSE stocks from NSE India API.
    Returns a list of popular stocks with clean data.
    """
    try:
        print("Fetching NSE stocks from API...")
        
        # Fetch all NSE stocks
        all_stocks = fetch_nse_equity_list()
        
        if not all_stocks:
            print("Failed to fetch from NSE API, using fallback")
            return get_fallback_stocks()
        
        # Return top popular stocks (first 25)
        return all_stocks[:25]
        
    except Exception as e:
        print(f"Error fetching NSE stocks: {e}")
        return get_fallback_stocks()


def get_fallback_stocks() -> List[Dict]:
    """
    Fallback list of popular NSE stocks when API fails.
    """
    return [
        {"symbol": "RELIANCE", "name": "Reliance Industries Limited"},
        {"symbol": "TCS", "name": "Tata Consultancy Services Limited"},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Limited"},
        {"symbol": "INFY", "name": "Infosys Limited"},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Limited"},
        {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Limited"},
        {"symbol": "SBIN", "name": "State Bank of India"},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Limited"},
        {"symbol": "ITC", "name": "ITC Limited"},
        {"symbol": "LT", "name": "Larsen & Toubro Limited"},
        {"symbol": "WIPRO", "name": "Wipro Limited"},
        {"symbol": "TITAN", "name": "Titan Company Limited"},
        {"symbol": "HCLTECH", "name": "HCL Technologies Limited"},
        {"symbol": "TECHM", "name": "Tech Mahindra Limited"},
        {"symbol": "AXISBANK", "name": "Axis Bank Limited"},
        {"symbol": "ULTRACEMCO", "name": "Ultratech Cement Limited"},
        {"symbol": "ASIANPAINT", "name": "Asian Paints Limited"},
        {"symbol": "MARUTI", "name": "Maruti Suzuki India Limited"},
        {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto Limited"},
        {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories Limited"},
        {"symbol": "COALINDIA", "name": "Coal India Limited"},
        {"symbol": "POWERGRID", "name": "Power Grid Corporation of India Limited"},
        {"symbol": "JSWSTEEL", "name": "JSW Steel Limited"},
        {"symbol": "TATASTEEL", "name": "Tata Steel Limited"},
        {"symbol": "DIVISLAB", "name": "Divi's Laboratories Limited"},
    ]
