#coding: utf-8

#モジュールをインポート
import bme280mod

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init() #BME280センサを初期化
    bme280mod.read_data() #測定

    data = bme280mod.get_data() #データを取得
    temp = data['temperature']
    hum = data['humidity'] 
    press = data['pressure']

    print(f'温度: {temp:.2f} ℃, 湿度: {hum:.2f} %, 気圧: {press:.2f} hPa')

main()