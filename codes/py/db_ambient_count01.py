#coding: utf-8

#モジュールをインポート
import pymysql.cursors #PythonからDBを取扱う

#DBへの接続情報
DB_USER = 'iot_user'
DB_PASS = 'password'
DB_HOST = 'localhost'
DB_NAME = 'iot_storage'

#共通で使うオブジェクトを指すための準備
sql_connection = None

def connect():
    global sql_connection

    #DBサーバに接続する
    sql_connection = pymysql.connect(
        user = DB_USER,  #データベースにログインするユーザ名
        passwd = DB_PASS,#データベースユーザのパスワード
        host = DB_HOST,  #接続先DBのホストorIPアドレス
        db = DB_NAME
    )

#データを追加する
def insert_row(row):
    #クエリの作成
    query = "INSERT INTO Ambient(timestamp, identifier, temperature, humidity, pressure)" \
            "VALUES(%(timestamp)s, %(identifier)s, %(temperature)s, %(humidity)s, %(pressure)s);"

    #cursorオブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #クエリを実行する
    result = sql_cursor.execute(query, row)

    #変更を実際に反映させる
    sql_connection.commit()

    return(result)

#１時間毎に平均値を集計する
def select_ave_one_hour(node_id, start_timestamp, limit_count):
    #cursorオブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #クエリに渡すパラメータを辞書にまとめる
    param = {
        'target_id' : node_id,
        'target_timestamp' : start_timestamp,
        'target_limit_count' : limit_count
    };

    #クエリのコマンド
    query = 'SELECT timestamp, identifier, AVG(temperature), AVG(humidity) , AVG(pressure) '\
            'FROM Ambient WHERE identifier=%(target_id)s '\
            'AND timestamp >= %(target_timestamp)s '\
            'GROUP BY CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp)) '\
            'ORDER BY timestamp ASC '\
            'LIMIT %(target_limit_count)s;'

    #クエリを実行する
    sql_cursor.execute(query, param)

    #クエリを実行した結果得られたデータを辞書にまとめ
    #配列に追加する
    array = []
    for row in sql_cursor.fetchall():
        dict = {
            'timestamp' : row[0],
            'identifier' : row[1],
            'temperature' : row[2],
            'humidity' : row[3],
            'pressure' : row[4]
        }
        array.append(dict)

    #データを格納した辞書の配列を返す
    return(array)