# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 9. MQTTブローカを経由した測定データの蓄積

センサから取得したデータを一旦MQTTブローカに送信(Publish) し、そのデータを受信(Subscrivbe)してMariaDBにデータを蓄積することを考えます。

### 9.1 MQTTプローカにPublishする

MQTT Publisher側のプログラムを考えます。

キーボードから入力されたメッセージをPublishするプログラムを作成します。このプログラムを実行したあと、mosquitto_subクライアントでメッセージをsubscribeして確認してください。

`,qtt_publish01.py`

```python
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

### 9.2 センサで測定したデータをPublishする

センサで測定したデータをMQTTブローカへPublishします。

`mqtt_bme280_publish01.py`

```python
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
MQTT_TOPIC = 'tochigi/iot899/bme'

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
```

プログラムの実行結果は次のとおりです。

* ターミナル１の操作

```bash
Connected with result code 0
Destination Host:  localhost
TOPIC:  tochigi/iot899/bme
publish するデータ:  {"timestamp": "2024-10-07T23:54:50.547143+00:00", "temperature": 26.72680231416598, "humidity": 57.53434981211512, "pressure": 997.8079720341007}
publish するデータ:  {"timestamp": "2024-10-07T23:55:00.555341+00:00", "temperature": 26.731868814124027, "humidity": 57.55789094105844, "pressure": 997.7028226020932}
publish するデータ:  {"timestamp": "2024-10-07T23:55:10.565033+00:00", "temperature": 26.731868814124027, "humidity": 57.56373069656037, "pressure": 997.7028226020932}
```

* ターミナル２の操作

```bash
pi@raspberrypi:~/python_sql $ mosquitto_sub -h localhost -p 1883 -t tochigi/iot899/bme
```

```bash
{"timestamp": "2024-10-07T23:54:50.547143+00:00", "temperature": 26.72680231416598, "humidity": 57.53434981211512, "pressure": 997.8079720341007}
{"timestamp": "2024-10-07T23:55:00.555341+00:00", "temperature": 26.731868814124027, "humidity": 57.55789094105844, "pressure": 997.7028226020932}
{"timestamp": "2024-10-07T23:55:10.565033+00:00", "temperature": 26.731868814124027, "humidity": 57.56373069656037, "pressure": 997.7028226020932}
```

### 9.3 プログラムをモジュール分割する

前節で作成したプログラムをモジュール分割することを考えます。

`mqtt_bme280_publish02.py`

```python
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
MQTT_TOPIC = 'tochigi/iot899/bme'

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
```

`mqtt_ambient_pub.py`

```python
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
```

プログラムの実行結果は次のとおりです。

* ターミナル１の操作

```bash
Connected with result code 0
Destination Host:  localhost
TOPIC:  tochigi/iot899/bme
publish するデータ:  {"timestamp": "2024-10-08T00:06:47.347754+00:00", "temperature": 26.964928126806626, "humidity": 57.82917887063231, "pressure": 997.7673772475841}
publish するデータ:  {"timestamp": "2024-10-08T00:06:57.357197+00:00", "temperature": 26.97506115437136, "humidity": 57.84707564655465, "pressure": 997.7270485520521}
publish するデータ:  {"timestamp": "2024-10-08T00:07:07.366935+00:00", "temperature": 26.980127668590285, "humidity": 57.76546467860513, "pressure": 997.6785398845532}
```

* ターミナル２の操作

```bash
pi@raspberrypi:~/python_sql $ mosquitto_sub -h localhost -p 1883 -t tochigi/iot899/bme
```

```bash
{"timestamp": "2024-10-08T00:06:47.347754+00:00", "temperature": 26.964928126806626, "humidity": 57.82917887063231, "pressure": 997.7673772475841}
{"timestamp": "2024-10-08T00:06:57.357197+00:00", "temperature": 26.97506115437136, "humidity": 57.84707564655465, "pressure": 997.7270485520521}
{"timestamp": "2024-10-08T00:07:07.366935+00:00", "temperature": 26.980127668590285, "humidity": 57.76546467860513, "pressure": 997.6785398845532}
```

### 9.4 MQTTブローカからSubscribeしてデータベースに追加する

MQTTブローカからデータをSubscribeして、データベースに追加することを考えます。

測定データをPublishする`mqtt_bme280_publish02.py`を実行している間に、このプログラムを実行します。
