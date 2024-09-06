
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

```bash
pi@raspberrypi:~ $ sudo apt update
```


本実習では、開発環境として`idle`を利用します。
下記のコマンドで、インストールを行ってください。すでにインストールされている場合は、実行する必要はありません。

```bash
pi@raspberrypi:~ $ sudo apt -y install idle-python3.11
```

```bash
pi@raspberrypi:~ $ sudo apt -y install python3-pymysql
```

### 2.2 MariaDB(MySQL)Serverの環境構築

下記のコマンドで`MariaDB Server`をインストールします。

```bash
pi@raspberrypi:~ $ sudo apt -y install mariadb-server
```

## 3. 練習用データベースの作成

練習用データベースを作成します。
以前の実習ですでに作成済である場合は、この章は飛ばしても問題ありません。

### 3.1. テーブルとデータベースの作成

#### データベースの作成

MariaDB側で、テーブルとデータベースを作成します。
MariaDBにroot ユーザでログインして、データベースを作成します。

```bash
pi@raspberrypi:~ $ sudo mariadb -u root
```

```sql
MariaDB[(none)]> CREATE DATABASE practice CHARACTER SET utf8mb4;
```

#### ユーザの作成

ユーザ名`iot_user`と`iot_admin`を作成する。

```sql
MariaDB [(none)]> CREATE user 'ユーザ名'@'localhost' identified by '任意のパスワード';
```

#### ユーザの確認

```sql
MariaDB [(none)]> SELECT host, user from mysql.user;
```

以下のようになる。

```bash
+-----------+-------------+
| Host      | User        |
+-----------+-------------+
| localhost | iot_admin   |
| localhost | iot_user    |
| localhost | mariadb.sys |
| localhost | mysql       |
| localhost | root        |
+-----------+-------------+
5 rows in set (0.002 sec)
```

#### 権限の付与

ユーザ"iot_user"と"iot_admin"に、データベース"practice"に関する操作の権限を付与します。

"iot_user"は一般ユーザとして取り扱い、"iot_admin"は管理者ユーザとして取り扱います。

次のコマンドは、"iot_user"に関する権限を付与します。付与する権限は、データベース"practice" に対する、一般的な SQL コマンドの使用です。

```sql
MariaDB [(none)]> GRANT select, update, insert, delete ON practice.* TO 'iot_user'@'localhost';
```

次のコマンドは、"iot_admin" に関する権限を付与します。付与する権限は、データベース
"practice"に対する、すべての SQL コマンドの使用です。

```sql
MariaDB [(none)]> GRANT ALL PRIVILEGES ON practice.* TO 'iot_admin'@'localhost';
```

#### 権限の確認

```sql
MariaDB [practice]> SHOW grants for iot_user@localhost;
```

```bash
+-----------------------------------------------------------------------------------------------------------------+
| Grants for iot_user@localhost                                                                                   |
+-----------------------------------------------------------------------------------------------------------------+
| GRANT USAGE ON *.* TO `iot_user`@`localhost` IDENTIFIED BY PASSWORD '*DDFB542AA0BD1D251995D81AEBEB96DEEAD1132F' |
| GRANT SELECT, INSERT, UPDATE, DELETE ON `practice`.* TO `iot_user`@`localhost`                                  |
+-----------------------------------------------------------------------------------------------------------------+
2 rows in set (0.000 sec)
```

#### データベースの確認

```sql
MariaDB [none]> SHOW databases;
```

```bash
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| practice           |
| sys                |
+--------------------+
5 rows in set (0.001 sec)
```

#### データベースの選択

```sql
MariaDB [none]> use practice;
```

```bash
Database changed
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

```sql
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

```sql
MariaDB [practice]> show tables;
```

```bash
+--------------------+
| Tables_in_practice |
+--------------------+
| BankAccount        |
+--------------------+
1 row in set (0.001 sec)
```

#### テーブルの中身の確認

```sql
MariaDB [practice]> show fields from BankAccount;
```

