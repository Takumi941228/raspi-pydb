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