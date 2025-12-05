import csv
import json

def create_search_json():
    """
    Convert NSE tickers CSV to a JSON file optimized for search
    """
    try:
        print("Loading tickers from CSV...")
        
        # Read CSV and create search-optimized JSON
        tickers = []
        symbol_index = {}
        name_index = {}
        
        with open('nse_tickers.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            idx = 0
            for row in reader:
                symbol = row['symbol'].upper()
                name = row['name']
                
                ticker_obj = {
                    "id": idx,
                    "symbol": symbol,
                    "name": name,
                    "searchTerm": f"{symbol} {name}".lower()
                }
                
                tickers.append(ticker_obj)
                symbol_index[symbol] = idx
                
                name_lower = name.lower()
                if name_lower not in name_index:
                    name_index[name_lower] = []
                name_index[name_lower].append(idx)
                
                idx += 1
        
        search_data = {
            "total": len(tickers),
            "tickers": tickers,
            "symbolIndex": symbol_index,
            "nameIndex": name_index
        }
        
        # Save to JSON file
        with open('nse_tickers_search.json', 'w', encoding='utf-8') as f:
            json.dump(search_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Search JSON created: 'nse_tickers_search.json'")
        print(f"✓ Total tickers: {len(tickers)}")
        print(f"\nSample search data:")
        for ticker in tickers[:3]:
            print(f"  {ticker}")
        
        return True
        
    except FileNotFoundError:
        print("Error: nse_tickers.csv not found!")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_search_json()
    exit(0 if success else 1)
