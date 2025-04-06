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


2. **OpenWeatherMap** (needs free API key signup)


# How to Run it

**A.** 

- Open your terminal or command prompt.

- Navigate (*cd*) into the *climate_pipeline* folder where you saved the files.

- Make sure your *config.json* is updated with your API key and desired location/thresholds.

- Run the script using: *python climate_agent.py*

or

**B.**

- Open your terminal or command prompt.

- Navigate (*cd*) into the *climate_pipeline* folder where you saved the files.

- Make sure your *config.json* is updated with your API key and desired location/thresholds.

- Run the script using: *streamlit run app.py*


# Expected Output

You will see output in your terminal showing the progress of each agent:

```
    ======= Starting Climate Data Pipeline =======
    [ConfigAgent] Loading configuration...
    [ConfigAgent] Configuration loaded successfully.
    [AQIAgent] Fetching air quality data...
    [AQIAgent] Air Quality Index (AQI): 1
    [WeatherAgent] Fetching weather data...
    [WeatherAgent] Current Temperature: 5.51°C, Description: overcast clouds
    [StorageAgent] Storing data...
    [StorageAgent] Data appended successfully to climate_data_log.csv
    [AnalysisAgent] Analyzing conditions...
    [AnalysisAgent] Analysis complete. Alert needed: False
    Running climate_agent.py directly (output uses prints within functions)...
    [ConfigAgent] Loading configuration...
    [ConfigAgent] Configuration loaded successfully.
    ======= Pipeline Run Finished =======
```

![image](https://github.com/user-attachments/assets/ffd55eba-43ab-44e8-a629-1b56187e22d6)



If the thresholds are met, the Analysis Result message will change accordingly.

A climate_data_log.csv file will also be created (or appended to) in the same folder, containing the collected data.


# Next Steps & Possible Improvements

* Error Handling: Add more robust error handling for network issues, API rate limits, or unexpected data formats.

* Scheduling: Use cron (Linux/macOS) or Task Scheduler (Windows) to run this script automatically (e.g., every hour).

* More Complex Analysis: Calculate moving averages, detect trends, or correlate specific pollutants with weather patterns.

* Notifications: Instead of just printing, use libraries like smtplib (email) or APIs for Slack/Discord/etc. to send alerts.

* Visualization: Use libraries like matplotlib or seaborn to plot the data stored in the CSV/database.

* Multiple Locations: Modify the config and agents to handle monitoring several locations.
