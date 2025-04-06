# Local Air Quality & Weather Correlator Agent

## Goal
Create a pipeline that fetches current air quality and weather data for a specific location, stores it, and checks if conditions exceed predefined thresholds (e.g., poor air quality combined with high temperature).

## Agentic Structure

A sequence of specialized functions (our "agents") passing data along.
It follows a defined pipeline structure (Config -> Fetch AQI -> Fetch Weather -> Store -> Analyze -> Report).
Each function/step has a distinct, specialized role, acting like a simple agent.
Data flows sequentially through the pipeline.


# Pipeline Steps & "Agents"

- *ConfigAgent* (Configuration Loader):
    
    **Task**: Reads configuration settings (e.g., target city/coordinates, AQI threshold, temperature threshold) potentially from a simple config.json file or directly in the script.
    
    **Output**: Configuration dictionary.

- *AQIAgent* (Air Quality Fetcher):

    **Task**: Takes location coordinates from ConfigAgent. Uses a free API like the OpenWeatherMap Air Pollution API (requires free API key) or OpenAQ API to get the current Air Quality Index (AQI) and pollutant levels (PM2.5, O3, etc.).
    
    **Input**: Location coordinates.
    
    **Output**: Dictionary with AQI data and timestamp.

- *WeatherAgent* (Weather Fetcher):

    **Task**: Takes location coordinates from ConfigAgent. Uses a free API like OpenWeatherMap Current Weather API (uses the same free API key as above) or Open-Meteo (no key needed, very generous free tier) to get current temperature, humidity, wind speed.
    
    **Input**: Location coordinates.
    
    **Output**: Dictionary with weather data and timestamp.

- *AnalysisAgent* (Condition Checker):

    **Task**: Takes the latest AQI and weather data (either directly or by querying the last entry from the DB/CSV). Compares values against the thresholds defined in the config (e.g., if aqi > 100 and temperature > 30:).
    
    **Input**: Latest AQI data, Weather data, Thresholds from Config.
    
    **Output**: Boolean flag (alert needed?) and a descriptive message.

- *ReportingAgent* (Notifier):
    
    **Task**: Takes the output from AnalysisAgent. If an alert is needed, print a clear message to the console (e.g., "ALERT: Poor Air Quality (AQI: 110) and High Temperature (32°C) detected in [City Name]!").
    
    **Input**: Alert flag and message.

    **Output**: Prints message to console.

## Key Technologies:

1. **Python**

    Libraries:

    - *requests*: For making API calls.

    - *json*: For handling API responses and config file.

    - *datetime*: For timestamps.

    - *csv*: For simple file storage.


2. Free APIs:

- **OpenWeatherMap** (needs free API key signup)
