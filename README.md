# Weather + AQI CLI Dashboard

A command-line Python application that fetches real-time weather and air quality data using the OpenWeatherMap API.

## Features
* Current weather conditions (Temp, Humidity, Wind in km/h)
* Air Quality Index (AQI) with health advisories
* Saves the last 5 searches locally
* Graceful error handling for bad inputs and network drops

## Setup Instructions
1. Clone this repository.
2. Create a virtual environment: `python -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt` *(or `pip install requests python-dotenv`)*
4. Create a `.env` file based on `.env.example`:
   `OPENWEATHER_API_KEY=your_actual_api_key_here`
5. Run the app: `python main.py`