import urllib.request
import json
import time
import os
import datetime

INTERVAL_MINUTES = 10

def get_kalshi_tickers():
    # Automatically generate the ticker string based on the current date
    # Format example: KXHIGHCHI-26MAY04 (YYMMMdd)
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    today_str = today.strftime("%y%b%d").upper()
    tomorrow_str = tomorrow.strftime("%y%b%d").upper()
    
    return {
        "today": f"KXHIGHCHI-{today_str}",
        "tomorrow": f"KXHIGHCHI-{tomorrow_str}"
    }

def fetch_kalshi_data():
    events = get_kalshi_tickers()
    for day, ticker in events.items():
        url = f"https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker={ticker}"
        file_path = f"kalshi_{day}.json"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=4)
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully updated {file_path}")
                else:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Failed with status code: {response.status}")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error fetching data for {ticker}: {e}")

if __name__ == "__main__":
    print(f"Starting Kalshi updater...")
    print(f"This will pull the latest probabilities and save them every {INTERVAL_MINUTES} minutes.")
    print("Press Ctrl+C to stop.")
    print("-" * 50)
    
    try:
        while True:
            fetch_kalshi_data()
            time.sleep(INTERVAL_MINUTES * 60)
    except KeyboardInterrupt:
        print("\nUpdater stopped by user.")