```bash
+------------+---------------+------+-----+---------+-------+
| Field      | Type          | Null | Key | Default | Extra |
+------------+---------------+------+-----+---------+-------+
| account_id | char(10)      | NO   | PRI | NULL    |       |
| first_name | varchar(100)  | YES  |     | NULL    |       |
| last_name  | varchar(100)  | YES  |     | NULL    |       |
| balance    | decimal(16,3) | YES  |     | NULL    |       |
| atm_count  | int(11)       | YES  |     | NULL    |       |
+------------+---------------+------+-----+---------+-------+
5 rows in set (0.002 sec)
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

```sql
MariaDB [practice]> INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count) VALUES('3141592', 'Thomas', 'Edison', -279.67, 10);
```

```sql
MariaDB [practice]> INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count) VALUES('653589793', 'Nicola', 'Tesla', 50288.45, 2);
```

```sql
MariaDB [practice]> INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count) VALUES('8462626', 'Watt', 'James', 41971.23, 3);
```

```sql
MariaDB [practice]> INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count) VALUES('43383', 'Bell', 'Graham', 693.01, 1);
```

```sql
MariaDB [practice]> INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count) VALUES('84197169', 'Carlos', 'Ghosn',314159265358.97, 6);
```

```sql
MariaDB [practice]> INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count) VALUES('2795028', 'Koichi', 'Hasegawa', 24362.06, 5);
```

### 3.1　データの確認

```sql
MariaDB [practice]> SELECT * FROM BankAccount;
```

```bash
+------------+------------+-----------+------------------+-----------+
| account_id | first_name | last_name | balance          | atm_count |
+------------+------------+-----------+------------------+-----------+
| 2795028    | Koichi     | Hasegawa  |        24362.060 |         5 |
| 3141592    | Thomas     | Edison    |         -279.670 |        10 |
| 43383      | Bell       | Graham    |          693.010 |         1 |
| 653589793  | Nicola     | Tesla     |        50288.450 |         2 |
| 84197169   | Carlos     | Ghosn     | 314159265358.970 |         6 |
| 8462626    | Watt       | James     |        41971.230 |         3 |
+------------+------------+-----------+------------------+-----------+
6 rows in set (0.001 sec)
```

exitコマンドでデータベースの操作から抜ける。

```sql
MariaDB [practice]> exit
```

## 4. MariaDBとPythonの連携

Python から MariaDB を操作するプログラムを作成します。
下記のように、プログラムを収納するディレクトリを作成します。

```bash
pi@raspberrypi:~ $ cd ~
```

```bash
pi@raspberrypi:~ $ mkdir python_sql
```

```bash
pi@raspberrypi:~ $ cd python_sql
```

MariaDB で管理されているデータベースを Python から操作するには、"PyMySQL"ライブラリを利用する必要があります。
下記のコマンドを使って、PyMySQL がすでにインストールされているか確認しましょう。

```bash
pi@raspberrypi:~/python_sql $ pip list | grep PyMySQL
```

```bash
PyMySQL                            1.0.2
types-PyMySQL                      1.0
```

上記のように PyMySQL が表示されればインストールされています。

PyMySQL モジュールについては、下記の URL より情報を収集することができます。

[PyMySQL documentation](https://pymysql.readthedocs.io/en/latest/index.html)

### 4.1 クエリの実行

Python から MariaDB のクエリを実行します。
練習用 DB から SELECT クエリを実行し、結果を出力します。

次のソースコードを作成し、実行してください。

```python
#coding: utf-8

import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

#select01.py
#テーブルのデータを表示する

def main():
#DBサーバに接続する
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
    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count' )

    #クエリを実行した結果得られたデータを 1 行ずつ表示する
    for row in sql_cursor.fetchall():
        print( row[0], ',\t', row[1], ',\t', row[2], ',\t', row[3], ',\t', row[4])
main()
```

結果は次のようになります。

```bash
SELECT * FROM BankAccount;  のクエリの結果

account_id       first_name      last_name       balance          atm_count
2795028 ,        Koichi ,        Hasegawa ,      24362.060 ,     5
3141592 ,        Thomas ,        Edison ,        -279.670 ,      10
43383 ,  Bell ,  Graham ,        693.010 ,       1
653589793 ,      Nicola ,        Tesla ,         50288.450 ,     2
84197169 ,       Carlos ,        Ghosn ,         314159265358.970 ,      6
8462626 ,        Watt ,  James ,         41971.230 ,     3
```

PythonからSQLサーバに接続し、クエリを実行してデータベース内のデータを取得することができました。


### 4.2 データベースの内容を変更しないクエリの実行

データベースのデータを参照するだけで内容を変更しないクエリは、概ね下記のようなコードで実行できます。変更する箇所は、下記コードの四角で囲った部分です。
なお、「データを参照するだけで内容を変更しない操作」を「副作用のない操作」ということもあります。

```python
#coding: utf-8
import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

