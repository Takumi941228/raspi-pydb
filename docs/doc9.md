# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 9. MQTTブローカを経由した測定データの蓄積

センサから取得したデータを一旦MQTTブローカに送信(Publish) し、そのデータを受信(Subscrivbe)してMariaDBにデータを蓄積することを考えます。MQTTブローカは、ローカルホスト（自分のRaspberryPi）にインストールされているものを利用します。

### 9.1 MQTTブローカーの構築

データの取得に使用するプロトコルであるMQTT通信を行うため、`mosquito`をインストールします。

```bash
pi@raspberrypi:~/python_sql $ sudo apt -y install mosquitto
```

別端末からパスワードなしで、MQTTブローカーにアクセスするには、ログイン認証をなしにする必要があります。

```bash
pi@raspberrypi:~ $ sudo apt -y install vim
```

```bash
pi@raspberrypi:~ $ sudo vim /etc/mosquitto/mosquitto.conf
```

* mosquitto.confに以下を追加
    * listener 1883
    * allow_anonymous true

```bash
# Place your local configuration in /etc/mosquitto/conf.d/
#
# A full description of the configuration file is at
# /usr/share/doc/mosquitto/examples/mosquitto.conf.example

pid_file /run/mosquitto/mosquitto.pid

persistence true
persistence_location /var/lib/mosquitto/

log_dest file /var/log/mosquitto/mosquitto.log

include_dir /etc/mosquitto/conf.d

listener 1883
allow_anonymous true
```

```bash
pi@raspberrypi:~ $ sudo systemctl restart mosquitto.service 
```

```bash
pi@raspberrypi:~ $ sudo systemctl status mosquitto.service 
```

```bash
● mosquitto.service - Mosquitto MQTT Broker
     Loaded: loaded (/lib/systemd/system/mosquitto.service; enabled; preset: enabled)
     Active: active (running) since Wed 2024-09-11 16:16:30 JST; 1min 2s ago
       Docs: man:mosquitto.conf(5)
             man:mosquitto(8)
    Process: 6633 ExecStartPre=/bin/mkdir -m 740 -p /var/log/mosquitto (code=exited, status=0/SUCCESS)
    Process: 6641 ExecStartPre=/bin/chown mosquitto /var/log/mosquitto (code=exited, status=0/SUCCESS)
    Process: 6642 ExecStartPre=/bin/mkdir -m 740 -p /run/mosquitto (code=exited, status=0/SUCCESS)
    Process: 6643 ExecStartPre=/bin/chown mosquitto /run/mosquitto (code=exited, status=0/SUCCESS)
   Main PID: 6644 (mosquitto)
      Tasks: 1 (limit: 3910)
        CPU: 50ms
     CGroup: /system.slice/mosquitto.service
             └─6644 /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf

 9月 11 16:16:30 raspberrypi systemd[1]: Starting mosquitto.service - Mosquitto MQTT Broker...
 9月 11 16:16:30 raspberrypi systemd[1]: Started mosquitto.service - Mosquitto MQTT Broker.
```

### 9.2 MQTTプローカにPublishする

MQTT Publisher側のプログラムを考えます。

キーボードから入力されたメッセージをPublishするプログラムを作成します。このプログラムを実行したあと、mosquitto_subクライアントでメッセージをsubscribeして確認してください。

`mqtt_publish01.py`

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

### 9.3 センサで測定したデータをPublishする

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

    #5秒やすみ
    time.sleep(5)
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
pi@raspberrypi:~/python_sql $ mosquitto_sub -h localhost -p 1883 -t raspi/bme
```

```bash
{"timestamp": "2024-10-07T23:54:50.547143+00:00", "temperature": 26.72680231416598, "humidity": 57.53434981211512, "pressure": 997.8079720341007}
{"timestamp": "2024-10-07T23:55:00.555341+00:00", "temperature": 26.731868814124027, "humidity": 57.55789094105844, "pressure": 997.7028226020932}
{"timestamp": "2024-10-07T23:55:10.565033+00:00", "temperature": 26.731868814124027, "humidity": 57.56373069656037, "pressure": 997.7028226020932}
```

### 9.4 プログラムをモジュール分割する

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
 
        #5秒やすみ
        time.sleep(5)

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
pi@raspberrypi:~/python_sql $ mosquitto_sub -h localhost -p 1883 -t raspi/bme
```

```bash
{"timestamp": "2024-10-08T00:06:47.347754+00:00", "temperature": 26.964928126806626, "humidity": 57.82917887063231, "pressure": 997.7673772475841}
{"timestamp": "2024-10-08T00:06:57.357197+00:00", "temperature": 26.97506115437136, "humidity": 57.84707564655465, "pressure": 997.7270485520521}
{"timestamp": "2024-10-08T00:07:07.366935+00:00", "temperature": 26.980127668590285, "humidity": 57.76546467860513, "pressure": 997.6785398845532}
```

### 9.5 MQTTブローカからSubscribeしてデータベースに追加する

MQTTブローカからデータをSubscribeして、データベースに追加することを考えます。

測定データをPublishする`mqtt_bme280_publish02.py`を実行している間に、このプログラムを実行します。

`mqtt_bme280_insert01.py`

