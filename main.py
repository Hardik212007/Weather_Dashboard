
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
HISTORY_FILE = "history.json"

if not API_KEY:
    print("Error: OPENWEATHER_API_KEY not found. Please set it in your .env file.")
    sys.exit(1)

def get_aqi_advisory(aqi):
    """Returns the advisory text based on AQI index."""
    advisories = {
        1: ("Good", "Air quality is considered satisfactory, and air pollution poses little or no risk."),
        2: ("Fair", "Air quality is acceptable; however, some pollutants may be a concern for very sensitive people."),
        3: ("Moderate", "Sensitive individuals should reduce outdoor activity."),
        4: ("Poor", "Everyone may begin to experience health effects; sensitive groups may experience more serious effects."),
        5: ("Very Poor", "Health warnings of emergency conditions. The entire population is more likely to be affected.")
    }
    return advisories.get(aqi, ("Unknown", "No advisory available."))

def load_history():
    """Loads the last 5 searches from the JSON file."""
    try:
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(history):
    """Saves the search history to the JSON file, keeping only the last 5."""
    with open(HISTORY_FILE, "w") as file:
        json.dump(history[-5:], file, indent=4)

def display_history():
    """Displays the saved search history."""
    history = load_history()
    if not history:
        print("\nNo search history available.")
        return
    
    print("\n--- Last 5 Searches ---")
    for entry in history:
        print(f"City: {entry['city']} | Temp: {entry['temp']}°C | Condition: {entry['condition']} | AQI: {entry['aqi']}")
    print("-----------------------\n")

def fetch_weather_and_aqi(city_name):
    """Fetches weather and AQI data for a given city."""
    weather_url = f"http://api.openweathermap.org/data/2.5/weather"
    weather_params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        # 1. Fetch Weather Data & Coordinates
        response = requests.get(weather_url, params=weather_params, timeout=10)
        
        if response.status_code == 404:
            print(f"Error: Could not find a city named '{city_name}'. Please check your spelling.")
            return
        elif response.status_code == 401:
            print("Error: Unauthorized. Please check your API key.")
            return
        
        response.raise_for_status() # Catch any other HTTP errors
        weather_data = response.json()

        # Safely extract weather data using .get()
        main_data = weather_data.get("main", {})
        temp = main_data.get("temp", "N/A")
        feels_like = main_data.get("feels_like", "N/A")
        humidity = main_data.get("humidity", "N/A")
        
        wind_data = weather_data.get("wind", {})
        wind_speed_ms = wind_data.get("speed", 0)
        wind_speed_kmh = round(wind_speed_ms * 3.6, 1) # Convert m/s to km/h
        
        condition = weather_data.get("weather", [{}])[0].get("description", "N/A").capitalize()
        
        lat = weather_data.get("coord", {}).get("lat")
        lon = weather_data.get("coord", {}).get("lon")

        # 2. Fetch AQI Data using Coordinates
        if lat is None or lon is None:
            print("Error: Could not retrieve coordinates to fetch Air Quality data.")
            return

        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution"
        aqi_params = {"lat": lat, "lon": lon, "appid": API_KEY}
        
        aqi_response = requests.get(aqi_url, params=aqi_params, timeout=10)
        aqi_response.raise_for_status()
        aqi_data = aqi_response.json()

        aqi_value = aqi_data.get("list", [{}])[0].get("main", {}).get("aqi", 0)
        aqi_label, aqi_advisory = get_aqi_advisory(aqi_value)

        # 3. Format and Print Output
        print(f"\nWeather in {city_name.title()}:")
        print(f"Temperature: {temp}°C (Feels like {feels_like}°C)")
        print(f"Humidity: {humidity}%")
        print(f"Wind Speed: {wind_speed_kmh} km/h")
        print(f"Condition: {condition}")
        print(f"Air Quality Index: {aqi_value} - {aqi_label}")
        print(f"Advisory: {aqi_advisory}\n")

        # 4. Update History
        history = load_history()
        history.append({
            "city": city_name.title(),
            "temp": temp,
            "condition": condition,
            "aqi": aqi_value
        })
        save_history(history)

    except requests.exceptions.ConnectionError:
        print("Network Error: Please check your internet connection and try again.")
    except requests.exceptions.Timeout:
        print("Timeout Error: The API took too long to respond.")
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
    except KeyError:
        print("Data Error: The API returned data in an unexpected format.")

def main():
    print("=== Weather + Air Quality CLI Dashboard ===")
    
    # Load last search on startup
    history = load_history()
    if history:
        last_search = history[-1]
        print(f"[Startup] Last searched: {last_search['city']} ({last_search['temp']}°C, {last_search['condition']})")
    
    print("Type 'history' to view recent searches, or 'quit' to exit.")

    while True:
        user_input = input("\nEnter city name: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        if user_input.lower() == 'history':
            display_history()
            continue

        fetch_weather_and_aqi(user_input)

if __name__ == "__main__":
    main()