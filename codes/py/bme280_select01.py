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
        user = DB_USER,   #データベースにログインするユーザ名
        passwd = DB_PASS, #データベースユーザのパスワード
        host = DB_HOST,   #接続先DBのホストorIPアドレス
        db = DB_NAME
    )
    #cursorオブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #クエリのパラメータを定義
    datetime_start = '2024-09-19 10:00:00'
    limit_count = 5

    #クエリのコマンド
    query = 'SELECT timestamp, identifier, temperature, humidity, pressure '\
            'FROM Ambient WHERE timestamp > %s LIMIT %s;'

    sql_cursor.execute(query, (datetime_start, limit_count))

    print('●実行するクエリ: ', query)
    print( 'timestamp       \t', 'identifier        \t', 'temperature   \t', 'humidity  \t', 'pressure')

    #クエリを実行した結果得られたデータを１行ずつ表示する
    for row in sql_cursor.fetchall():
        print(row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])

main()