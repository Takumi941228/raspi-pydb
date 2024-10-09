#coding: utf-8

#PahoのMQTTライブラリを使用する
import paho.mqtt.client as mqtt

import time #時間を取扱う

MQTT_HOST = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'tochigi/iot999/message'

#サーバからCONNACK応答を受信したときに実行されるコールバック
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    #どのtopicにsubscribeするかを決定
    #再接続のときも、自動的にon_connectが実行される
    mqttClient.subscribe(MQTT_TOPIC, qos=0)

mqttClient = mqtt.Client()
mqttClient.on_connect = on_connect

#MQTTブローカーに接続する
#ユーザ認証は使用しない
mqttClient.connect(MQTT_HOST, MQTT_PORT, 120)

#PUBLISHERを開始
mqttClient.loop_start()

#１秒やすみ
time.sleep(1)

print("Destination Host: ", MQTT_HOST)
print("TOPIC: ", MQTT_TOPIC)

while True:
    #キーボードからメッセージを入力
    message = input('message: ')
    
    #メッセージを PUBLISH する
    mqttClient.publish(MQTT_TOPIC, message)