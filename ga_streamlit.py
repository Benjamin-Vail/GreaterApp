import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import deque
import json
import time
from utils.MQTTClients import MQTTListener, MQTTPusher  # Import the MQTTListener and MQTTPusher classes

# Enter the broker address
broker_address = "192.168.0.107"

# Initialize a dictionary to store the latest 10 readings for each sensor
sensor_data = {f'sensor{i}': deque(maxlen=10) for i in range(1, 7)}

# GPS data storage with a max length of 10
gps_coords = deque(maxlen=10)

# Initialize Streamlit page
st.set_page_config(page_title="Sensor Data and GPS", layout="centered")

# Display the Streamlit app
st.title("Real-time Sensor Data and GPS")
st.write("Listening for sensor data and GPS coordinates...")

# Placeholder for the charts and map
col1, col2 = st.columns(2)
with col1:
    chart_placeholder = st.empty()
with col2:
    gps_map_placeholder = st.empty()

# MQTT listener setup
mqtt_listener = MQTTListener(Host=broker_address, Port=1883, ListenTopic="ga/sensors/values")
mqtt_pusher = MQTTPusher(Host=broker_address, Port=1883)

# Plotting function for sensor data
def plot_line_chart(df):
    fig = px.line(df, title="Sensor Data")
    chart_placeholder.plotly_chart(fig, use_container_width=True)

# Plotting function for GPS coordinates using Plotly
def plot_gps_map(coords):
    if coords:
        lat, lon = zip(*coords)
        fig = go.Figure(go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode='markers',
            marker=go.scattermapbox.Marker(size=9),
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
        gps_map_placeholder.plotly_chart(fig, use_container_width=True)

# Button callbacks
def start_command():
    mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Command": "start"}))

def stop_command():
    mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Command": "stop"}))

# Create buttons
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        if st.button("Start", use_container_width=True):
            start_command()
    with col3:
        if st.button("Stop", use_container_width=True):
            stop_command()

# Initial map display
plot_gps_map(gps_coords)

# Main loop to update the Streamlit app
while True:
    if len(mqtt_listener.Messages) > 0:
        msg = mqtt_listener.Messages.pop()
        payload = json.loads(msg.payload)

        sensor_values = payload['sensors']
        latitude = payload['latitude']
        longitude = payload['longitude']

        for sensor_id, value in sensor_values.items():
            sensor_data[sensor_id].append(value)

        gps_coords.append((latitude, longitude))

        data = {sensor: list(values) for sensor, values in sensor_data.items()}
        df = pd.DataFrame(data)
        plot_line_chart(df)
        plot_gps_map(gps_coords)

    time.sleep(1)


# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from collections import deque
# import json
# import time
# from utils.MQTTClients import MQTTListener, MQTTPusher  # Import the MQTTListener and MQTTPusher classes

# # Enter the broker address
# broker_address = "192.168.0.107"

# # Initialize a dictionary to store the latest 10 readings for each sensor
# sensor_data = {f'sensor{i}': deque(maxlen=10) for i in range(1, 7)}

# # GPS data storage with a max length of 10
# gps_coords = deque(maxlen=10)

# # Initialize Streamlit page
# st.set_page_config(page_title="Sensor Data and GPS", layout="centered")

# # Display the Streamlit app
# st.title("Real-time Sensor Data and GPS")
# st.write("Listening for sensor data and GPS coordinates...")

# # Placeholder for the charts and map
# col1, col2 = st.columns(2)
# with col1:
#     chart_placeholder = st.empty()
# with col2:
#     gps_map_placeholder = st.empty()

# # MQTT listener setup
# mqtt_listener = MQTTListener(Host=broker_address, Port=1883, ListenTopic="ga/sensors/values")
# mqtt_pusher = MQTTPusher(Host=broker_address, Port=1883)

# # Plotting function for sensor data
# def plot_line_chart(df):
#     fig = px.line(df, title="Sensor Data")
#     chart_placeholder.plotly_chart(fig, use_container_width=True)

# # Plotting function for GPS coordinates using Plotly
# def plot_gps_map(coords):
#     if coords:
#         lat, lon = zip(*coords)
#         fig = go.Figure(go.Scattermapbox(
#             lat=lat,
#             lon=lon,
#             mode='markers',
#             marker=go.scattermapbox.Marker(size=9),
#             text=["GPS Point"] * len(coords)
#         ))
#         fig.update_layout(
#             mapbox=dict(
#                 style="open-street-map",
#                 zoom=12,
#                 center=dict(lat=39.1836, lon=-96.5717)
#             ),
#             margin=dict(l=0, r=0, t=0, b=0)
#         )
#         gps_map_placeholder.plotly_chart(fig, use_container_width=True)

# # Button callbacks
# def start_command():
#     mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Command": "start"}))

# def stop_command():
#     mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Command": "stop"}))

# # Create buttons
# with st.container():
#     col1, col2, col3, col4 = st.columns(4)
#     with col2:
#         if st.button("Start", use_container_width=True):
#             start_command()
#     with col3:
#         if st.button("Stop", use_container_width=True):
#             stop_command()

# # Initial map display
# plot_gps_map(gps_coords)

# # Main loop to update the Streamlit app
# while True:
#     if len(mqtt_listener.Messages) > 0:
#         msg = mqtt_listener.Messages.pop()
#         payload = json.loads(msg.payload)

#         sensor_values = payload['sensors']
#         latitude = payload['latitude']
#         longitude = payload['longitude']

#         for sensor_id, value in sensor_values.items():
#             sensor_data[sensor_id].append(value)

#         gps_coords.append((latitude, longitude))

#         data = {sensor: list(values) for sensor, values in sensor_data.items()}
#         df = pd.DataFrame(data)
#         plot_line_chart(df)
#         plot_gps_map(gps_coords)

#     time.sleep(1)





# # Use this format for sensor data
# # {
# #     "sensor1": 33.5,
# #     "sensor2": 65.6,
# #     "sensor3": 58.2,
# #     "sensor4": 32.3,
# #     "sensor5": 37.4,
# #     "sensor6": 14.8
# # }
