#coding: utf-8

#PahoのMQTTライブラリを使用する
import paho.mqtt.client as mqtt #モジュールをインポート
import bme280mod                #BME280センサ関連を取扱う
import time                     #時間を取扱う
import datetime                 #日付と時刻を取扱う

#JSONに関するライブラリを使用する
import json

#タイムゾーンを取り扱う
from pytz import timezone

#MQTTメッセージをPUBLISHする処理
import mqtt_ambient_pub

#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_iot_899'

#接続先情報
MQTT_HOST = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'raspi/bme'

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init()   #BME280センサを初期化

    #MQTTブローカに接続
    mqtt_ambient_pub.connect(MQTT_HOST, MQTT_PORT, MQTT_TOPIC)

    #メッセージを開始
    mqtt_ambient_pub.loop_start()

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
        mqtt_ambient_pub.publish(send_json)
 
        #10秒やすみ
        time.sleep(10)
main()