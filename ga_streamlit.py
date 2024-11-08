import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import deque
import json
import time
from utils.MQTTClients import MQTTListener, MQTTPusher  # Import the MQTTListener and MQTTPusher classes

# Enter the broker address
broker_address = "192.168.0.1"

# Initialize a dictionary to store the latest 10 readings for each sensor
sensor_data = {f'sensor{i}': deque(maxlen=10) for i in range(1, 7)}

# MQTT listener setup
mqtt_listener = MQTTListener(Host=broker_address, Port=1883, ListenTopic="ga/sensors/values")
mqtt_pusher = MQTTPusher(Host=broker_address, Port=1883)

# GPS data storage with a max length of 10
gps_coords = deque(maxlen=10)

# Initialize Streamlit page
st.set_page_config(page_title="Sensor Data and GPS", layout="centered")

# Display the Streamlit app
st.title("Real-time Sensor Data and GPS")
st.write("Listening for sensor data and GPS coordinates...")

def start_command():
    mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Start_Stop": "Start"}))

def stop_command():
    mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Start_Stop": "Stop"}))

cont = st.container(border=True)
with cont:
    # Placeholder for the charts and map
    col1, col2 = st.columns([2, 1], gap='small')  # Allocate more width to the chart
    # Button callbacks


    with col1:
        if st.button("Start", use_container_width=True):
            start_command()
        if st.button("Stop", use_container_width=True):
            stop_command()
        chart_placeholder = st.empty()
    with col2:
        gps_map_placeholder = st.empty()

# Global state variable to track sensor activity
if 'last_message_received' not in st.session_state:
    st.session_state.last_message_received = time.time()

# Plotting function for sensor data
def plot_line_chart(df):
    fig = px.line(df,title=None)
    chart_placeholder.plotly_chart(fig, use_container_width=True, on_select="ignore")

# Plotting function for GPS coordinates using Plotly
def plot_gps_map(coords):
    if coords:
        lat, lon = zip(*coords)
        fig = go.Figure(go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode='markers',
            marker=go.scattermapbox.Marker(size=9, color='red'),
            text=["GPS Point"] * len(coords)
        ))
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                zoom=12,
                center=dict(lat=39.1836, lon=-96.5717)
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        gps_map_placeholder.plotly_chart(fig, use_container_width=True, on_select="ignore")

# Initial map display
plot_gps_map(gps_coords)

# Main loop to update the Streamlit app
while True:
    current_time = time.time()
    if len(mqtt_listener.Messages) > 0:
        msg = mqtt_listener.Messages.pop()
        payload = json.loads(msg.payload)
        st.session_state.last_message_received = current_time  # Update last message received time
        try:
            sensor_values = payload['sensors']
            latitude = payload['lat']
            longitude = payload['long']


            for sensor_id, value in sensor_values.items():
                sensor_data[sensor_id].append(value)

            gps_coords.append((latitude, longitude))

            data = {sensor: list(values) for sensor, values in sensor_data.items()}
            df = pd.DataFrame(data)
            plot_line_chart(df)
            plot_gps_map(gps_coords)

        except KeyError as ke:
            print(ke)
        


    # Check if the sensor data has stopped
    if current_time - st.session_state.last_message_received > 5:  # 10 seconds threshold
        payload = []
        sensor_data = {f'sensor{i}': deque(maxlen=10) for i in range(1, 7)}
        gps_coords = deque(maxlen=10)

    time.sleep(1)

st.stop()
