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