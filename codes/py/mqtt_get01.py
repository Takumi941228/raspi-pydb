#coding: utf-8

#PahoのMQTTライブラリを使用する
import paho.mqtt.client as mqtt

MQTT_HOST = '10.45.48.110'
MQTT_PORT = 1883
MQTT_TOPIC = 'esp32/bme'

#サーバからCONNACK応答を受信したときに実行されるコールバック
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  #どのtopicにsubscribeするかを決定。
  #再接続のときも、自動的にon_connectが実行される
  mqttClient.subscribe(MQTT_TOPIC, qos=0)

#PUBLISHメッセージをサーバから受信したときのコールバック
def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))

mqttClient = mqtt.Client()
mqttClient.on_connect = on_connect
mqttClient.on_message = on_message

#MQTTブローカーに接続する
mqttClient.connect(MQTT_HOST, MQTT_PORT, 120)

#データを待ち受ける
mqttClient.loop_forever()