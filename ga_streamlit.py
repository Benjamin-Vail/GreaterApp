import streamlit as st
import MQTTClients
import pandas as pd
import json
from time import sleep
import matplotlib.pyplot as plt
import sys

should_run = True
x_data = []
y_data = []

# def on_message(client, userdata, message):
#     global mqtt_data
#     msg = message.pop()
#     mqtt_data = json.loads(msg.payload)
#     print(mqtt_data)
    # mqtt_data = json_data
    

if __name__ == '__main__':        
    MQTTSub, MQTTPub = None,None
                  
    while(MQTTSub is None):
        try:
            MQTTPub = MQTTClients.MQTTPusher('192.168.0.107',1883)
            MQTTSub = MQTTClients.MQTTListener('192.168.0.107',1883,"gatest")
            print("Connected")
        except ConnectionRefusedError:
            print("Connection Error\nRetrying")
            sleep(2)
                
    st.set_page_config(
    page_title="GA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
    )
    st.sidebar.title("Navigation")
    
    if st.sidebar.button("Publish JSON"):
        json_data = json.dumps({"Command": "Start"})
        MQTTPub.PushData("ece631/finalproject/status/alert", json_data)
        st.success("JSON data published")
        
    if st.sidebar.button("Stop client"):
        should_run = False
        sys.exit()
        
    plot_placeholder = st.empty()

    try:    
        while should_run:
            if(len(MQTTSub.AMessages)==0):
                pass
            else:
                msg = MQTTSub.AMessages.pop()
                mqtt_data = json.loads(msg.payload)
                
                if mqtt_data["x"] and mqtt_data["y"]:
                    xval = mqtt_data["x"]
                    yval = mqtt_data["y"]
                    
                    x_data.append(xval)
                    y_data.append(yval)
                    
                    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
                    ax.scatter(x_data, y_data)
                    
                    with plot_placeholder.container():
                        st.pyplot(fig)     
            sleep(0.2)   
    
    except KeyboardInterrupt:
        print("interupted")
        should_run = False
        sys.exit()
        
    except Exception as e:
        print(e)
        
    finally:
        del MQTTPub
        del MQTTSub