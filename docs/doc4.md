# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 4. MariaDBとPythonの連携

PythonからMariaDBを操作するプログラムを作成します。下記のように、プログラムを収納するディレクトリを作成します。

```bash
pi@raspberrypi:~ $ cd ~
```

```bash
pi@raspberrypi:~ $ mkdir python_sql
```

```bash
pi@raspberrypi:~ $ cd python_sql
```

MariaDBで管理されているデータベースをPythonから操作するには、`PyMySQL`ライブラリを利用する必要があります。下記のコマンドを使って、PyMySQLがすでにインストールされているか確認しましょう。

```bash
pi@raspberrypi:~/python_sql $ pip list | grep PyMySQL
```

```bash
PyMySQL                            1.0.2
types-PyMySQL                      1.0
```

上記のように`PyMySQL`が表示されればインストールされています。

`PyMySQL`については、下記のURLより情報を収集することができます。

[PyMySQL documentation](https://pymysql.readthedocs.io/en/latest/index.html)

### 4.1 操作フォルダの設定

VSCodeからPythonスクリプトを実行するため、Raspberry Piの`python_sql`ディレクトリにアクセスします。

* フォルダーを開く
    * python_sql
        * OK

![IPAdress](../images/vscode20.PNG)

* 新しいテキストファイル
    * 名前の変更[`sample.py`]

![VSCode](../images/vscode25.PNG)

`sample.py`の内容

```python
print('Hello Python')
```

### 4.2 Pythonスクリプトの実行

#### 4.2.1 ボタンからの実行

* サイドバー`拡張機能`
    * `Python`と検索
        * 一番上をクリック
            * インストール

![VSCode](../images/vscode24.PNG)

* 再生マーク

![VSCode](../images/vscode26.PNG)

#### 4.2.2 ターミナルからの実行

```bash
pi@raspberrypi:~ $ cd python_sql
```

```bash
pi@raspberrypi:~/python_sql $ python sample.py
```

### 4.3 クエリの実行

PythonからMariaDBのクエリを実行します。練習用DBからSELECTクエリを実行し、結果を出力します。

次のソースコードを作成し、実行してください。

`select01.py`

```python
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
    #cursorオブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    query = 'SELECT * FROM BankAccount;' #クエリのコマンド
    sql_cursor.execute(query) #クエリを実行
    print(query, ' のクエリの結果\n')
    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count' )

    #クエリを実行した結果得られたデータを1行ずつ表示する
    for row in sql_cursor.fetchall():
        print( row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])
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

### 4.4 データベースの内容を変更しないクエリの実行

データベースのデータを参照するだけで内容を変更しないクエリは、概ね下記のようなコードで実行できます。なお、「データを参照するだけで内容を変更しない操作」を「副作用のない操作」ということもあります。

`select02.py`

```python
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

カラム名を`*`で指定するような書き方は避けるべきです。

下記のように

<code>SELECT account_id, first_name, last_name, balance, atm_count FROM ...</code>

カラム名を指定すると良いでしょう。

### 4.5 データベースの内容を変更するクエリの実行

#### 4.5.1 クエリを直接指定する方法

1行のデータを挿入することを考えます。クエリ文字列は下記のようになります。

<code>INSERT INTO BankAccount(account_id, first_name,last_name, balance, atm_count) VALUES('1234567','Jhon', 'von Neumann', 9999.98, 55)</code>

次のプログラムは、1行のデータを上記のクエリを使って挿入した後、すべての行を選択し表示します。クエリ文字列を設定して実行するまでの手順は、ほぼ同一であることを確認してください。

<code>sql_connection.commit()</code>

挿入したデータを実際に反映させるには、`commit()`メソッドを実行する必要があります。

`insert01.py`

```python
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
        print( row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])
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

#### 4.5.2 行を削除するコマンド

デバッグのためにプログラムを再実行すると、同じデータを重複して挿入することになります。
MariaDBにログインして、下記のように新しく追加するデータを予め削除しておきましょう。

```db
MariaDB [practice]> DELETE FROM BankAccount WHERE account_id = '1234567';
```

#### 4.5.3 クエリとデータを分離する方法 その１

1行のデータを挿入することを考えます。相当するクエリ文字列は下記のようになります。

<code>INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES('223344', 'Stieve', 'Jobs', 9999999.23, 24);</code>

次のプログラムは、上記クエリの`VALUES(…)`の部分を実際のデータではなく、`%s`のようなプレースホルダを指定し、後から実データを割り当てる方法を用いています。

<code>INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES(%s, %s, %s, %s, %s);</code>

プレースホルダで指定した値は、sql_cursor.execute()メソッドの引数に指定します。クエリとデータを分離します。

<code>result1 = sql_cursor.execute(query1, (new_account_id, new_first_name, new_last_name, new_balance, new_atm_count) )</code>

コードは次のようになります。

`insert02.py`

```python
#coding: utf-8

import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

def main():
    #DB サーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user',  #データベースにログインするユーザ名
        passwd='password',#データベースユーザのパスワード
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
        print( row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])

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

