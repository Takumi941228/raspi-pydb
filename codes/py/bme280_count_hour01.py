#coding: utf-8

import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

#DBへの接続情報
DB_USER = 'iot_user'
DB_PASS = 'password'
DB_HOST = 'localhost'
DB_NAME = 'iot_storage'

def main():
    #DBサーバに接続する
    sql_connection = pymysql.connect(
        user = DB_USER,  #データベースにログインするユーザ名
        passwd = DB_PASS,#データベースユーザのパスワード
        host = DB_HOST,  #接続先DBのホストorIPアドレス
        db = DB_NAME
    )
    #cursorオブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #クエリのパラメータを入力
    #表示を開始する日付・時刻を入力する
    print('１時間ごとに平均したデータを表示します。')
    print('どのノードのデータを表示しますか？')
    node_id = input('ノードの Identifier(例: tochigi_mqtt_999): ')

    print('いつのデータから表示しますか？')
    s_year = input('年(例: 2024): ')
    s_month = input('月(例: 09): ')
    s_day = input('日(例: 19): ')
    s_hour = input('時(例: 00): ')

    datetime_start = f'{s_year}-{s_month}-{s_day} {s_hour}:00:00'

    print(f'{datetime_start}のデータからから何行のデータを表示しますか？')
    #入力したデータを数値に変換
    limit_count = int(input('数値を入力(例: 5) : '))


    #クエリのコマンド
    query = 'SELECT timestamp, identifier, AVG(temperature), AVG(humidity) , AVG(pressure) '\
            'FROM Ambient WHERE identifier=%(target_id)s '\
            'AND timestamp >= %(target_timestamp)s '\
            'GROUP BY CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp)) '\
            'ORDER BY timestamp ASC '\
            'LIMIT %(target_limit_count)s;'

    #クエリに渡すデータ
    param = {'target_id': node_id, 'target_timestamp': datetime_start, 'target_limit_count': limit_count};

    print('●実行するクエリ: ', query, 'Data: ', param)
    sql_cursor.execute(query, param)

    print( 'timestamp       \t', 'identifier        \t',  'temperature  \t', 'humidity  \t', 'pressure')

    #クエリを実行した結果得られたデータを１行ずつ表示する
    print('●取得したデータを表示します')

    for row in sql_cursor.fetchall():
        print( row[0], ', \t', row[1], ', \t', round(row[2], 2), ', \t', round(row[3], 2), ', \t', round(row[4], 2))

main()