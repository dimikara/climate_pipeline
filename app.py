import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Import the pipeline runner function from your original script
from climate_agent import run_pipeline, load_config # Also import load_config to show it

# --- Page Configuration (Optional) ---
st.set_page_config(
    page_title="Climate Pipeline Runner",
    page_icon="🌦️",
    layout="wide"
)

# --- Load Configuration ---
# Load config once and display it
config = load_config()

# --- App Title ---
st.title("🌦️ Local Climate & Air Quality Pipeline")
st.markdown("Run the agentic pipeline to fetch, store, and analyze local weather and air quality data.")

# --- Display Configuration ---
if config:
    st.subheader("Current Configuration")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Target City", config['location']['city_name'])
        st.write(f"Coordinates: ({config['location']['latitude']}, {config['location']['longitude']})")
    with col2:
        st.metric("AQI Alert Threshold", f">= {config['thresholds']['aqi_alert']}")
        st.metric("Temp Alert Threshold", f"> {config['thresholds']['temp_alert_celsius']} °C")
    # Optional: Show full config in an expander
    with st.expander("View Full Configuration"):
        st.json(config)
else:
    st.error("Failed to load configuration (config.json). Please check the file.")
    st.stop() # Stop the app if config fails

# --- Pipeline Execution Section ---
st.divider()
st.header("Run Pipeline")

if st.button("▶️ Run Now", type="primary"):
    st.info("Pipeline execution started...")
    # Use a spinner while the pipeline runs
    with st.spinner('Fetching data, storing, and analyzing...'):
        # Call the modified run_pipeline function
        logs, final_result = run_pipeline()

    st.success("Pipeline execution finished!")

    # --- Display Results ---
    st.subheader("Pipeline Results")

    # Display Final Analysis Message
    if final_result:
        if final_result.get("alert") is None: # Handle errors reported by run_pipeline
             st.error(f"Analysis incomplete: {final_result.get('message', 'Unknown error')}")
        elif final_result.get("alert"):
            st.warning(f"🚨 {final_result['message']}") # Use warning or error for alerts
        else:
            st.success(f"✅ {final_result['message']}") # Use success for normal conditions
    else:
        st.error("Analysis could not be completed.")


    # Display Logs in an Expander
    with st.expander("Show Detailed Logs"):
        st.code('\n'.join(logs), language=None) # Display logs as preformatted text

else:
    st.write("Click the button above to run the pipeline.")


# --- Display Data Log Section ---
st.divider()
st.header("📊 Data Log Viewer")

log_file = config['storage']['csv_filename']

if os.path.exists(log_file):
    try:
        df = pd.read_csv(log_file)
        st.dataframe(df.tail(10)) # Show the last 10 entries
        st.caption(f"Displaying latest entries from `{log_file}`")

        # Option to download the CSV
        with open(log_file, "rb") as fp:
            st.download_button(
                label="Download Full Log (CSV)",
                data=fp,
                file_name=log_file,
                mime="text/csv"
            )

    except pd.errors.EmptyDataError:
        st.info(f"`{log_file}` exists but is empty.")
    except Exception as e:
        st.error(f"Error reading or displaying the CSV log file: {e}")
else:
    st.info(f"Log file (`{log_file}`) not found. Run the pipeline to create it.")


# --- Footer (Optional) ---
st.divider()
st.caption(f"Last Refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")