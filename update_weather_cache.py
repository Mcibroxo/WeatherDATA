import urllib.request
import json
import datetime
import os

LAT = "41.7856"
LON = "-87.7527"
API_KEY = "ce15cbd2ded827cc3a4f8c0a7148f3ea" # OpenWeather API Key
CACHE_FILE = "weather_cache.json"

def fetch_and_cache():
    # 1. Fetch NOAA
    noaa_normalized = []
    try:
        req = urllib.request.Request(f"https://api.weather.gov/points/{LAT},{LON}", headers={'User-Agent': 'WeatherAppCache/1.0'})
        res = json.loads(urllib.request.urlopen(req).read().decode())
        req2 = urllib.request.Request(res['properties']['forecastHourly'], headers={'User-Agent': 'WeatherAppCache/1.0'})
        res2 = json.loads(urllib.request.urlopen(req2).read().decode())
        for p in res2['properties']['periods']:
            noaa_normalized.append({"time": p['startTime'], "temp": p['temperature']})
    except Exception as e: 
        print("NOAA Error:", e)

    # 2. Fetch OWM
    owm_normalized = []
    try:
        req = urllib.request.Request(f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&units=imperial&appid={API_KEY}")
        res = json.loads(urllib.request.urlopen(req).read().decode())
        for p in res['list']:
            dt = datetime.datetime.fromtimestamp(p['dt'], datetime.timezone.utc)
            owm_normalized.append({"time": dt.isoformat(), "temp": p['main']['temp']})
    except Exception as e: 
        print("OWM Error:", e)

    # 3. Fetch Open-Meteo
    om_normalized = {"ecmwf_ifs025": [], "icon_seamless": [], "gem_seamless": []}
    try:
        req = urllib.request.Request(f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m&temperature_unit=fahrenheit&timezone=auto&models=ecmwf_ifs025,icon_seamless,gem_seamless")
        res = json.loads(urllib.request.urlopen(req).read().decode())
        
        for model in om_normalized.keys():
            k = f"temperature_2m_{model}"
            if k in res['hourly']:
                for i, t_str in enumerate(res['hourly']['time']):
                    val = res['hourly'][k][i]
                    if val is not None:
                        om_normalized[model].append({"time": t_str, "temp": val})
    except Exception as e: 
        print("OM Error:", e)

    # Load existing cache
    cache = {"owmData": [], "noaaData": [], "omData_ecmwf_ifs025": [], "omData_icon_seamless": [], "omData_gem_seamless": []}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache.update(json.load(f))
        except: 
            pass

    def merge_data(key, new_data):
        if not new_data: return
        stored = cache.get(key, [])
        merged = {}
        
        for p in stored + new_data:
            t = p['time']
            if not t.endswith('Z') and '+' not in t: t += 'Z'
            dt = datetime.datetime.fromisoformat(t.replace('Z', '+00:00'))
            merged[dt.timestamp()] = p['temp']
            
        cutoff = datetime.datetime.now(datetime.timezone.utc).timestamp() - (36 * 3600) # Keep 36 hours
        
        final_list = []
        for ts in sorted(merged.keys()):
            if ts > cutoff:
                final_list.append({
                    "time": datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat(),
                    "temp": merged[ts]
                })
        cache[key] = final_list

    merge_data('owmData', owm_normalized)
    merge_data('noaaData', noaa_normalized)
    for model, data in om_normalized.items():
        merge_data(f"omData_{model}", data)

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)
    print("Weather cache updated.")

if __name__ == "__main__":
    fetch_and_cache()
