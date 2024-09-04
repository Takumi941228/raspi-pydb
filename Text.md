
# Raspberry Piを活用したデータ処理とグラフの表示

## 1. 実習の目標

### 1.1 Pythonとデータベースの連携

この実習では、プログラミング言語の一種であるPython言語の習得とともに、SQL言語によるデータベースの基礎的な使い方を習得し、Pythonとデータベースの連携させたより実践的なレベルを習得することを目的とする。

### 1.2 実習の成果物

この実習の最後では、次のようなグラフを生成するプログラムを作成します。このグラフは、温度・湿度・気圧の変化を表したグラフになります。


BME280センサ等のセンサからデータを取得して、それらのデータをMQTT経由で取得し、データベースに蓄積します。蓄積されたデータを一定時間毎に表示し、リアルタイムで温度・湿度・気圧の変化がわかるシステムを構築します。

## 2. 開発環境のインストールと設定

### 2.1 Pythonの開発環境

まず、aptパッケージのアップデートをします。

```cmd
pi@raspberrypi:~ $ sudo apt update
```


本実習では、開発環境として`idle`を利用します。
下記のコマンドで、インストールを行ってください。すでにインストールされている場合は、実行する必要はありません。

```cmd
pi@raspberrypi:~ $ sudo apt -y install idle-python3.11
```

```cmd
pi@raspberrypi:~ $ sudo apt -y install python3-pymysql
```

### 2.2 MariaDB(MySQL)Serverの環境構築

下記のコマンドで`MariaDB Server`をインストールします。

```cmd
pi@raspberrypi:~ $ sudo apt -y install mariadb-server
```

## 3. 練習用データベースの作成

練習用データベースを作成します。
以前の実習ですでに作成済である場合は、この章は飛ばしても問題ありません。

### 3.1. テーブルとデータベースの作成

#### データベースの作成

MariaDB側で、テーブルとデータベースを作成します。
MariaDBにroot ユーザでログインして、データベースを作成します。

```cmd
pi@raspberrypi:~ $ sudo mariadb -u root -p
```

```db
MariaDB[(none)]> CREATE DATABASE practice CHARACTER SET utf8mb4;
```

#### ユーザの作成

```db
MariaDB [(none)]> CREATE user 'ユーザ名'@'localhost identified by '任意のパスワード';
```

#### ユーザの確認

```db
MariaDB [(none)]> SELECT host, user from mysql.user;
```



#### 権限の付与

ユーザ"iot_user"と"iot_admin"に、データベース"practice"に関する操作の権限を付与します。

"iot_user"は一般ユーザとして取り扱い、"iot_admin"は管理者ユーザとして取り扱います。

次のコマンドは、"iot_user"に関する権限を付与します。付与する権限は、データベース"practice" に対する、一般的な SQL コマンドの使用です。

```db
MariaDB [(none)]> GRANT select, update, insert, delete ON practice.* TO 'iot_user'@'localhost';
```

次のコマンドは、"iot_admin" に関する権限を付与します。付与する権限は、データベース
"practice"に対する、すべての SQL コマンドの使用です。

```db
MariaDB [(none)]> GRANT ALL PRIVILEGES ON practice.* TO 'iot_admin'@'localhost';
```

#### 権限の確認

```db
MariaDB [practice]> SHOW grants for iot_user@localhost;
```

#### データベースの確認

```db
MariaDB [none]> SHOW databases;
```

#### データベースの選択

```db
MariaDB [none]> use practice
```

#### テーブルの作成

テーブルを作成します。

| カラム名(列名) | データの意味 | データの型 | 型の設定理由 | 主キー |
| --- | --- | --- | --- | --- |
|account_id | 口座番号 | CAHR(10) | 最大10桁まで対応文字列として処理 | ◯ |
| first_name | 名前 | VARCHAR(100) | 長い名前 の人に対応し100byteまで対応 | - |
| last_name | 名字 | VARCHAR(100) | 長い名前 の人に対応し100byteまで対応 |  - | 
| balance | 残高 | DECIMAL(16,3) | 大富豪に対応し16桁まで。小数点以下は 3 位まで記録 | - |
| atm_count | ATM利用回数 | INT | 小数点を使用しない | - |

```db
MariaDB [practice]> CREATE TABLE
                    -> BankAccount( account_id CHAR(10)
                    -> PRIMARY KEY, first_name
                    -> VARCHAR(100), last_name
                    -> VARCHAR(100), balance
                    -> DECIMAL(16, 3), atm_count
                    -> INT );
```

※SQLでは、Enterで改行して、コマンドを複数行にわたって記述することができます。

#### テーブルの確認

```db
MariaDB [practice]> show tables;
```

#### テーブルの中身の確認

```db
MariaDB [practice]> show fields from BankAccount;
```

### 3.2 データの追加

追加するデータは次のとおりです。

| account_id | first_name | last_name | balance | atm_count |
| --- | --- | --- | --- | --- |
| 3141592 | Thomas | Edison | -279.67 | 10 |
| 653589793 | Nicola | Tesla | 50288.45 | 2 |
| 8462626 | Watt | James | 41971.23 | 3 |
| 43383 | Bell | Graham | 693.01 | 1 |

次のコマンドに倣って、データを追加しましょう。
文字列データは ' ' (シングルクオート) で囲みます。数値データはそのまま入力します

```db
INSERT INTO
BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES('3141592', 'Thomas', 'Edison', -279.67, 10);
```

```db
INSERT INTO
BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES('653589793', 'Nicola', 'Tesla', 50288.45 , 2);
```

```db
INSERT INTO
BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES('8462626', 'Watt', 'James', 41971.23 , 3);
```

```db
INSERT INTO
BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES('43383', 'Bell', 'Graham', 693.01 , 1);
```