#select02.py
#テーブルのデータを表示する

def main():
    #DBサーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user', #データベースにログインするユーザ名
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
        print( row[0], ',\t', row[1], ',\t', row[2], ',\t', row[3], ',\t', row[4])
main()
```

結果は次のようにな`ります。

```bash
SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount WHERE atm_count >= 5;  のクエリの結果

account_id       first_name      last_name       balance          atm_count
2795028 ,        Koichi ,        Hasegawa ,      24362.060 ,     5
3141592 ,        Thomas ,        Edison ,        -279.670 ,      10
84197169 ,       Carlos ,        Ghosn ,         314159265358.970 ,      6
```

なお、クエリを指定するにあたって、下記のような

<code>SELECT * FROM ...</code>

カラム名を * で指定するような書き方は避けるべきです。

下記のように

<code>SELECT account_id, first_name, last_name, balance, atm_count FROM ...</code>

カラム名を指定すると良いでしょう。

### 4.3 データベースの内容を変更するクエリの実行

#### 4.3.1 クエリを直接指定する方法

1 行のデータを挿入することを考えます。クエリ文字列は下記のようになります。

<code>INSERT INTO BankAccount(account_id, first_name,last_name, balance, atm_count) VALUES('1234567','Jhon', 'von Neumann', 9999.98, 55)</code>

次のプログラムは、1 行のデータを上記のクエリを使って挿入した後、すべての行を選択し表示します。クエリ文字列を設定して実行するまでの手順は、ほぼ同一であることを確認してください。

挿入したデータを実際に反映させるには、commit()メソッドを実行する必要があります。

<code>sql_connection.commit()</code>

```python
#coding: utf-8
import pymysql.cursors #Python から DB を利用するためのモジュールを利用

#insert01.py
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
```

結果は下記のとおりです。

```bash
●クエリの実行(データの挿入)
実行するクエリ: INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)  VALUES('1234567', 'Jhon', 'von Neumann', 9999.98, 55)
クエリを実行しました。(1 row affected.)
●クエリの実行(データの選択)
実行するクエリ: SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;
クエリを実行しました。(7 row affected.)
account_id       first_name      last_name       balance          atm_count
1234567 ,        Jhon ,  von Neumann ,   9999.980 ,      55
2795028 ,        Koichi ,        Hasegawa ,      24362.060 ,     5
3141592 ,        Thomas ,        Edison ,        -279.670 ,      10
43383 ,  Bell ,  Graham ,        693.010 ,       1
653589793 ,      Nicola ,        Tesla ,         50288.450 ,     2
84197169 ,       Carlos ,        Ghosn ,         314159265358.970 ,      6
8462626 ,        Watt ,  James ,         41971.230 ,     3
```

#### ※行を削除するコマンド

デバッグのためにプログラムを再実行すると、同じデータを重複して挿入することになります。
MariaDBにログインして、下記のように新しく追加するデータを予め削除しておきましょう。

```db
MariaDB [practice]> DELETE FROM BankAccount WHERE account_id = '1234567';
```

#### 4.3.2 クエリとデータを分離する方法 その１

1 行のデータを挿入することを考えます。相当するクエリ文字列は下記のようになります。

<code>INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES('223344', 'Stieve', 'Jobs', 9999999.23, 24);</code>

次のプログラムは、上記クエリの"VALUES(…)"の部分を実際のデータではなく、"%s"のようなプレースホルダを指定し、後から実データを割り当てる方法を用いています。

<code>INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES(%s, %s, %s, %s, %s);</code>

プレースホルダで指定した値は、sql_cursor.execute()メソッドの引数に指定します。クエリとデータを分離します。

<code>result1 = sql_cursor.execute(query1, (new_account_id, new_first_name, new_last_name, new_balance, new_atm_count) )</code>

コードは次のようになります。

```python
#coding: utf-8
import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

#insert02.py 
#テーブルにデータを挿入する#(データとクエリを分離）

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

    #クエリを指定する。実データは後から指定する。
    query1 = "INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) " \
                " VALUES(%s, %s, %s, %s, %s)";

    print('実行するクエリ: ' + query1)

    #挿入するデータを変数に格納
    new_account_id = '223344'
    new_first_name = 'Stieve'
    new_last_name = 'Jobs'
    new_balance = 9999999.23
    new_atm_count = 24

    #変数に格納されたデータを指定して挿入を実行する
    result1 = sql_cursor.execute( query1,(new_account_id, new_first_name, new_last_name, new_balance, new_atm_count) )

    #クエリを実行。変更した row の数が戻り値となる
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
```