#### 4.5.4 クエリとデータを分離する方法 その２

クエリにプレースホルダを設定し、実データはディクショナリ形式で指定します。 ディクショナリ形式でのデータの指定に備えて、プレースホルダにキー名を指定します。ここで指定するキー名は、ディクショナリでのキー名と一致する必要があります。

<code>INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) VALUES(%(account_id)s, %(first_name)s, %(last_name)s, %(balance)s, %(atm_count)s );</code>

ディクショナリ形式でのデータの指定は、次のように行います。

<code>new_row = {
    'account_id' : '998877'
    'first_name' : 'Bill'
    'last_name' : 'Gates'
    'balance' : 88888888.34,
    'atm_count' : 54
}</code>

execute()メソッドの引数に、クエリ文字列とディクショナリ変数を指定します。

<code>result1 = sql_cursor.execute(query1, new_row)</code>

コードは次のようになります。

`insert03.py`

```python :
#coding: utf-8

import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

def main():
    #DB サーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user',  #データベースにログインするユーザ名
        passwd='password',#データベースユーザのパスワード
        host='localhost', #接続先DBのホストorIPアドレス
        db='practice'
    )

    #cursorオブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #テーブルにデータを挿入する
    print('●クエリの実行(データの挿入)')

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
        print( row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])

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

### 4.6 外部からのデータ入力

実際のデータベース操作では、入力するデータを外部から受け取る必要があります。キーボードやWebの入力フォームをはじめ、外部からデータを入力する方法はいくつか存在します。データの受取の方法は場合によって様々ですが、受け取り後に注意をしてデータを取り扱う必要があります。外部から受け取ったデータをそのまま適用すると、思わぬ不具合や脆弱性を持つこともあります。

#### 4.6.1 外部から受け取ったデータをそのまま反映する

外部から受け取ったデータを、そのままクエリに反映する方法を用います。１件分のデータをキーボードから入力します。入力するデータは次のものを想定しています。

```bash
■データを入力してください。
account_id: 987987
first_name: Linus
last_name: Tovalds
balance: 6666666.66
atm_count: 26
```

データの入力には`input()`メソッドを使用します。引数には、入力を催すために表示する文字列を指定します。入力した文字列は変数に格納されます。

<code>new_account_id = input('account_id: ') new_first_name = input('first_name: ') new_last_name = input('last_name: ') new_balance = input('balance: ')
new_atm_count = input('atm_count: ')</code>

input()メソッドの使い方については、下記Webサイトに詳しい解説があります。

[Python documentation](https://docs.python.org/ja/3/library/functions.html#input)

下記に input()メソッドの解説を抜粋します。

引数promptが存在すれば、それが末尾の改行を除いて標準出力に書き出されます。次に、この関数は入力から1行を読み込み、文字列に変換して (末尾の改行を除いて) 返します。 EOF が読み込まれたとき、 EOFError が送出されます。

入力したデータをクエリに展開します。入力したデータを文字列に展開するには、"f 文字列"を使用します。 f"… {変数名} …"のように記述すると、{変数名}の部分にその変数の内容が展開されます。たとえば、次のように利用します。

<code>f"INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)
VALUES('{new_account_id}', '{new_first_name}', '{new_last_name}', {new_balance}, {new_atm_count})"</code>

入力した内容が展開されると、次のような文字列となります。

<code>INSERT INTO BankAccount(account_id, first_name,last_name, balance, atm_count) VALUES('987987', 'Linus', 'Tovalds', 6666666.66, 26)</code>

使用するコードは次のとおりです。

`input01.py`

```python
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
    #cursorオブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #テーブルにデータを挿入する
    print('■データを入力してください')
    new_account_id = input('account_id: ') 
    new_first_name = input('first_name: ') 
    new_last_name = input('last_name: ')
    new_balance = input('balance: ')
    new_atm_count = input('atm_count: ')

    print('●クエリの実行(データの挿入)')

    query1 = 'INSERT INTO BankAccount(account_id,first_name, last_name, balance, atm_count) ' \
            f" VALUES('{new_account_id}', '{new_first_name}','{new_last_name}', {new_balance}, {new_atm_count})";

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

    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count') #クエリを実行した結果得られたデータを1行ずつ表示する
    for row in sql_cursor.fetchall():
        print( row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])

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

