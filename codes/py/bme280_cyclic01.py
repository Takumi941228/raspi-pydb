#coding: utf-8

#モジュールをインポート
import bme280mod #BME280センサ関連を取扱う
import time      #時間を取扱う
import datetime  #日付と時刻を取扱う

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init() #BME280センサを初期化

    print('測定時間[YYYY-MM-DD HH:MM:SS], 温度[℃], 湿度[%], 気圧[hPa]')

    while True:
        bme280mod.read_data() #測定
        data = bme280mod.get_data() #データを取得

        temp = data['temperature']
        hum = data['humidity']
        press = data['pressure']

        datetime_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f'{datetime_now},    {temp:.2f},    {hum:.2f},    {press:.2f}')

        time.sleep(10)
main()