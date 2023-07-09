import paho.mqtt.client as mqtt

def on_connect(client,userdata,flags,rc):
    print("connected with result code " +str(rc))
    
    client.subscribe("/esp8266/temp")
    client.subscriber("/esp8266/hum")
    
    def on_message(client,userdata,message):
        print("recieved message '" +str(message.payload) + "'on topic'"+message.topic)
        
    def main():
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        
        mqtt_client.connect('localhost', 1883, 60)
        
        mqtt_client.loop_start()
        
    if __name__ == '__main__':
        print('mqtt to influxdb bridge')
        main()
        
        