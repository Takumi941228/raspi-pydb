#coding: utf-8

#MQTTに関するライブラリを使用する
import paho.mqtt.client as mqtt

#JSONに関するライブラリを使用する
import json

#日付・時刻に関するライブラリを使用する
from datetime import datetime as dt
from dateutil import parser
from pytz import timezone

#mqttClientを指すための変数を用意
mqttClient = None

#topicを保存する変数
pub_topic = ''

#サーバからCONNACK 応答を受信したときに実行されるコールバック
def on_connect(client, userdata, flags, rc):
    global mqttClient
    print("Connected with result code "+str(rc))

    #どのtopicにsubscribeするかを決定
    #再接続のときも、自動的にon_connectが実行される
    mqttClient.subscribe(pub_topic, qos=2)

#MQTTブローカに接続する
def connect(host, port, topic):
    global mqttClient
    global pub_topic
    
    mqttClient = mqtt.Client()
    mqttClient.on_connect = on_connect
    pub_topic = topic
    
    #MQTTブローカーに接続する
    mqttClient.connect(host, port, 120)

def publish(data):
    mqttClient.publish(pub_topic, str(data))

#MQTTメッセージを待ち受ける
def loop_start():
    mqttClient.loop_start()