#coding: utf-8

#PahoのMQTTライブラリを使用する
import paho.mqtt.client as mqtt

#モジュールをインポート
import bme280mod #BME280センサ関連を取扱う
import time      #時間を取扱う
import datetime  #日付と時刻を取扱う

#JSONに関するライブラリを使用する
import json

#タイムゾーンを取り扱う
from pytz import timezone

#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_iot_899'

#MQTTブローカの情報
MQTT_HOST = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'raspi/bme'

#サーバからCONNACK応答を受信したときに実行されるコールバック
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #どのtopicにsubscribeするかを決定
    # 再接続のときも、自動的にon_connectが実行される
    mqttClient.subscribe(MQTT_TOPIC, qos=0)

#モジュール内に定義されているメソッドを呼び出す
bme280mod.init()   #BME280センサを初期化

mqttClient = mqtt.Client()
mqttClient.on_connect = on_connect

#MQTTブローカーに接続する
mqttClient.connect(MQTT_HOST, MQTT_PORT, 120)

#PUBLISHERを開始
mqttClient.loop_start()

#１秒やすみ
time.sleep(1)

print('Destination Host: ', MQTT_HOST)
print('TOPIC: ', MQTT_TOPIC)

while True:
    bme280mod.read_data() #測定
    sensor_data = bme280mod.get_data() #データを取得

    temp = sensor_data['temperature']
    hum = sensor_data['humidity']
    press = sensor_data['pressure']

    #現在時刻を世界協定時刻で取得
    ts = datetime.datetime.now(timezone('UTC')).isoformat()
 
    send_dict = {
        'timestamp' : ts,
        'temperature' : temp,
        'humidity' : hum,
        'pressure' : press
    }

    send_json = json.dumps(send_dict)
    print('publish するデータ: ', send_json)
    
    #MQTTブローカへPUBLISHする
    mqttClient.publish(MQTT_TOPIC, send_json)

    #10秒やすみ
    time.sleep(10)