#coding: utf-8

#DB関連をまとめたモジュール
import db_ambient_count02

#グラフ表示関連
import matplotlib.pyplot as plt
import numpy as np

def main():
    #クエリのパラメータを入力
    #表示を開始する日付・時刻を入力する
    print('最新のデータをリアルタイムに表示します。')
    print('どのノードのデータを表示しますか？')
    node_id = input('ノードの Identifier(例: tochigi_iot_999): ')

    print('何サンプル前のデータまで表示しますか？')
    #入力したデータを数値に変換
    limit_count = int(input('数値を入力(例: 20) : '))

    print('グラフの更新周期(秒)は？')
    #入力したデータを数値に変換
    update_cycle = int(input('数値を入力(例: 10) : '))

    #グラフの設定をおこなう
    plt.rcParams["figure.figsize"] = (15,5) #グラフの大きさを指定する
    plt.tight_layout()                      #文字が重ならないようなレイアウトにする

    #無限ループにてグラフを連続して描画
    while True:
        #DBサーバに接続する
        db_ambient_count02.connect()

        #グラフに与えるデータを初期化
        x = np.array([])
        y={
            'temperature' : np.array([]),
            'humidity' : np.array([]),
            'pressure' : np.array([])
        }
    
        #グラフ内のデータを初期化
        plt.clf()

        #クエリを実施して結果を得る
        result = db_ambient_count02.select_newest(node_id, limit_count)

        #クエリの結果得られたデータを表示する
        print( 'timestamp       \t', 'identifier        \t', 'temperature   \t', 'humidity  \t ','pressure')
        for data in result:
            print( data['timestamp'], ', \t', data['identifier'], ', \t', data['temperature'], ', \t', data['humidity'], ', \t', data['pressure'])
            x = np.append(x, data['timestamp'])
            y['temperature'] = np.append(y['temperature'], data['temperature'])
            y['humidity'] = np.append(y['humidity'], data['humidity'])
            y['pressure'] = np.append(y['pressure'], data['pressure'])

        #１つめのグラフを用意する
        plt.subplot(1,3,1)                   #縦１-横３のエリアを設定し、その１つめのグラフ
        plt.title('Temperature Trend')       #グラフのタイトルを指定
        plt.xlabel('TimeStamp')              #Y軸のタイトルを指定
        plt.ylabel('Temperature [deg. C.]')  #X軸のタイトルを指定
        plt.xticks(rotation=45)              #X軸のラベルを 45°回転させる
    
        #上下左右の余白の設定
        plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.95)
        plt.plot(x, y['temperature'])       #プロットデータを設定する

        #２つめのグラフを用意する
        plt.subplot(1,3,2)                  #縦１-横 ３のエリアを設定し、その２つめのグラフ
        plt.title('Humidity Trend')         #グラフのタイトルを指定
        plt.xlabel('TimeStamp')             #Y軸のタイトルを指定
        plt.ylabel('Humidity [%]')          #X軸のタイトルを指定
        plt.xticks(rotation=45)             #X軸のラベルを 45°回転させる
        
        #上下左右の余白の設定
        plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.95)
        plt.plot(x, y['humidity'])          #プロットデータを設定する

        #３つめのグラフを用意する
        plt.subplot(1,3,3)                 #縦１-横 ３のエリアを設定し、その３つめのグラフ
        plt.ylim(995, 1035)                #Y軸の値の範囲を設定
        plt.title('Pressure Trend')        #グラフのタイトルを指定
        plt.xlabel('TimeStamp')            #Y軸のタイトルを指定
        plt.ylabel('Pressure [hPa]')       #X軸のタイトルを指定
        plt.xticks(rotation=45)            #X軸のラベルを 45°回転させる
        
        #上下左右の余白の設定
        plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.95)
        plt.plot(x, y['pressure'])         #プロットデータを設定する

        #次の更新周期まで待つ
        plt.pause(update_cycle)

main()