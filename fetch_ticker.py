import requests
import pandas as pd
import io
import time

def fetch_nse_tickers():
    """
    Fetch all listed companies from NSE (National Stock Exchange of India)
    using the official CSV file from NSE archives
    """
    nse_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print("Fetching NSE tickers from official NSE archives...")
        
        # Create Session for proper cookie handling
        session = requests.Session()
        session.headers.update(headers)
        
        # Fetch the CSV file
        response = session.get(nse_url, timeout=10)
        session.close()
        
        if response.status_code == 200:
            # Read CSV from response content
            df_nse = pd.read_csv(io.BytesIO(response.content))
            
            # Select relevant columns
            if 'SYMBOL' in df_nse.columns and 'NAME OF COMPANY' in df_nse.columns:
                df_nse = df_nse[['SYMBOL', 'NAME OF COMPANY']].copy()
                df_nse.columns = ['symbol', 'name']
                df_nse = df_nse.dropna()
                df_nse = df_nse.sort_values('symbol').reset_index(drop=True)
                
                print(f"✓ NSE tickers fetched successfully")
                print(f"✓ Total NSE companies: {len(df_nse)}")
                
                return df_nse
        
        print(f"Error: Failed to fetch NSE data. Status code: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"Error fetching NSE data: {e}")
        return None

def fetch_bse_tickers():
    """
    Fetch all listed companies from BSE (Bombay Stock Exchange)
    Note: This requires selenium and splinter for browser automation
    Falls back to alternative method if not available
    """
    try:
        print("\nNote: BSE data requires selenium and splinter libraries for browser automation")
        print("Attempting to fetch BSE data...")
        
        # Try to import required libraries
        try:
            from splinter import Browser
            from selenium import webdriver
            import os
            
            download_dir = "/tmp"
            bse_link = "https://mock.bseindia.com/corporates/List_Scrips.html"
            
            # Set up chrome options
            prefs = {"download.default_directory": download_dir}
            options = webdriver.ChromeOptions()
            options.add_experimental_option("prefs", prefs)
            
            # Initiate browser
            browser = Browser('chrome', options=options, headless=True)
            browser.visit(bse_link)
            
            # Fill out form fields
            browser.find_by_id('ddlsegment').select("Equity")
            browser.find_by_id('ddlstatus').select("Active")
            
            # Hit submit button
            browser.find_by_id('btnSubmit').click()
            
            # Wait for table to load
            browser.is_element_present_by_text("Issuer Name")
            time.sleep(5)
            
            # Download
            browser.find_by_id('lnkDownload').click()
            time.sleep(3)
            
            # Read downloaded CSV
            import glob
            csv_files = glob.glob(os.path.join(download_dir, "*.csv"))
            if csv_files:
                df_bse = pd.read_csv(csv_files[-1])
                browser.quit()
                
                print(f"✓ BSE tickers fetched successfully")
                print(f"✓ Total BSE companies: {len(df_bse)}")
                
                return df_bse
            
            browser.quit()
            return None
            
        except ImportError:
            print("⚠ Selenium/Splinter not installed. Skipping BSE data fetch.")
            print("  Install with: pip install selenium splinter")
            return None
            
    except Exception as e:
        print(f"Error fetching BSE data: {e}")
        return None

def merge_and_save(df_nse, df_bse):
    """
    Merge NSE and BSE data and save to CSV
    """
    try:
        if df_nse is not None:
            if df_bse is not None:
                # Rename BSE columns if needed
                if 'Security Name' in df_bse.columns and 'Security Id' in df_bse.columns:
                    df_bse = df_bse.rename(columns={
                        "Security Name": "name",
                        "Security Id": "symbol"
                    })
                
                # Merge on SYMBOL
                final_df = pd.merge(df_nse, df_bse, on='symbol', how='outer', suffixes=('_nse', '_bse'))
                
                # Combine name columns
                if 'name_nse' in final_df.columns and 'name_bse' in final_df.columns:
                    final_df['name'] = final_df['name_nse'].fillna(final_df['name_bse'])
                    final_df = final_df.drop(['name_nse', 'name_bse'], axis=1)
                
                final_df = final_df[['symbol', 'name']].drop_duplicates().sort_values('symbol').reset_index(drop=True)
                
                print(f"\n✓ NSE tickers: {len(df_nse)}")
                print(f"✓ BSE tickers: {len(df_bse)}")
                print(f"✓ Merged total: {len(final_df)}")
                
            else:
                final_df = df_nse
                print(f"\n✓ Using NSE data only: {len(final_df)} companies")
            
            # Save to CSV
            final_df.to_csv("nse_tickers.csv", index=False)
            print(f"\n✓ Tickers saved to 'nse_tickers.csv'")
            
            print("\nSample of fetched tickers:")
            print("=" * 60)
            print(final_df.head(20).to_string(index=False))
            
            return True
        
        return False
        
    except Exception as e:
        print(f"Error merging data: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Fetching Indian Stock Market Tickers (NSE & BSE)")
    print("=" * 60)
    
    # Fetch NSE tickers
    df_nse = fetch_nse_tickers()
    
    # Fetch BSE tickers (optional - requires selenium)
    df_bse = fetch_bse_tickers()
    
    # Merge and save
    success = merge_and_save(df_nse, df_bse)
    
    exit(0 if success else 1)
