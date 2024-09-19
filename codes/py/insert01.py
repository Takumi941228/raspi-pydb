#coding: utf-8
import pymysql.cursors #Python から DB を利用するためのモジュールを利用

#insert01.py
#テーブルにデータを挿入する

def main():
    #DB サーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user', #データベースにログインするユーザ名
        passwd='Passw0rd', #データベースユーザのパスワード
        host='localhost', #接続先DBのホストorIPアドレス
        db='practice'
    )
    #cursor オブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #テーブルにデータを挿入する 
    print('●クエリの実行(データの挿入)')
    query1 = "INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) " \
            " VALUES('1234567', 'Jhon', 'von Neumann', 9999.98, 55)";

    print('実行するクエリ: ' + query1)

    result1 = sql_cursor.execute(query1) #クエリを実行。変更したrowの数が戻り値となる
    print('クエリを実行しました。('+ str(result1) +' row affected.)')

    #変更を実際に反映させる
    sql_connection.commit()

    #挿入したデータを含めてすべてのデータを表示
    print('●クエリの実行(データの選択)')
    query2 = 'SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;' #クエリのコマンド

    print('実行するクエリ: ' + query2)
    result2 = sql_cursor.execute(query2) #クエリを実行。取得したrowが戻り値となる

    print('クエリを実行しました。('+ str(result2) +' row affected.)')

    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count')
    #クエリを実行した結果得られたデータを1行ずつ表示する
    for row in sql_cursor.fetchall():
        print( row[0], ',\t', row[1], ',\t', row[2], ',\t', row[3], ',\t', row[4])
main()