```db
INSERT INTO
BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES('84197169', 'Carlos', 'Ghosn',314159265358.97,6);
```

```db
INSERT INTO
BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES('2795028', 'Koichi', 'Hasegawa', 24362.06,5);
```

### 3.1　データの確認

```db
MariaDB [practice]> SELECT * FROM BankAccount;
```

## 4. MariaDBとPythonの連携

Python から MariaDB を操作するプログラムを作成します。
下記のように、プログラムを収納するディレクトリを作成します。

```cmd
pi@raspberrypi:~ $ cd ~
```

```cmd
pi@raspberrypi:~ $ mkdir python_sql
```

```cmd
pi@raspberrypi:~ $ cd python_sql
```

MariaDB で管理されているデータベースを Python から操作するには、"PyMySQL"ライブラリを利用する必要があります。
下記のコマンドを使って、PyMySQL がすでにインストールされているか確認しましょう。


```cmd
pi@raspberrypi:~ $ pip list | grep PyMySQL
```

```cmd
PyMySQL                            1.0.2
types-PyMySQL                      1.0
```

上記のように PyMySQL が表示されればインストールされています。
表示されていなければ、「1.1.Python の開発環境」の手順で PyMySQL をインストールしてください。


PyMySQL モジュールについては、下記の URL より情報を収集することができます。

[PyMySQL documentation](https://pymysql.readthedocs.io/en/latest/index.html "Qiita Home")

### 4.1 クエリの実行

Python から MariaDB のクエリを実行します。
練習用 DB から SELECT クエリを実行し、結果を出力します。

次のソースコードを作成し、実行してください。

```python
#coding: utf-8

import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

#select01.py:
#テーブルのデータを表示する

def main():
#DB サーバに接続する
sql_connection = pymysql.connect(
    user='iot_user', #データベースにログインするユーザ名
    passwd='password',#データベースユーザのパスワード
    host='localhost', #接続先DBのホストorIPアドレス
    db='practice'
)
#cursorオブジェクトのインスタンスを生成
sql_cursor = sql_connection.cursor()

query = 'SELECT * FROM BankAccount;' #クエリのコマンド
sql_cursor.execute(query) #クエリを実行
print(query, ' のクエリの結果\n')
print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count')

#クエリを実行した結果得られたデータを 1 行ずつ表示する
for row in sql_cursor.fetchall():
    print( row[0], ',\t', row[1], ',\t', row[2], ',\t', row[3], ',\t', row[4])
main()
```

結果は次のようになります。

Python から SQL サーバに接続し、クエリを実行してデータベース内のデータを取得することができました。


### 4.2 データベースの内容を変更しないクエリの実行

データベースのデータを参照するだけで内容を変更しないクエリは、概ね下記のようなコードで実行できます。変更する箇所は、下記コードの四角で囲った部分です。
なお、「データを参照するだけで内容を変更しない操作」を「副作用のない操作」ということもあります。

```python
#coding: utf-8
import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

#select02.py:
#テーブルのデータを表示する

def main():
#DB サーバに接続する
sql_connection = pymysql.connect(
    user='iot_user', #データベースにログインするユーザ名
    passwd='password',#データベースユーザのパスワード
    host='localhost', #接続先DBのホストorIPアドレス
    db='practice'
)
#cursor オブジェクトのインスタンスを生成
sql_cursor = sql_connection.cursor()

query = 'SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount WHERE atm_count
>= 5;' #クエリのコマンド
sql_cursor.execute(query) #クエリを実行
print(query, ' のクエリの結果\n')
print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count')

#クエリを実行した結果得られたデータを 1 行ずつ表示する
for row in sql_cursor.fetchall():
    print( row[0], ',\t', row[1], ',\t', row[2], ',\t', row[3], ',\t', row[4])
main()
```

結果は次のようになります。


なお、クエリを指定するにあたって、下記のような

```db
SELECT * FROM ...
```

カラム名を * で指定するような書き方は避けるべきです。

下記のように

```db
SELECT account_id, first_name, last_name, balance, atm_count FROM ...
```

カラム名を指定すると良いでしょう。

### 4.3 データベースの内容を変更するクエリの実行

#### 4.3.1 クエリを直接指定する方法

1 行のデータを挿入することを考えます。クエリ文字列は下記のようになります。

```db
INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)
VALUES('1234567', 'Jhon', 'von Neumann', 9999.98, 55)
```

次のプログラムは、1 行のデータを上記のクエリを使って挿入した後、すべての行を選択し表示します。クエリ文字列を設定して実行するまでの手順は、ほぼ同一であることを確認してください。

挿入したデータを実際に反映させるには、commit()メソッドを実行する必要があります。

```python
sql_connection.commit()
```

```python
#coding: utf-8
import pymysql.cursors #Python から DB を利用するためのモジュールを利用

#insert01.py:
#テーブルにデータを挿入する

def main():
#DB サーバに接続する
sql_connection = pymysql.connect(
    user='iot_user', #データベースにログインするユーザ名
    passwd='password', #データベースユーザのパスワード
    host='localhost', #接続先DBのホストorIPアドレス
    db='practice'
)
#cursor オブジェクトのインスタンスを生成
sql_cursor = sql_connection.cursor()

#テーブルにデータを挿入する 
print('●クエリの実行(データの挿入)')
query1 = "INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) " \ " VALUES('1234567', 'Jhon', 'von Neumann', 9999.98, 55)";

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
```

結果は下記のとおりです。

※行を削除するコマンド
デバッグのためにプログラムを再実行すると、同じデータを重複して挿入することになります。
MariaDBにログインして、下記のように新しく追加するデータを予め削除しておきましょう。

```db
MariaDB [practice]> DELETE FROM BankAccount WHERE account_id = '1234567';
```
