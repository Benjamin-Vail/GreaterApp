import paho.mqtt.client as mqtt
import time
import json
import random

# MQTT Broker details
broker_address = "192.168.0.107"
topic = "ga/sensors/values"

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
        
        # Publish the sensor values as a JSON string
        client.publish(topic, json.dumps(sensor_values))
        
        # Print the published values for verification
        print("Published:", sensor_values)
        
        # Wait for a second before publishing the next set of values
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    client.loop_stop()
    client.disconnect()
