#coding: utf-8
import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

#insert03.py:S
#テーブルにデータを挿入する
#(データをディクショナリ形式で指定）

def main():
    #DB サーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user', #データベースにログインするユーザ名
        passwd='Passw0rd',#データベースユーザのパスワード
        host='localhost', #接続先DBのホストorIPアドレス
        db='practice'
    )

    #cursor オブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #テーブルにデータを挿入する print('●クエリの実行(データの挿入)')

    #クエリを指定する。実データは後から指定する。
    #実データはディクショナリ形式とするため、ブレースホルダにキー名を指定する
    query1 = "INSERT INTO BankAccount(account_id, first_name,last_name, balance, atm_count) " \
            " VALUES( " \
            " %(account_id)s, " \
            " %(first_name)s, " \
            " %(last_name)s, " \
            " %(balance)s, " \
            " %(atm_count)s );"

    print('実行するクエリ: ' + query1)

    #挿入するデータをディクショナリ変数に格納
    new_row = {
        'account_id' : '998877',
        'first_name' : 'Bill' ,
        'last_name' : 'Gates',
        'balance' : 88888888.34,
        'atm_count' : 54
    }

    print('ディクショナリ内のデータ: ')
    print(new_row)

    #ディクショナリ変数に格納されたデータを指定して挿入を実行する
    result1 = sql_cursor.execute(query1, new_row)

    #クエリを実行。変更したrowの数が戻り値となる
    print('クエリを実行しました。('+ str(result1) +' row affected.)')

    #変更を実際に反映させる
    sql_connection.commit()

    #挿入したデータを含めてすべてのデータを表示
    print('●クエリの実行(データの選択)')
    query2 = 'SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;' #クエリのコマンド

    print('実行するクエリ: ' + query2)
    result2 = sql_cursor.execute(query2) #クエリを実行。取得したrowが戻り値となる

    print('クエリを実行しました。('+ str(result2) +' row affected.)')


    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count') #クエリを実行した結果得られたデータを1行ずつ表示する
    for row in sql_cursor.fetchall():
        print( row[0], ',\t', row[1], ',\t', row[2], ',\t', row[3], ',\t', row[4])
main()