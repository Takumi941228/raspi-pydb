#coding: utf-8

import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

def main():
    #DBサーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user',  #データベースにログインするユーザ名
        passwd='password',#データベースユーザのパスワード
        host='localhost', #接続先DBのホストorIPアドレス
        db='practice'
    )
    #cursor オブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    query = 'SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount WHERE atm_count >= 5;' #クエリのコマンド
    sql_cursor.execute(query) #クエリを実行
    print(query, ' のクエリの結果\n')
    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count')

    #クエリを実行した結果得られたデータを1行ずつ表示する
    for row in sql_cursor.fetchall():
        print( row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])
main()