import streamlit as st
import pandas as pd
import plotly.express as px
from collections import deque
import json
import time
from utils.MQTTClients import MQTTListener, MQTTPusher  # Import the MQTTListener and MQTTPusher classes
import folium
from streamlit_folium import st_folium
from fastkml import kml
import geojson

# Enter the broker address
broker_address = "192.168.0.107"
kml_path = './maps/man_ks_area.kml'  # Path to the KML file

# Initialize a dictionary to store the latest 10 readings for each sensor
sensor_data = {f'sensor{i}': deque(maxlen=10) for i in range(1, 7)}

# GPS data storage
gps_coords = []

# Initialize Streamlit page
st.set_page_config(page_title="Sensor Data and GPS", layout="wide")

# Display the Streamlit app
st.title("Real-time Sensor Data and GPS")
st.write("Listening for sensor data and GPS coordinates...")

# Placeholder for the charts and map
chart_placeholder = st.empty()
map_placeholder = st.empty()

# MQTT listener setup
mqtt_listener = MQTTListener(Host=broker_address, Port=1883, ListenTopic="ga/sensors/values")
mqtt_listener_gps = MQTTListener(Host=broker_address, Port=1883, ListenTopic="ga/gps/coords")
mqtt_pusher = MQTTPusher(Host=broker_address, Port=1883)

# Plotting function for sensor data
def plot_line_chart(df):
    fig = px.line()
    for column in df.columns:
        fig.add_scatter(x=df.index, y=df[column], mode='lines', name=column)
    fig.update_layout(title="Sensor Data", xaxis_title="Reading", yaxis_title="Value")
    chart_placeholder.plotly_chart(fig, use_container_width=True)

# Convert KML to GeoJSON
def kml_to_geojson(kml_path):
    with open(kml_path, 'rb') as kml_file:
        k = kml.KML()
        k.from_string(kml_file.read())
        features = list(k.features())
        geojson_obj = geojson.FeatureCollection([geojson.loads(f.to_string()) for f in features])
        return geojson.dumps(geojson_obj)

# Initial map plot function
def init_map():
    kml_map = folium.Map(location=[39.1836, -96.5717], zoom_start=12)  # Center on Manhattan, KS
    geojson_data = kml_to_geojson(kml_path)
    folium.GeoJson(geojson_data).add_to(kml_map)
    return kml_map

# Plotting function for GPS coordinates on KML map
def plot_gps_map(coords, kml_map):
    for coord in coords:
        folium.Marker(location=coord, popup='GPS Point').add_to(kml_map)

    st_folium(kml_map, width=700, height=500)

# Initialize the map
kml_map = init_map()

# Button callbacks
def start_command():
    mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Command": "start"}))

def stop_command():
    mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Command": "stop"}))

# Create buttons
cont2 = st.container()
with cont2:
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        if st.button("Start", use_container_width=True):
            start_command()
    with col3:
        if st.button("Stop", use_container_width=True):
            stop_command()

# Initial map display
plot_gps_map(gps_coords, kml_map)

# Main loop to update the Streamlit app
while True:
    if len(mqtt_listener.Messages) > 0:
        msg = mqtt_listener.Messages.pop()
        sensor_values = json.loads(msg.payload)

        for sensor_id, value in sensor_values.items():
            sensor_data[sensor_id].append(value)

        data = {sensor: list(values) for sensor, values in sensor_data.items()}
        df = pd.DataFrame(data)
        plot_line_chart(df)

    if len(mqtt_listener_gps.Messages) > 0:
        msg = mqtt_listener_gps.Messages.pop()
        gps_data = json.loads(msg.payload)
        latitude = gps_data['latitude']
        longitude = gps_data['longitude']
        gps_coords.append((latitude, longitude))

        plot_gps_map(gps_coords, kml_map)

    time.sleep(1)


# Main loop to update

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from collections import deque
# import json
# from utils.MQTTClients import MQTTListener, MQTTPusher  
# import time

# # Enter the broker address
# broker_address = "192.168.0.107"

# # Initialize a dictionary to store the latest 10 readings for each sensor
# sensor_data = {f'sensor{i}': deque(maxlen=10) for i in range(1, 7)}

# # Initialize Streamlit page
# st.set_page_config(page_title="Sensor Data", layout="wide")

# # Display the Streamlit app
# st.title("Real-time Sensor Data")
# st.write("Listening for sensor data...")

# # Placeholder for the Plotly chart
# chart_placeholder = st.empty()

# # MQTT listener setup
# mqtt_listener = MQTTListener(Host=broker_address, Port=1883, ListenTopic="ga/sensors/values")
# mqtt_pusher = MQTTPusher(Host=broker_address, Port=1883)

# def plot_line_chart(df, key):
#     fig = px.line()
#     for column in df.columns:
#         fig.add_scatter(x=df.index, y=df[column], mode='lines', name=column)
#     fig.update_layout(title="Sensor Data", xaxis_title="Reading", yaxis_title="Value")
#     # Update the chart placeholder in Streamlit
#     chart_placeholder.plotly_chart(fig, use_container_width=True, key=key)

# # Button callbacks
# def start_command():
#     mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Command": "start"}))

# def stop_command():
#     mqtt_pusher.PushData("ga/sensors/control", json.dumps({"Command": "stop"}))

# # Create buttons
# cont2 = st.container()
# with cont2:
#     col1, col2, col3, col4 = st.columns(4)
#     with col2:
#         if st.button("Start", use_container_width=True):
#             start_command()
#     with col3:
#         if st.button("Stop", use_container_width=True):
#             stop_command()

# # Main loop to update the Streamlit app

# while True:
#     if len(mqtt_listener.Messages) > 0:
#         msg = mqtt_listener.Messages.pop()
#         sensor_values = json.loads(msg.payload)

#         # Append the new values to the respective sensor queues
#         for sensor_id, value in sensor_values.items():
#             sensor_data[sensor_id].append(value)

#         # Convert sensor_data to a DataFrame
#         data = {sensor: list(values) for sensor, values in sensor_data.items()}
#         df = pd.DataFrame(data)
#         print(df)

#         # Update the Plotly line chart with a unique key
#         plot_line_chart(df, key=f"sensor_chart_{time.time()}")

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