実行結果は次のようになります。

```bash
●クエリの実行(データの挿入)
実行するクエリ: INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)  VALUES(%s, %s, %s, %s, %s)
クエリを実行しました。(1 row affected.)
●クエリの実行(データの選択)
実行するクエリ: SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;
クエリを実行しました。(8 row affected.)
account_id       first_name      last_name       balance          atm_count
1234567 ,        Jhon ,  von Neumann ,   9999.980 ,      55
223344 ,         Stieve ,        Jobs ,  9999999.230 ,   24
2795028 ,        Koichi ,        Hasegawa ,      24362.060 ,     5
3141592 ,        Thomas ,        Edison ,        -279.670 ,      10
43383 ,  Bell ,  Graham ,        693.010 ,       1
653589793 ,      Nicola ,        Tesla ,         50288.450 ,     2
84197169 ,       Carlos ,        Ghosn ,         314159265358.970 ,      6
8462626 ,        Watt ,  James ,         41971.230 ,     3
```

#### 4.3.3 クエリとデータを分離する方法 その２

クエリにプレースホルダを設定し、実データはディクショナリ形式で指定します。 ディクショナリ形式でのデータの指定に備えて、プレースホルダにキー名を指定します。ここで指定するキー名は、ディクショナリでのキー名と一致する必要があります。

<code>INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES(%(account_id)s, %(first_name)s, %(last_name)s, %(balance)s, %(atm_count)s );</code>

ディクショナリ形式でのデータの指定は、次のように行います。

<code>
new_row = {
    'account_id' : '998877'
    'first_name' : 'Bill'
    'last_name' : 'Gates'
    'balance' : 88888888.34,
    'atm_count' : 54
}
</code>

execute()メソッドの引数に、クエリ文字列とディクショナリ変数を指定します。

<code>result1 = sql_cursor.execute(query1, new_row)</code>

コードは次のようになります。

```python :
#coding: utf-8
import pymysql.cursors #Python から DB を利用するためのモジュールを利用

#insert03.py:
#テーブルにデータを挿入する
#(データをディクショナリ形式で指定）

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
```

実行結果は次のようになります。

```bash
実行するクエリ: INSERT INTO BankAccount(account_id, first_name,last_name, balance, atm_count)  VALUES(  %(account_id)s,  %(first_name)s,  %(last_name)s,  %(balance)s,  %(atm_count)s );
ディクショナリ内のデータ: 
{'account_id': '998877', 'first_name': 'Bill', 'last_name': 'Gates', 'balance': 88888888.34, 'atm_count': 54}
クエリを実行しました。(1 row affected.)
●クエリの実行(データの選択)
実行するクエリ: SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;
クエリを実行しました。(9 row affected.)
account_id       first_name      last_name       balance          atm_count
1234567 ,        Jhon ,  von Neumann ,   9999.980 ,      55
223344 ,         Stieve ,        Jobs ,  9999999.230 ,   24
2795028 ,        Koichi ,        Hasegawa ,      24362.060 ,     5
3141592 ,        Thomas ,        Edison ,        -279.670 ,      10
43383 ,  Bell ,  Graham ,        693.010 ,       1
653589793 ,      Nicola ,        Tesla ,         50288.450 ,     2
84197169 ,       Carlos ,        Ghosn ,         314159265358.970 ,      6
8462626 ,        Watt ,  James ,         41971.230 ,     3
998877 ,         Bill ,  Gates ,         88888888.340 ,  54
```

### 4.4 外部からのデータ入力

実際のデータベース操作では、入力するデータを外部から受け取る必要があります。キーボードやWEB の入力フォームをはじめ、外部からデータを入力する方法はいくつか存在します。データの受取の方法は場合によって様々ですが、受け取り後に注意をしてデータを取り扱う必要があります。
外部から受け取ったデータをそのまま適用すると、思わぬ不具合や脆弱性を持つこともあります。

#### 4.4.1 外部から受け取ったデータをそのまま反映する

外部から受け取ったデータを、そのままクエリに反映する方法を用います。１件分のデータをキーボードから入力します。
入力するデータは次のものを想定しています。

