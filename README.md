# Chicago Weather & Kalshi Dashboard

This repository contains a customized weather tracking dashboard and prediction logger tailored for Chicago. It aggregates high and low temperature forecasts from multiple meteorological models and integrates with prediction market data (Kalshi).

## Features

- **Automated Weather Logging**: The `log_predictions.py` script automatically fetches and logs tomorrow's forecast at 11:00 PM local time daily.
- **Multi-Provider Consensus**: Aggregates forecasts from NOAA, OpenWeather, and Open-Meteo (ECMWF, ICON, GEM models) to calculate an average consensus prediction.
- **Kalshi Market Integration**: `update_kalshi.py` pulls current market probabilities for weather-related events and contracts.
- **Interactive Dashboard**: `index.html` provides a sleek, responsive interface to visualize daily forecast logs, compare prediction models, and view the latest market data.

## Project Structure

- `index.html`: The main web dashboard UI. Open in any modern web browser to view.
- `log_predictions.py`: Python daemon script that queries multiple weather APIs and saves the data to `predictions_log.json`.
- `update_kalshi.py`: Python script to fetch the latest prediction market data from Kalshi API.
- `predictions_log.json`: The JSON database where automated weather predictions are stored.
- `kalshi_*.json` / `events.json`: Associated data caches for Kalshi market predictions.

## Setup and Usage

### Prerequisites
- Python 3.x
- Modern web browser

### Running the Dashboard
Since the dashboard uses vanilla HTML, CSS, and JS, you can simply open `index.html` directly in your browser or run a simple local web server:
```bash
python -m http.server 8000
```
Then navigate to `http://localhost:8000`.

### Running the Logger
To start the automated background logger that captures tomorrow's predictions every day at 11:00 PM:
```bash
python log_predictions.py
```
*Note: Keep this script running in the background to continue logging data daily.*

### Updating Kalshi Data
To manually pull the latest prediction market data:
```bash
python update_kalshi.py
```
