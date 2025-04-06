import json
import requests
import csv
from datetime import datetime
import os
import streamlit as st

# --- Agent 1: Configuration Loader ---
def load_config(config_path="config.json"):
    """Loads configuration from a JSON file."""
    print("[ConfigAgent] Loading configuration...")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Check if running in Streamlit Cloud and use secrets
            if 'api_key' not in config and hasattr(st, 'secrets'):
                try:
                    config['api_key'] = st.secrets["OPENWEATHERMAP_API_KEY"]
                except KeyError:
                    raise ValueError("API key missing from config and Streamlit secrets")
            elif 'api_key' not in config or not config['api_key']:
                raise ValueError("API key missing or not set in config.json / secrets")
        print("[ConfigAgent] Configuration loaded successfully.")
        # Basic validation
        if "api_key" not in config or not config["api_key"] or config["api_key"] == "OPENWEATHERMAP_API_KEY":
             raise ValueError("API key missing or not set in config.json")
        if "location" not in config or "latitude" not in config["location"] or "longitude" not in config["location"]:
             raise ValueError("Location coordinates missing in config.json")
        return config
    except FileNotFoundError:
        print(f"[ConfigAgent] ERROR: Configuration file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"[ConfigAgent] ERROR: Could not decode JSON from {config_path}")
        return None
    except ValueError as ve:
        print(f"[ConfigAgent] ERROR: Configuration validation failed: {ve}")
        return None
    except Exception as e:
        print(f"[ConfigAgent] ERROR: An unexpected error occurred loading config: {e}")
        return None

# --- Agent 2: Air Quality Fetcher ---
def fetch_air_quality(config):
    """Fetches air quality data from OpenWeatherMap."""
    print("[AQIAgent] Fetching air quality data...")
    lat = config['location']['latitude']
    lon = config['location']['longitude']
    api_key = config['api_key']
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"

    try:
        response = requests.get(url, timeout=10) # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        # Extract relevant data (structure based on OpenWeatherMap API doc)
        aqi_data = data['list'][0]['main']
        components = data['list'][0]['components']
        timestamp = datetime.now().isoformat() # Use ISO format for clarity

        processed_data = {
            "timestamp": timestamp,
            "latitude": lat,
            "longitude": lon,
            "aqi": aqi_data['aqi'],
            "co": components.get('co'), # Use .get for safety if key is missing
            "no2": components.get('no2'),
            "o3": components.get('o3'),
            "pm2_5": components.get('pm2_5'),
            "pm10": components.get('pm10'),
            "so2": components.get('so2')
        }
        print(f"[AQIAgent] Air Quality Index (AQI): {processed_data['aqi']}")
        return processed_data
    except requests.exceptions.RequestException as e:
        print(f"[AQIAgent] ERROR: Failed to fetch AQI data: {e}")
        return None
    except (KeyError, IndexError) as e:
         print(f"[AQIAgent] ERROR: Could not parse AQI response structure: {e}. Response: {data}")
         return None
    except Exception as e:
        print(f"[AQIAgent] ERROR: An unexpected error occurred fetching AQI data: {e}")
        return None


# --- Agent 3: Weather Fetcher ---
def fetch_weather(config):
    """Fetches current weather data from OpenWeatherMap."""
    print("[WeatherAgent] Fetching weather data...")
    lat = config['location']['latitude']
    lon = config['location']['longitude']
    api_key = config['api_key']
    # Request Celsius units
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        response = requests.get(url, timeout=10) # Added timeout
        response.raise_for_status()
        data = response.json()

        # Extract relevant data
        weather_main = data['main']
        weather_desc = data['weather'][0]['description']
        timestamp = datetime.now().isoformat()

        processed_data = {
            "timestamp": timestamp, # Redundant but keeps structure clear
            "temperature_celsius": weather_main.get('temp'),
            "feels_like_celsius": weather_main.get('feels_like'),
            "humidity_percent": weather_main.get('humidity'),
            "pressure_hpa": weather_main.get('pressure'),
            "description": weather_desc,
            "wind_speed_mps": data.get('wind', {}).get('speed') # Safer access
        }
        print(f"[WeatherAgent] Current Temperature: {processed_data['temperature_celsius']}°C, Description: {processed_data['description']}")
        return processed_data
    except requests.exceptions.RequestException as e:
        print(f"[WeatherAgent] ERROR: Failed to fetch weather data: {e}")
        return None
    except (KeyError, IndexError) as e:
         print(f"[WeatherAgent] ERROR: Could not parse Weather response structure: {e}. Response: {data}")
         return None
    except Exception as e:
        print(f"[WeatherAgent] ERROR: An unexpected error occurred fetching weather data: {e}")
        return None


# --- Agent 4: Data Logger (CSV) ---
def store_data_csv(aqi_data, weather_data, config):
    """Stores the combined data into a CSV file."""
    print("[StorageAgent] Storing data...")
    filename = config['storage']['csv_filename']

    # Combine data, ensuring timestamp isn't duplicated if present in both
    combined_data = aqi_data.copy() # Start with AQI data
    # Add weather data, avoiding overwriting common keys like timestamp if needed
    for key, value in weather_data.items():
        if key not in combined_data:
             combined_data[key] = value
        elif key != "timestamp": # Allow overwriting other potential duplicates if logic demands
             combined_data[f"weather_{key}"] = value # Or prefix to avoid collision

    # Define the order of columns
    fieldnames = [
        'timestamp', 'latitude', 'longitude', 'aqi', 'temperature_celsius',
        'humidity_percent', 'description', 'co', 'no2', 'o3', 'pm2_5', 'pm10', 'so2',
        'feels_like_celsius', 'pressure_hpa', 'wind_speed_mps'
        # Add other fields from combined_data if needed
    ]

    # Ensure all keys in combined_data are included in fieldnames, adding any missing ones
    for key in combined_data.keys():
        if key not in fieldnames:
            fieldnames.append(key)

    file_exists = os.path.isfile(filename)

    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            # Use DictWriter for easier handling based on keys
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore') # Ignore extra fields not in fieldnames

            # Write header only if file is new/empty
            if not file_exists or os.path.getsize(filename) == 0:
                writer.writeheader()
                print(f"[StorageAgent] Created CSV file and wrote header: {filename}")

            # Write the data row
            writer.writerow(combined_data)
            print(f"[StorageAgent] Data appended successfully to {filename}")
            return True
    except IOError as e:
        print(f"[StorageAgent] ERROR: Could not write to CSV file {filename}: {e}")
        return False
    except Exception as e:
        print(f"[StorageAgent] ERROR: An unexpected error occurred during storage: {e}")
        return False

# --- Agent 5: Condition Analyzer ---
def analyze_conditions(aqi_data, weather_data, config):
    """Analyzes if conditions exceed predefined thresholds."""
    print("[AnalysisAgent] Analyzing conditions...")
    aqi_threshold = config['thresholds']['aqi_alert']
    temp_threshold = config['thresholds']['temp_alert_celsius']

    current_aqi = aqi_data.get('aqi')
    current_temp = weather_data.get('temperature_celsius')

    alert = False
    message = "Conditions are within normal parameters."

    # Check if data is valid before comparing
    if current_aqi is None or current_temp is None:
        message = "[AnalysisAgent] WARNING: Missing AQI or Temperature data, cannot perform full analysis."
        print(message)
        return {"alert": False, "message": message}

    # --- Alert Logic ---
    # Alert if AQI is at or above threshold AND Temperature is above threshold
    aqi_alert_triggered = current_aqi >= aqi_threshold
    temp_alert_triggered = current_temp > temp_threshold

    if aqi_alert_triggered and temp_alert_triggered:
        alert = True
        message = (f"ALERT: Conditions threshold exceeded in {config['location']['city_name']}! "
                   f"AQI: {current_aqi} (Threshold: >= {aqi_threshold}), "
                   f"Temperature: {current_temp}°C (Threshold: > {temp_threshold}°C).")
    elif aqi_alert_triggered:
         message = (f"INFO: Air Quality index is {current_aqi} (Threshold: >= {aqi_threshold}) "
                    f"in {config['location']['city_name']}, but temperature ({current_temp}°C) is below threshold.")
    elif temp_alert_triggered:
         message = (f"INFO: Temperature is {current_temp}°C (Threshold: > {temp_threshold}°C) "
                    f"in {config['location']['city_name']}, but AQI ({current_aqi}) is below threshold.")

    print(f"[AnalysisAgent] Analysis complete. Alert needed: {alert}")
    return {"alert": alert, "message": message}

# --- Agent 6: Notifier ---
def report_findings(analysis_result):
    """Prints the analysis findings to the console."""
    print("[ReportingAgent] Reporting findings...")
    print("--------------------------------------------------")
    print(f"Analysis Result: {analysis_result['message']}")
    print("--------------------------------------------------")


# --- Modified Main Orchestrator ---
def run_pipeline():
    """Runs the agentic pipeline steps and returns logs and results."""
    logs = []
    logs.append("======= Starting Climate Data Pipeline =======")

    # 1. Load Config
    config = load_config() # Assuming load_config prints its own status/errors
    if not config:
        logs.append("Pipeline failed: Could not load configuration.")
        return logs, {"alert": None, "message": "Configuration Error"}

    # Append config loading messages (if any were printed by load_config) - Optional refinement
    logs.append(f"[ConfigAgent] Using config for {config.get('location',{}).get('city_name', 'N/A')}")

    # 2. Fetch Air Quality
    # Modify agent functions slightly to also return their log string (optional, but cleaner)
    # For simplicity here, we'll just add logs before/after calling the original functions
    logs.append("[AQIAgent] Attempting to fetch air quality...")
    aqi_data = fetch_air_quality(config) # fetch_air_quality still prints its own logs
    if not aqi_data:
        logs.append("Pipeline interrupted: Failed to fetch air quality data.")
        # Decide if you want to continue or stop
        return logs, {"alert": None, "message": "Failed to fetch AQI"}
    logs.append(f"[AQIAgent] Fetch successful. AQI: {aqi_data.get('aqi', 'N/A')}")


    # 3. Fetch Weather
    logs.append("[WeatherAgent] Attempting to fetch weather...")
    weather_data = fetch_weather(config) # fetch_weather still prints its own logs
    if not weather_data:
        logs.append("Pipeline interrupted: Failed to fetch weather data.")
        # Decide if you want to continue or stop
        return logs, {"alert": None, "message": "Failed to fetch Weather"}
    logs.append(f"[WeatherAgent] Fetch successful. Temp: {weather_data.get('temperature_celsius', 'N/A')}°C")

    # Check if we have the necessary data (redundant check if handled above, but safe)
    if not aqi_data or not weather_data:
         logs.append("Pipeline cannot proceed without both AQI and Weather data.")
         logs.append("======= Pipeline Finished with Errors =======")
         return logs, {"alert": None, "message": "Missing required data"}

    # 4. Store Data
    logs.append("[StorageAgent] Attempting to store data...")
    storage_success = store_data_csv(aqi_data, weather_data, config) # store_data_csv prints its own logs
    if not storage_success:
        logs.append("Pipeline Warning: Failed to store data.")
        # Continue anyway for analysis/reporting
    else:
        logs.append("[StorageAgent] Storage successful.")

    # 5. Analyze Conditions
    logs.append("[AnalysisAgent] Analyzing conditions...")
    analysis_result = analyze_conditions(aqi_data, weather_data, config) # analyze_conditions prints its own logs
    logs.append(f"[AnalysisAgent] Analysis complete. Alert: {analysis_result.get('alert', 'N/A')}")


    # 6. Report Findings (The reporting agent is now the Streamlit UI)
    logs.append("[ReportingAgent] Preparing results for display.")
    logs.append("======= Pipeline Run Finished =======")

    # Return collected logs and the final analysis object
    return logs, analysis_result

# --- Keep the Entry Point (optional, allows running script directly too) ---
if __name__ == "__main__":
    # You can still run the script directly if needed, it will just print logs
    returned_logs, final_result = run_pipeline()
    # print("\n--- Direct Run Logs ---")
    # for log in returned_logs:
    #     print(log)
    # print("\n--- Direct Run Final Result ---")
    # print(final_result)
    # Or simply call the original print-heavy functions if preferred for direct runs
    print("Running climate_agent.py directly (output uses prints within functions)...")
    load_config()
    # ... call other functions if needed for testing ...