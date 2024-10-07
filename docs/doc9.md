# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 9. MQTTブローカを経由した測定データの蓄積

センサから取得したデータを一旦MQTTブローカに送信(Publish) し、そのデータを受信(Subscrivbe)してMariaDBにデータを蓄積することを考えます。

### 9.1 MQTTプローカにPublishする

MQTT Publisher側のプログラムを考えます。

キーボードから入力されたメッセージをPublishするプログラムを作成します。このプログラムを実行したあと、mosquitto_subクライアントでメッセージをsubscribeして確認してください。

`,qtt_publish01.py`

```python
#coding: utf-8

#Paho のMQTT ライブラリを使用する
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
```

プログラムの実行結果は次のとおりです。

* ターミナル１の操作

```bash
Connected with result code 0
Destination Host:  localhost
TOPIC:  tochigi/iot999/message
```

* ターミナル２の操作

新しいターミナルを起動し、msquitto_subクライアンの出力を確認します。

```bash
pi@raspberrypi:~/python_sql $ mosquitto_sub -h localhost -p 1883 -t tochigi/iot999/message
```

* ターミナル１の操作

```bash
message: Hello MQTT!
message: This is THE IoT.
```

* ターミナル２の操作

```bash
Hello MQTT!
This is THE IoT.
```

