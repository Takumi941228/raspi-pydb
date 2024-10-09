#coding: utf-8

#MQTTに関するライブラリを使用する
import paho.mqtt.client as mqtt

#JSONに関するライブラリを使用する
import json

#日付・時刻に関するライブラリを使用する
from datetime import datetime as dt 

#DB関連を取扱う
import db_ambient

#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_mqtt_999'

#MQTTブローカへの接続に必要な情報
MQTT_HOST = 'MQTTブローカのIPアドレス'
MQTT_PORT = 1883
MQTT_TOPIC = 'esp32/bme'
#mqttClient を指すための変数を用意
mqttClient = None
#コールバック関数
handler_on_mqtt_data_arrive = None

#サーバからCONNACK応答を受信したときに実行されるコールバック
def on_connect(client, userdata, flags, rc):
  global mqttClient
  print("Connected with result code "+str(rc))

  #どのtopicにsubscribeするかを決定。
  #再接続のときも、自動的にon_connectが実行される
  mqttClient.subscribe(MQTT_TOPIC, qos=2)

#PUBLISHメッセージをMQTTブローカから受信したときのコールバック
def on_message(client, userdata, msg):
  #受信データはjson形式となっている、これを辞書形式に変更
  json_msg = json.loads(msg.payload)

  #各項目を取り出し
  date_raw = json_msg["timestamp"]
  humi_raw = json_msg["humid"]
  press_raw = json_msg["press"]
  temp_raw = json_msg["temp"]
  
  #各データを扱いやすい形に変換
  date = str(dt.today().strftime('%Y-%m-%d')) + " " + str(date_raw) #日付と時間を文字列連結
  #小数点第二位で四捨五入
  temp = round(temp_raw, 2)
  humi = round(humi_raw, 2)
  press = round(press_raw, 2)

  #データをディクショナリ形式にまとめる
  new_data ={
    'timestamp' : date,
    'temperature' : temp,
    'humidity' : humi,
    'pressure' : press
  };

  handler_on_mqtt_data_arrive(new_data)

#MQTTブローカに接続する
def connect():
  global mqttClient
  mqttClient = mqtt.Client()
  mqttClient.on_connect = on_connect
  mqttClient.on_message = on_message

  #MQTTブローカーに接続する
  mqttClient.connect(MQTT_HOST, MQTT_PORT, 120)

#MQTTメッセージが到着したときに実行されるコールバック関数をセットする
def add_handler_on_mqtt_data_arrive(handler):
  global handler_on_mqtt_data_arrive
  handler_on_mqtt_data_arrive = handler

#MQTTメッセージを待ち受ける
def loop():
  mqttClient.loop_forever()