```python
#coding: utf-8

#MQTTでデータ取得する
import mqtt_ambient_sub

#DB関連を取扱う
import db_ambient

#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_iot_899'

#接続先情報
MQTT_HOST = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'raspi/bme'

#コールバック関数
#MQTTブローカより新たなデータが来たらこのメソッドが呼ばれる
def on_mqtt_data_arrive(new_data):
    #DBに渡すための新しいディクショナリ形式にまとめる。
    new_row ={
        'timestamp' : new_data['timestamp'],
        'identifier' : NODE_IDENTIFIER,
        'temperature' : round(new_data['temperature'], 2),
        'humidity' : round(new_data['humidity'], 2),
        'pressure' : round(new_data['pressure'], 2)
    };

    #データベースの操作を行う------
    db_result = db_ambient.insert_row(new_row)
    print('●NEW_DATA: ', new_row)
    print(' クエリを実行しました。('+ str(db_result) +' row affected.)')

def main():
    #DBサーバに接続する
    db_ambient.connect()
    print('db server connected')

    #MQTTブローカに接続する
    mqtt_ambient_sub.connect(MQTT_HOST, MQTT_PORT, MQTT_TOPIC)
    print('mqtt server connected')

    #MQTTブローカからデータが到着したときに
    #呼ばれるコールバック関数をセットする
    mqtt_ambient_sub.add_handler_on_mqtt_data_arrive(on_mqtt_data_arrive)

    #MQTTメッセージを待ち受ける
    print('waiting for mqtt message')
    mqtt_ambient_sub.loop()

main()
```

`mqtt_ambient_sub.py`

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
```

プログラムの出力は次のとおりとなる。

```bash
db server connected
mqtt server connected
waiting for mqtt message
Connected with result code 0
●NEW_DATA:  {'timestamp': datetime.datetime(2024, 10, 9, 15, 30, 59, 927507, tzinfo=<DstTzInfo 'Asia/Tokyo' JST+9:00:00 STD>), 'identifier': 'tochigi_iot_899', 'temperature': 25.87, 'humidity': 45.86, 'pressure': 996.93}
 クエリを実行しました。(1 row affected.)
●NEW_DATA:  {'timestamp': datetime.datetime(2024, 10, 9, 15, 31, 9, 936963, tzinfo=<DstTzInfo 'Asia/Tokyo' JST+9:00:00 STD>), 'identifier': 'tochigi_iot_899', 'temperature': 25.89, 'humidity': 45.9, 'pressure': 996.87}
 クエリを実行しました。(1 row affected.)
●NEW_DATA:  {'timestamp': datetime.datetime(2024, 10, 9, 15, 31, 19, 946706, tzinfo=<DstTzInfo 'Asia/Tokyo' JST+9:00:00 STD>), 'identifier': 'tochigi_iot_899', 'temperature': 25.89, 'humidity': 45.9, 'pressure': 996.96}
 クエリを実行しました。(1 row affected.)
```

MariaDBにログインし、クエリを発行してデータが追加されたか確認しましょう。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient WHERE identifier = 'tochigi_iot_899' ORDER BY timestamp DESC;
```

```sql
+--------+---------------------+-----------------+-------------+----------+----------+
| row_id | timestamp           | identifier      | temperature | humidity | pressure |
+--------+---------------------+-----------------+-------------+----------+----------+
|  70144 | 2024-10-09 15:33:20 | tochigi_iot_899 |       25.86 |    46.01 |   996.88 |
|  70143 | 2024-10-09 15:33:10 | tochigi_iot_899 |       25.84 |    46.02 |   996.88 |
|  70142 | 2024-10-09 15:33:00 | tochigi_iot_899 |       25.82 |    45.98 |   996.83 |
|  70141 | 2024-10-09 15:32:50 | tochigi_iot_899 |       25.83 |    45.96 |   996.81 |
|  70140 | 2024-10-09 15:32:39 | tochigi_iot_899 |       25.83 |    45.97 |   996.84 |
|  70139 | 2024-10-09 15:32:29 | tochigi_iot_899 |       25.85 |    45.99 |   996.87 |
|  70138 | 2024-10-09 15:32:19 | tochigi_iot_899 |       25.83 |       46 |   996.87 |
|  70137 | 2024-10-09 15:32:09 | tochigi_iot_899 |       25.86 |    45.97 |   996.81 |
|  70136 | 2024-10-09 15:31:59 | tochigi_iot_899 |       25.86 |    45.92 |   996.83 |
|  70135 | 2024-10-09 15:31:49 | tochigi_iot_899 |       25.88 |    45.91 |    996.8 |
|  70134 | 2024-10-09 15:31:39 | tochigi_iot_899 |       25.86 |    45.97 |   996.88 |
|  70133 | 2024-10-09 15:31:29 | tochigi_iot_899 |       25.86 |    45.93 |   996.85 |
|  70132 | 2024-10-09 15:31:19 | tochigi_iot_899 |       25.89 |     45.9 |   996.96 |
|  70131 | 2024-10-09 15:31:09 | tochigi_iot_899 |       25.89 |     45.9 |   996.87 |
|  70130 | 2024-10-09 15:30:59 | tochigi_iot_899 |       25.87 |    45.86 |   996.93 |
+--------+---------------------+-----------------+-------------+----------+----------+
15 rows in set (0.071 sec)
```
