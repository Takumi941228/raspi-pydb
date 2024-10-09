#coding: utf-8

#DB関連をまとめたモジュール
import db_ambient_count02

#グラフ表示関連
import matplotlib.pyplot as plt
import numpy as np

def main():
    #グラフのデータ
    x = np.array([])
    y = np.array([])

    #DBサーバに接続する
    db_ambient_count02.connect()

    #クエリのパラメータを入力
    #表示を開始する日付・時刻を入力する
    print('最新のデータを表示します。')
    print('どのノードのデータを表示しますか？')
    node_id = input('ノードの Identifier(例:tochigi_mqtt_999): ')

    print('何サンプル前のデータまで表示しますか？')
    #入力したデータを数値に変換
    limit_count = int(input('数値を入力(例: 100) : '))

    #クエリを実施して結果を得る
    result = db_ambient_count02.select_newest(node_id, limit_count)
 
    #クエリの結果得られたデータを表示する
    print( 'timestamp       \t', 'identifier        \t', 'temperature   \t', 'humidity  \t ', 'pressure')
    for data in result:
        print( data['timestamp'], ', \t', data['identifier'], ', \t', data['temperature'], ', \t', data['humidity'], ', \t', data['pressure'])
        x = np.append(x, data['timestamp'])
        y = np.append(y, data['temperature'])
    
    #グラフの設定をおこなう
    fig, ax = plt.subplots()

    plt.title('Temperature Trend')      #グラフのタイトルを指定
    plt.xlabel('TimeStamp')             #Y軸のタイトルを指定
    plt.ylabel('Temperature [deg. C.]') #X軸のタイトルを指定

    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=90) #x軸のラベルを90度回転させる

    plt.plot(x,y)    #グラフを描画する

    #グラフを表示する
    plt.show()
main()