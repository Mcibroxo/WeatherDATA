import urllib.request
import json
import time
import datetime
import os

LAT = "41.7856"
LON = "-87.7527"
API_KEY = "ce15cbd2ded827cc3a4f8c0a7148f3ea" # OpenWeather API Key
LOG_FILE = "predictions_log.json"

from zoneinfo import ZoneInfo

def fetch_and_log():
    today = datetime.datetime.now(ZoneInfo("America/Chicago"))
    tomorrow = (today + datetime.timedelta(days=1)).date()
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    predictions = {
        "date_predicted_for": tomorrow_str,
        "logged_at": today.isoformat(),
        "providers": {}
    }

    try:
        # NOAA
        noaa_point_req = urllib.request.Request(f"https://api.weather.gov/points/{LAT},{LON}", headers={'User-Agent': 'WeatherAppLogger/1.0'})
        with urllib.request.urlopen(noaa_point_req) as response:
            noaa_point = json.loads(response.read().decode())
        
        noaa_forecast_req = urllib.request.Request(noaa_point['properties']['forecastHourly'], headers={'User-Agent': 'WeatherAppLogger/1.0'})
        with urllib.request.urlopen(noaa_forecast_req) as response:
            noaa_res = json.loads(response.read().decode())
            
        noaa_temps = []
        for p in noaa_res['properties']['periods']:
            dt = datetime.datetime.fromisoformat(p['startTime'])
            if dt.date() == tomorrow:
                noaa_temps.append(p['temperature'])
                
        if noaa_temps:
            predictions['providers']['NOAA'] = {"high": max(noaa_temps), "low": min(noaa_temps)}
            
    except Exception as e:
        print("NOAA Error:", e)

    try:
        # OpenWeather
        owm_req = urllib.request.Request(f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&units=imperial&appid={API_KEY}")
        with urllib.request.urlopen(owm_req) as response:
            owm_res = json.loads(response.read().decode())
            
        owm_temps = []
        for p in owm_res['list']:
            dt = datetime.datetime.fromtimestamp(p['dt'])
            if dt.date() == tomorrow:
                owm_temps.append(p['main']['temp'])
                
        if owm_temps:
            predictions['providers']['OpenWeather'] = {"high": max(owm_temps), "low": min(owm_temps)}
            
    except Exception as e:
        print("OpenWeather Error:", e)

    try:
        # Open-Meteo (ECMWF, ICON, GEM)
        om_req = urllib.request.Request(f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m&temperature_unit=fahrenheit&timezone=America%2FChicago&models=ecmwf_ifs025,icon_seamless,gem_seamless")
        with urllib.request.urlopen(om_req) as response:
            om_res = json.loads(response.read().decode())
            
        for model_name, api_key in [("ECMWF", "temperature_2m_ecmwf_ifs025"), ("ICON", "temperature_2m_icon_seamless"), ("GEM", "temperature_2m_gem_seamless")]:
            temps = []
            if api_key in om_res['hourly']:
                for i, t_str in enumerate(om_res['hourly']['time']):
                    dt = datetime.datetime.fromisoformat(t_str)
                    if dt.date() == tomorrow:
                        val = om_res['hourly'][api_key][i]
                        if val is not None:
                            temps.append(val)
                if temps:
                    predictions['providers'][model_name] = {"high": max(temps), "low": min(temps)}
            
    except Exception as e:
        print("Open-Meteo Error:", e)

    # Calculate Consensus
    highs = [p['high'] for p in predictions['providers'].values()]
    lows = [p['low'] for p in predictions['providers'].values()]
    
    if highs and lows:
        predictions['providers']['Consensus'] = {
            "high": round(sum(highs)/len(highs), 1),
            "low": round(sum(lows)/len(lows), 1)
        }

    # Save to JSON
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                logs = json.load(f)
            except:
                pass
                
    # Remove any existing log for 'tomorrow' to avoid duplicates if testing multiple times a day
    logs = [log for log in logs if log.get('date_predicted_for') != tomorrow_str]
    logs.append(predictions)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=4)
        
    print(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] Logged predictions for {tomorrow_str}:")
    print(json.dumps(predictions['providers'], indent=2))

if __name__ == "__main__":
    print("Starting Prediction Logger.")
    print("This script will automatically run at 23:00 (11 PM) every day to log tomorrow's forecast.")
    print("Press Ctrl+C to stop.")
    print("-" * 50)
    
    last_logged_date = None
    
    try:
        while True:
            now = datetime.datetime.now(ZoneInfo("America/Chicago"))
            # Run if it's 11 PM and we haven't logged yet today
            if now.hour == 23 and now.date() != last_logged_date:
                fetch_and_log()
                last_logged_date = now.date()
            time.sleep(60) # Check the time every 1 minute
    except KeyboardInterrupt:
        print("\nLogger stopped.")