```bash
■データを入力してください。account_id: 987987 first_name: Linus last_name: Tovalds
balance: 6666666.66
atm_count: 26
```

データの入力には"input()"メソッドを使用します。引数には、入力を催すために表示する文字列を指定します。入力した文字列は変数に格納されます。

<code>new_account_id = input('account_id: ') new_first_name = input('first_name: ') new_last_name = input('last_name: ') new_balance = input('balance: ')
new_atm_count = input('atm_count: ')</code>

input()メソッドの使い方については、下記 WEB サイトに詳しい解説があります。

[Python documentation](https://docs.python.org/ja/3/library/functions.html#input)

下記に input()メソッドの解説を抜粋します。

引数 prompt が存在すれば、それが末尾の改行を除いて標準出力に書き出されます。次に、この関数は入力から 1 行を読み込み、文字列に変換して (末尾の改行を除いて) 返します。 EOF が読み込まれたとき、 EOFError が送出されます。

入力したデータをクエリに展開します。入力したデータを文字列に展開するには、"f 文字列"を使用します。 f"… {変数名} …"のように記述すると、{変数名}の部分にその変数の内容が展開されます。たとえば、次のように利用します。

<code>f"INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)
VALUES('{new_account_id}', '{new_first_name}', '{new_last_name}', {new_balance}, {new_atm_count})"</code>

入力した内容が展開されると、次のような文字列となります。

<code>INSERT INTO BankAccount(account_id, first_name,last_name, balance, atm_count) VALUES('987987', 'Linus', 'Tovalds', 6666666.66, 26)</code>

使用するコードは次のとおりです。

```python
#coding: utf-8 import sys
import pymysql.cursors #Python から DB を利用するためのモジュールを利用

#input01.py:
#ユーザが入力したデータをテーブルに挿入する#(クエリの中にデータを直接展開）)

def main():
    #DB サーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user', #データベースにログインするユーザ名
        passwd='password',#データベースユーザのパスワード
        host='localhost', #接続先 DB のホストorIPアドレス
        db='practice'
    )
    #cursor オブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #テーブルにデータを挿入する
    print('■データを入力してください');
    new_account_id = input('account_id: ') new_first_name = input('first_name: ') 
    new_last_name = input('last_name: ')

    new_balance = input('balance: ')
    new_atm_count = input('atm_count: ')

    print('●クエリの実行(データの挿入)')

    query1 = 'INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count) ' \
    f" VALUES('{new_account_id}', '{new_first_name}','{new_last_name}', {new_balance}, {new_atm_count})";

    print('実行するクエリ: ' + query1)

    result1 = sql_cursor.execute(query1) #クエリを実行。変更した row の数が戻り値となる
    print('クエリを実行しました。('+ str(result1) +' row affected.)')

    #変更を実際に反映させるsql_connection.commit()


    #挿入したデータを含めてすべてのデータを表示print('●クエリの実行(データの選択)')
    query2 = 'SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;' #クエリのコマンド


    print('実行するクエリ: ' + query2)
    result2 = sql_cursor.execute(query2) #クエリを実行。取得した row が戻り値となる

    print('クエリを実行しました。('+ str(result2) +' row affected.)')


    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count') #クエリを実行した結果得られたデータを 1 行ずつ表示する
    for row in sql_cursor.fetchall():
    print( row[0], ',\t', row[1], ',\t', row[2], ',\t', row[3], ',\t', row[4])
main()
```

実行結果は次のようになります。

```bash
■データを入力してください
account_id: 987987
first_name: Linus
last_name: Tovalds
balance: 6666666.66
atm_count: 26
●クエリの実行(データの挿入)
実行するクエリ: INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count)  VALUES('987987', 'Linus','Tovalds', 6666666.66, 26)
クエリを実行しました。(1 row affected.)
実行するクエリ: SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;
クエリを実行しました。(10 row affected.)
account_id       first_name      last_name       balance          atm_count
1234567 ,        Jhon ,  von Neumann ,   9999.980 ,      55
223344 ,         Stieve ,        Jobs ,  9999999.230 ,   24
2795028 ,        Koichi ,        Hasegawa ,      24362.060 ,     5
3141592 ,        Thomas ,        Edison ,        -279.670 ,      10
43383 ,  Bell ,  Graham ,        693.010 ,       1
653589793 ,      Nicola ,        Tesla ,         50288.450 ,     2
84197169 ,       Carlos ,        Ghosn ,         314159265358.970 ,      6
8462626 ,        Watt ,  James ,         41971.230 ,     3
987987 ,         Linus ,         Tovalds ,       6666666.660 ,   26
998877 ,         Bill ,  Gates ,         88888888.340 ,  54
```

#### 4.4.2 SQLインジェクションの危険性

SQL インジェクションとは、入力欄に SQL コマンドを巧妙に埋め込み、データを改竄したり消したり、または不正に盗み出す行為の総称です。
例えば、悪意のあるユーザが「名前」の欄に SQL コマンドを混入させて、全く関係のない他のユーザの登録情報を書き換える事も考えられます。
このシステムの例では、"account_id"の入力欄に下記のコマンドを入力すると、意図しないデータの書き換えが行われてしまいます。

<code>3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン';</code>

実験の前に、MariaDB にログインして元のデータを確認しておきましょう。

```sql
MariaDB [practice]> SELECT * FROM BankAccount;
+------------+------------+-------------+------------------+-----------+
| account_id | first_name | last_name   | balance          | atm_count |
+------------+------------+-------------+------------------+-----------+
| 1234567    | Jhon       | von Neumann |         9999.980 |        55 |
| 223344     | Stieve     | Jobs        |      9999999.230 |        24 |
| 2795028    | Koichi     | Hasegawa    |        24362.060 |         5 |
| 3141592    | Thomas     | Edison      |         -279.670 |        10 |
| 43383      | Bell       | Graham      |          693.010 |         1 |
| 653589793  | Nicola     | Tesla       |        50288.450 |         2 |
| 84197169   | Carlos     | Ghosn       | 314159265358.970 |         6 |
| 8462626    | Watt       | James       |        41971.230 |         3 |
| 987987     | Linus      | Tovalds     |      6666666.660 |        26 |
| 998877     | Bill       | Gates       |     88888888.340 |        54 |
+------------+------------+-------------+------------------+-----------
```

データを確認したら、"input01.py"を実行し、下記の文字列を"account_id"の欄に入力してみましょう。

<code>3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン'; #</code>

実行結果の四角で囲った部分に注目してください。全く関係のないデータが書き換わっていることが確認できます。このプログラムは、データを新規に追加することを意図しているのに、全く関係のない他のユーザ情報が書き換えられてしまいました。

```bash
■データを入力してください
account_id: 3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン'; #
first_name: 
last_name: aaaa
balance: bbbb
atm_count: 22
●クエリの実行(データの挿入)
実行するクエリ: INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count)  VALUES('3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン'; #', '','aaaa', bbbb, 22)
クエリを実行しました。(2 row affected.)
実行するクエリ: SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;
クエリを実行しました。(10 row affected.)
account_id       first_name      last_name       balance          atm_count
1234567 ,        Jhon ,  von Neumann ,   9999.980 ,      55
223344 ,         Stieve ,        Jobs ,  9999999.230 ,   24
2795028 ,        Koichi ,        Hasegawa ,      24362.060 ,     5
3141592 ,        怪盗ルパン ,    Edison ,        -279.670 ,      10
43383 ,  Bell ,  Graham ,        693.010 ,       1
653589793 ,      Nicola ,        Tesla ,         50288.450 ,     2
84197169 ,       Carlos ,        Ghosn ,         314159265358.970 ,      6
8462626 ,        Watt ,  James ,         41971.230 ,     3
987987 ,         Linus ,         Tovalds ,       6666666.660 ,   26
998877 ,         Bill ,  Gates ,         88888888.340 ,  54
```

表示された実行結果のうち、次の部分に注目してください。

`実行するクエリ: INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)
VALUES('3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン'; #', '', 'aaaa', bbbb, 22)`

前半はプログラムに埋め込まれていたクエリですが、後半は不正に入力されたクエリです。それらが組み合わさって「悪意があるけれどクエリとしては成立しているクエリ」が出来上がってしまいました。なお、"ON DUPLICATE KEY UPDATE…"は、「主キーが重複していればデータを更新する」という意味で、"#"以降はコメントとなります。
これらを巧妙に組み合わせ、システムに意図せぬ動作をさせるのが「SQL インジェクション」です。外部からデータを受け取り SQL と連携させるには、これについて予め考慮しておく必要があります。

#### 削除する

```sql
MariaDB [practice]>  DELETE FROM BankAccount WHERE account_id = '3141592';
```

#### 4.4.3 クエリとデータを分散する

SQLインジェクションの可能性を減らす方法のひとつが、プレースホルダを使用する方法です。この方法は「3.3.2.クエリとデータを分離する方法 その１」で説明しました。
クエリの「命令」と「データ」を分離することで、意図せぬ命令を埋め込まれることを防ぎます。

プレースホルダを使用するには、クエリの中のデータ部分を"%s"で置き換えます。

<code>INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)
VALUES(%s, %s, %s, %s, %s);</code>

