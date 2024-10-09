#coding: utf-8

#MQTTでデータ取得する
import mqtt_ambient

#DB関連を取扱う
import db_ambient

#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_mqtt_999';

#コールバック関数
#MQTTブローカより新たなデータが来たらこのメソッドが呼ばれる
def on_mqtt_data_arrive(new_data):
  #DBに渡すための新しいディクショナリ形式にまとめる。
  new_row ={
    'timestamp' : new_data['timestamp'],
    'identifier' : NODE_IDENTIFIER,
    'temperature' : new_data['temperature'],
    'humidity' : new_data['humidity'],
    'pressure' : new_data['pressure']
  };

  #データベースの操作を行う------
  db_result = db_ambient.insert_row(new_row)
  print('●NEW_DATA: ', new_row)
  print(' クエリを実行しました。('+ str(db_result) +' row affected.)')

def main():
  #DB サーバに接続する
  db_ambient.connect()
  print('db server connected')

  #MQTTブローカに接続する
  mqtt_ambient.connect()
  print('mqtt server connected')

  #MQTTブローカからデータが到着したときに呼ばれるコールバック関数をセットする
  mqtt_ambient.add_handler_on_mqtt_data_arrive(on_mqtt_data_arrive)

  #MQTTメッセージを待ち受ける
  print('waiting for mqtt message')
  mqtt_ambient.loop()

main()