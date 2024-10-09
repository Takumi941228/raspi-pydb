#coding: utf-8

#DB関連をまとめたモジュール
import db_ambient_count02

#グラフ表示関連
import sys
import matplotlib.pyplot as plt
import math
import numpy as np

def main():
    #グラフのデータ(空のデータを準備)
    x = np.array([])
    y = np.array([])

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

    #グラフの設定
    fig, ax = plt.subplots()

    #グラフのタイトルを指定
    plt.title(f'Temperature Trend(Node: {node_id}, Every {update_cycle} sec. cycle)')
    plt.xlabel('TimeStamp')             #Y軸のタイトルを指定
    plt.ylabel('Temperature [deg. C.]') #X軸のタイトルを指定

    #ラベルの設定
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=90) #x軸のラベルを90度回転させる

    while True:
        #DBサーバに接続する
        db_ambient_count02.connect()

        #グラフに与えるデータを初期化
        x = np.array([])
        y = np.array([])

        #グラフ内のデータを初期化
        plt.clf()

        #クエリを実施して結果を得る
        result = db_ambient_count02.select_newest(node_id, limit_count)

        #クエリの結果得られたデータを表示する
        print( 'timestamp       \t', 'identifier        \t', 'temperature   \t', 'humidity  \t ','pressure')

        for data in result:
            print( data['timestamp'], ', \t', data['identifier'], ', \t', data['temperature'], ', \t', data['humidity'], ', \t', data['pressure'])
            #得られたデータをプロットとして追加する
            x = np.append(x, data['timestamp'])
            y = np.append(y, data['temperature'])
 
        plt.plot(x,y) #グラフを描画する

        #次の更新周期まで待つ
        plt.pause(update_cycle)

main()