#### 4.6.2 SQLインジェクションの危険性

SQLインジェクションとは、入力欄にSQLコマンドを巧妙に埋め込み、データを改竄したり消したり、または不正に盗み出す行為の総称です。例えば、悪意のあるユーザが「名前」の欄にSQLコマンドを混入させて、全く関係のない他のユーザの登録情報を書き換える事も考えられます。このシステムの例では、`account_id`の入力欄に下記のコマンドを入力すると、意図しないデータの書き換えが行われてしまいます。

<code>3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン'; #</code>

実験の前に、MariaDBにログインして元のデータを確認しておきましょう。

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
| 3141592    | Thomas     | Edison      |         -279.670 |        10 |
| 43383      | Bell       | Graham      |          693.010 |         1 |
| 653589793  | Nicola     | Tesla       |        50288.450 |         2 |
| 84197169   | Carlos     | Ghosn       | 314159265358.970 |         6 |
| 8462626    | Watt       | James       |        41971.230 |         3 |
| 987987     | Linus      | Tovalds     |      6666666.660 |        26 |
| 998877     | Bill       | Gates       |     88888888.340 |        54 |
+------------+------------+-------------+------------------+-----------
```

データを確認したら、`input01.py`を実行し、下記の文字列を`account_id`の欄に入力してみましょう。

<code>3141592','','',0,0) ON DUPLICATE KEY UPDATE first_name = '怪盗ルパン'; #</code>

実行結果に注目してください。全く関係のないデータが書き換わっていることが確認できます。このプログラムは、データを新規に追加することを意図しているのに、全く関係のない他のユーザ情報が書き換えられてしまいました。

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

前半はプログラムに埋め込まれていたクエリですが、後半は不正に入力されたクエリです。それらが組み合わさって「悪意があるけれどクエリとしては成立しているクエリ」が出来上がってしまいました。なお、`ON DUPLICATE KEY UPDATE…`は、「主キーが重複していればデータを更新する」という意味で、`#`以降はコメントとなります。これらを巧妙に組み合わせ、システムに意図せぬ動作をさせるのが「SQLインジェクション」です。外部からデータを受け取りSQLと連携させるには、これについて予め考慮しておく必要があります。

#### 4.6.3 削除する

```sql
MariaDB [practice]>  DELETE FROM BankAccount WHERE account_id = '3141592';
```

#### 4.6.4 クエリとデータを分散する

SQLインジェクションの可能性を減らす方法のひとつが、プレースホルダを使用する方法です。クエリの「命令」と「データ」を分離することで、意図せぬ命令を埋め込まれることを防ぎます。

プレースホルダを使用するには、クエリの中のデータ部分を`%s`で置き換えます。

<code>INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count)
VALUES(%s, %s, %s, %s, %s);</code>

実際のデータは`execute()`メソッドの引数で指定します。

<code>result1 = sql_cursor.execute(query1, (new_account_id, new_first_name, new_last_name, new_balance, new_atm_count))</code>

入力するデータは次のものを想定します。

```bash
account_id: 334455 
first_name: Mark 
last_name: Zuckerberg 
balance: 9998877.66
atm_count: 33
```

`input02.py`

コードは次の通りです。

```python
#coding: utf-8

import pymysql.cursors #PythonからDBを利用するためのモジュールを利用

def main():
    #DBサーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user',  #データベースにログインするユーザ名
        passwd='password',#データベースユーザのパスワード
        host='localhost', #接続先DBのホストorIPアドス
        db='practice'
    )
    #cursorオブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()

    #テーブルにデータを挿入する
    print('■データを入力してください')
    new_account_id = input('account_id: ')
    new_first_name = input('first_name: ')
    new_last_name = input('last_name: ')
    new_balance = input('balance: ')
    new_atm_count = input('atm_count: ')

    print('●クエリの実行(データの挿入)')

    query1 = 'INSERT INTO BankAccount(account_id, first_name, last_name, balance, atm_count) ' \
                ' VALUES(%s, %s, %s, %s, %s)';

    print('実行するクエリ: ' + query1)
    
    #クエリを実行。変更したrowの数が戻り値となる
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

    print( 'account_id \t', 'first_name \t', 'last_name \t', 'balance \t ','atm_count') #クエリを実行した結果得られたデータを1行ずつ表示する
    for row in sql_cursor.fetchall():
        print( row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])

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

MariaDBにログインし、データが登録されているかどうか確認してください。

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

前節で入力したSQLインジェクションを引き起こすコマンドを入力してみましょう。

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
