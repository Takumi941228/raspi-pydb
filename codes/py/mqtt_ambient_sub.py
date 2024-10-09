#coding: utf-8

#MQTTに関するライブラリを使用する
import paho.mqtt.client as mqtt

#JSONに関するライブラリを使用する
import json

#日付・時刻に関するライブラリを使用する
from datetime import datetime as dt
from dateutil import parser
from pytz import timezone

#topicを保存する変数
pub_topic = ''

#mqttClientを指すための変数を用意
mqttClient = None

#コールバック関数
handler_on_mqtt_data_arrive = None

#サーバからCONNACK 応答を受信したときに実行されるコールバック
def on_connect(client, userdata, flags, rc):
    global mqttClient
    print("Connected with result code "+str(rc))

    #どのtopicにsubscribeするかを決定
    #再接続のときも、自動的にon_connectが実行される
    mqttClient.subscribe(pub_topic, qos=2)

#PUBLISHメッセージをMQTTブローカから受信したときのコールバック
def on_message(client, userdata, msg):
    #受信データはjson形式となっている、これを辞書形式に変更
    json_msg = json.loads(msg.payload)

    ts = json_msg['timestamp']
    temp = json_msg['temperature']
    hum = json_msg['humidity']
    press = json_msg['pressure']

    #受信した日付はUTCなのでJSTに変換
    date_jst = parser.parse(ts).astimezone(timezone('Asia/Tokyo'))

    #データをディクショナリ形式にまとめる
    new_data ={
        'timestamp' : date_jst,
        'temperature': temp,
        'humidity' : hum,
        'pressure' : press
    };

    handler_on_mqtt_data_arrive(new_data)
    
#MQTTブローカに接続する
def connect(host, port, topic):
    global mqttClient
    global pub_topic
    mqttClient = mqtt.Client()
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    pub_topic = topic

    #MQTTブローカーに接続する
    mqttClient.connect(host, port, 120)

#MQTTメッセージが到着したときに実行されるコールバック関数をセットする
def add_handler_on_mqtt_data_arrive(handler):
    global handler_on_mqtt_data_arrive
    handler_on_mqtt_data_arrive = handler

#MQTTメッセージを待ち受ける
def loop():
    mqttClient.loop_forever()