実際のデータは"execute()"メソッドの引数で指定します。

<code>result1 = sql_cursor.execute(query1, (new_account_id, new_first_name, new_last_name, new_balance, new_atm_count))</code>

入力するデータは次のものを想定します。

```bash
account_id: 334455 
first_name: Mark 
last_name: Zuckerberg 
balance: 9998877.66
atm_count: 33
```

コードは次の通りです。

```python
#coding: utf-8 import sys
import pymysql.cursors #Python から DB を利用するためのモジュールを利用

#input02.py:
#ユーザが入力したデータをテーブルに挿入する#(クエリとデータを分離）

def main():
    #DB サーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user', #データベースにログインするユーザ名
        passwd='password',#データベースユーザのパスワード
        host='localhost', #接続先 DB のホストorIPアドス
        db='practice'
    )
    #cursor オブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #テーブルにデータを挿入する
    print('■データを入力してください')
    new_account_id = input('account_id: ') new_first_name = input('first_name: ')
    new_last_name = input('last_name: ')
    new_balance = input('balance: ')
    new_atm_count = input('atm_count: ')

    print('●クエリの実行(データの挿入)')

    query1 = 'INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) ' \ 
            ' VALUES(%s, %s, %s, %s, %s)';

    print('実行するクエリ: ' + query1)
    
    #クエリを実行。変更した row の数が戻り値となる
    result1 = sql_cursor.execute(query1, (new_account_id, new_first_name, new_last_name, new_balance, new_atm_count))

    print('クエリを実行しました。('+ str(result1) +' row affected.)')

    #変更を実際に反映させる
    sql_connection.commit()

    #挿入したデータを含めてすべてのデータを表示
    print('●クエリの実行(データの選択)')
    query2 = 'SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;' #クエリのコマンド


    print('実行するクエリ: ' + query2)
    result2 = sql_cursor.execute(query2) #クエリを実行。取得した row が戻り値となる

    print('クエリを実行しました。('+ str(result2) +' row affected.)')

    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count') #クエリを実行した結果得られたデータを 1行ずつ表示する
    for row in sql_cursor.fetchall():
        print( row[0], ',\t', row[1], ',\t', row[2], ',\t', row[3], ',\t', row[4])
main() 
```

