# -*- coding: utf-8 -*-

#MQTTに関するライブラリを使用する
import paho.mqtt.client as mqtt

#JSONに関するライブラリを使用する
import json

#日付・時刻に関するライブラリを使用する
from datetime import datetime as dt

#DB関連を取扱う
import db_ambient

#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_mqtt_999';

#MQTTブローカへの接続に必要な情報
MQTT_HOST = '10.45.48.110'
MQTT_PORT = 1883
MQTT_TOPIC = 'esp32/bme'
#mqttClient を指すための変数を用意
mqttClient = None

#サーバからCONNACK応答を受信したときに実行されるコールバック
def on_connect(client, userdata, flags, rc):
  global mqttClient
  print("Connected with result code "+str(rc))

  #どのtopicにsubscribeするかを決定。
  #再接続のときも、自動的にon_connectが実行される
  mqttClient.subscribe(MQTT_TOPIC, qos=2)

#PUBLISHメッセージをサーバから受信したときのコールバック
def on_message(client, userdata, msg):
  #受信データは json 形式となっている、これを辞書形式に変更
  json_msg = json.loads(msg.payload)
  print('●new mqtt message arrived: ', json_msg)
  
  #各項目を取り出し
  date_raw = json_msg["timestamp"]
  humi_raw = json_msg["humid"]
  press_raw = json_msg["press"]
  temp_raw = json_msg["temp"]
  
  #各データを扱いやすい形に変換
  date = str(dt.today().strftime('%Y-%m-%d')) + " " + str(date_raw)
  temp = round(temp_raw, 2)
  humi = round(humi_raw, 2)
  press = round(press_raw, 2)

  #DBに渡すための新しいディクショナリ形式にまとめる。
  new_row ={
            "timestamp" : date,
            "identifier" : NODE_IDENTIFIER,
            "temperature" : temp,
            "humidity" : humi,
            "pressure" : press
            };

  #データベースの操作を行う------
  db_result = db_ambient.insert_row(new_row)
  print(' NEW_DATA: ', new_row)
  print(' クエリを実行しました。('+ str(db_result) +' row affected.)')

def mqtt_connect():
  global mqttClient
  mqttClient = mqtt.Client()
  mqttClient.on_connect = on_connect
  mqttClient.on_message = on_message

  #MQTTブローカーに接続する
  mqttClient.connect(MQTT_HOST, MQTT_PORT, 120)
  print('mqtt broker connected')

#データを待ち受ける
def mqtt_loop():
  print('waiting for mqtt message...')
  mqttClient.loop_forever()

def main():
  #DBサーバに接続する
  db_ambient.connect()
  print('db server connected')

  mqtt_connect()
  mqtt_loop()

main()