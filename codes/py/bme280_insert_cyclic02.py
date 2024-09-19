#coding: utf-8

#モジュールをインポート
import bme280mod  #BME280センサ関連を取扱う
import db_ambient #DB関連を取扱う
import time       #時間を取扱う
import datetime   #日付と時刻を取扱う

#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_iot_999';

#何秒ごとに測定するか
CYCLE_SEC = 10

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init() #BME280センサを初期化

    #DBサーバに接続する
    db_ambient.connect()

    while True:
        bme280mod.read_data() #測定
        data = bme280mod.get_data() #データを取得

        #DBに渡すための新しいディクショナリ形式にまとめる。
        new_row ={
            "timestamp" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "identifier" : NODE_IDENTIFIER,
            "temperature" : round(data['temperature'], 2),
            "humidity" : round(data['humidity'], 2),
            "pressure" : round(data['pressure'], 2)
        };

        #データベースの操作を行う------
        db_result = db_ambient.insert_row(new_row)
        print('追加するデータ: ', new_row)
        #クエリを実行した。変更した row の数が戻り値となる
        print('クエリを実行しました。('+ str(db_result) +' row affected.)')

        time.sleep(CYCLE_SEC)

main()