正常なデータを登録した場合の実行結果は次のようになります。

```bash
■データを入力してください
account_id: 334455
first_name: Mark
last_name: Zuckerberg
balance: 9998877.66
atm_count: 33
●クエリの実行(データの挿入)
実行するクエリ: INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)  VALUES(%s, %s, %s, %s, %s)
クエリを実行しました。(1 row affected.)
●クエリの実行(データの選択)
実行するクエリ: SELECT account_id, first_name, last_name, balance, atm_count FROM BankAccount;
クエリを実行しました。(10 row affected.)
account_id       first_name      last_name       balance          atm_count
1234567 ,        Jhon ,  von Neumann ,   9999.980 ,      55
223344 ,         Stieve ,        Jobs ,  9999999.230 ,   24
2795028 ,        Koichi ,        Hasegawa ,      24362.060 ,     5
334455 ,         Mark ,  Zuckerberg ,    9998877.660 ,   33
43383 ,  Bell ,  Graham ,        693.010 ,       1
653589793 ,      Nicola ,        Tesla ,         50288.450 ,     2
84197169 ,       Carlos ,        Ghosn ,         314159265358.970 ,      6
8462626 ,        Watt ,  James ,         41971.230 ,     3
987987 ,         Linus ,         Tovalds ,       6666666.660 ,   26
998877 ,         Bill ,  Gates ,         88888888.340 ,  54
```

MariaDB にログインし、データが登録されているかどうか確認してください。

```sql
MariaDB [practice]> SELECT * FROM BankAccount;
```

