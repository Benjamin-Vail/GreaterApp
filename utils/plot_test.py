import paho.mqtt.client as mqtt
import time
import json
import random

# MQTT Broker details
broker_address = "192.168.0.1"
topic = "ga/sensors/values"

# Latitude and longitude for the center point on Knox Lane, Manhattan, KS
center_lat = 39.195
center_lon = -96.565

# Helper function to generate random coordinates within a 20-acre area
def generate_random_coords(center_lat, center_lon):
    # 1 acre is approximately 63.614907 meters squared
    # 20 acres is approximately 1272.29814 meters squared
    # Converting meters to degrees (approx. 111139 meters per degree)
    area_radius = 1272.29814 / 111139  # Degree conversion for 20-acre radius

    lat = center_lat + random.uniform(-area_radius, area_radius)
    lon = center_lon + random.uniform(-area_radius, area_radius)
    return lat, lon

# Initialize MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker_address, 1883, 60)

# Start the MQTT client loop
client.loop_start()

try:
    while True:
        # Generate random flow values for each sensor
        sensor_values = {
            f"sensor{i}": round(random.uniform(10.0, 100.0), 2) for i in range(1, 7)
        }
        
        # Generate random GPS coordinates
        lat, lon = generate_random_coords(center_lat, center_lon)
        
        # Combine sensor values and GPS coordinates into one JSON payload
        payload = {
            "sensors": sensor_values,
            "Lat": lat,
            "Long": lon
        }
        
        # Publish the payload as a JSON string
        client.publish(topic, json.dumps(payload))
        
        # Print the published values for verification
        print("Published:", payload)
        
        # Wait for a second before publishing the next set of values
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    client.loop_stop()
    client.disconnect()