```bash
+------------+------------+-------------+------------------+-----------+
| account_id | first_name | last_name   | balance          | atm_count |
+------------+------------+-------------+------------------+-----------+
| 1234567    | Jhon       | von Neumann |         9999.980 |        55 |
| 223344     | Stieve     | Jobs        |      9999999.230 |        24 |
| 2795028    | Koichi     | Hasegawa    |        24362.060 |         5 |
| 334455     | Mark       | Zuckerberg  |      9998877.660 |        33 |
| 43383      | Bell       | Graham      |          693.010 |         1 |
| 653589793  | Nicola     | Tesla       |        50288.450 |         2 |
| 84197169   | Carlos     | Ghosn       | 314159265358.970 |         6 |
| 8462626    | Watt       | James       |        41971.230 |         3 |
| 987987     | Linus      | Tovalds     |      6666666.660 |        26 |
| 998877     | Bill       | Gates       |     88888888.340 |        54 |
+------------+------------+-------------+------------------+-----------+
10 rows in set (0.001 sec)
```

入力したデータがそのまま反映されていることがわかります。

前節で入力した SQL インジェクションを引き起こすコマンドを入力してみましょう。

<code>3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン'; #</code>

```bash
■データを入力してください
account_id: 3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン'; # 
first_name: aaa
last_name: bbb
balance: 1111111
atm_count: 22
●クエリの実行(データの挿入)
実行するクエリ: INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)  VALUES(%s, %s, %s, %s, %s)
Traceback (most recent call last):
  File "/home/pi/python_sql/input02.py", line 54, in <module>
    main() 
    ^^^^^^
  File "/home/pi/python_sql/input02.py", line 34, in main
    result1 = sql_cursor.execute(query1, (new_account_id, new_first_name, new_last_name, new_balance, new_atm_count))
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/pymysql/cursors.py", line 148, in execute
    result = self._query(query)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/pymysql/cursors.py", line 310, in _query
    conn.query(q)
  File "/usr/lib/python3/dist-packages/pymysql/connections.py", line 548, in query
    self._affected_rows = self._read_query_result(unbuffered=unbuffered)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/pymysql/connections.py", line 775, in _read_query_result
    result.read()
  File "/usr/lib/python3/dist-packages/pymysql/connections.py", line 1156, in read
    first_packet = self.connection._read_packet()
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/pymysql/connections.py", line 725, in _read_packet
    packet.raise_for_error()
  File "/usr/lib/python3/dist-packages/pymysql/protocol.py", line 221, in raise_for_error
    err.raise_mysql_exception(self._data)
  File "/usr/lib/python3/dist-packages/pymysql/err.py", line 143, in raise_mysql_exception
    raise errorclass(errno, errval)
pymysql.err.DataError: (1406, "Data too long for column 'account_id' at row 1")
```

例外が発生しクエリが実行できなかったことが伺えます。

もういちど、データベースの内容を確認してみましょう。例外が発生しクエリが実行できなかったことが伺えます。もういちど、データベースの内容を確認してみましょう。

```sql
MariaDB [practice]> SELECT * FROM BankAccount;
```

```bash
+------------+------------+-------------+------------------+-----------+
| account_id | first_name | last_name   | balance          | atm_count |
+------------+------------+-------------+------------------+-----------+
| 1234567    | Jhon       | von Neumann |         9999.980 |        55 |
| 223344     | Stieve     | Jobs        |      9999999.230 |        24 |
| 2795028    | Koichi     | Hasegawa    |        24362.060 |         5 |
| 334455     | Mark       | Zuckerberg  |      9998877.660 |        33 |
| 43383      | Bell       | Graham      |          693.010 |         1 |
| 653589793  | Nicola     | Tesla       |        50288.450 |         2 |
| 84197169   | Carlos     | Ghosn       | 314159265358.970 |         6 |
| 8462626    | Watt       | James       |        41971.230 |         3 |
| 987987     | Linus      | Tovalds     |      6666666.660 |        26 |
| 998877     | Bill       | Gates       |     88888888.340 |        54 |
+------------+------------+-------------+------------------+-----------+
10 rows in set (0.001 sec)
```

例外が発生しプログラムが停止してしまいましたが、データベースの内容は変更されていません。例外の発生は、例外をキャッチすれば見かけ上は問題がないようにプログラムが振舞うこともできます。
このような対策は、不正な入力からシステムを守ることに役立ちます。


