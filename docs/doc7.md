# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 7. データの集計・分析

測定したデータは、そのままでは役に立ちません。集計・分析して可視化することで思いもしなかった用途に活用することができます。

### 7.1 データの集計

テーブルの構造をもう一度確認しておきましょう。

| 内容 | カラム名 | データ型 | 制約 |
| --- | --- | --- | --- |
| 主キー | row_id | INT | PRIMARY KEY NOT NULL AUTO_INCREMENT |
| 取得した日付と時刻 | timestamp | TIMESTAMP | - |
| 取得したノードの識別子 | identifier | CHAR(24) | - |
| 温度 | temperature | DOUBLE | - |
| 湿度 | humidity | DOUBLE | - |
| 気圧 | pressure | DOUBLE | - |

#### 7.1.1 ノードを指定したデータの取り出し

現在のところ、ふたつのノードからデータを取得してデータベースに登録しています。これらを区別してデータを取り出す方法を考えます。
ノードの識別子によって、「どのノードからのデータであるか」を識別することができます。このデータは、各自のプログラムに埋め込まれています。

|ノードの識別子|どのデータか|
|---|---|
|tochigi_iot_999|RaspberryPiに直接接続された BME280センサから取得したデータ（室内の温度・湿度・気圧）|
|tochigi_mqtt_999|esp32に接続されたBME280センサから取得したデータ（屋外の温度・湿度・気圧）|

これらの識別子の値は、各個人によって異なります。プログラムを確認する方法もありますが、これらの値を下記のSQLクエリで一覧することができます。

```sql
MariaDB [iot_storage]> SELECT DISTINCT identifier FROM Ambient;
```

```sql
+------------------+
| identifier       |
+------------------+
| tochigi_iot_999  |
| tochigi_mqtt_999 |
+------------------+
2 rows in set (0.001 sec)
```

`DISTINCT`句は、選択されるデータの重複を取り除くことを指示します。

カラム`identifier`を指定してデータを取り出す、下記のようなクエリを使用します。このクエリでは、`identifier`カラムの値`tochigi_mqtt_999`である行のみを選択します。`WHERE`句のあとに続く条件式で取り出すデータを指定します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient WHERE identifier = "tochigi_mqtt_999";
```

```sql
+--------+---------------------+------------------+-------------+----------+----------+
| row_id | timestamp           | identifier       | temperature | humidity | pressure |
+--------+---------------------+------------------+-------------+----------+----------+
|     19 | 2024-09-19 14:59:51 | tochigi_mqtt_999 |       27.39 |    40.63 |  1000.71 |
|     20 | 2024-09-19 14:59:56 | tochigi_mqtt_999 |        27.4 |    40.68 |  1000.76 |
|     21 | 2024-09-19 15:00:01 | tochigi_mqtt_999 |        27.4 |    40.64 |  1000.75 |
|     22 | 2024-09-19 15:00:06 | tochigi_mqtt_999 |       27.35 |     40.7 |  1000.73 |
|     23 | 2024-09-19 15:00:11 | tochigi_mqtt_999 |       27.36 |    40.65 |  1000.75 |
|     24 | 2024-09-19 15:00:16 | tochigi_mqtt_999 |       27.36 |     40.4 |  1000.76 |
|     25 | 2024-09-19 15:00:21 | tochigi_mqtt_999 |       27.36 |     40.4 |  1000.79 |
|     26 | 2024-09-19 15:00:26 | tochigi_mqtt_999 |       27.36 |    40.96 |   1000.8 |
|     27 | 2024-09-19 15:00:31 | tochigi_mqtt_999 |       27.37 |    40.98 |  1000.75 |
|     28 | 2024-09-19 15:00:36 | tochigi_mqtt_999 |       27.37 |    40.56 |  1000.76 |
|     29 | 2024-09-19 15:00:41 | tochigi_mqtt_999 |       27.37 |    40.99 |   1000.7 |
|     30 | 2024-09-19 15:00:46 | tochigi_mqtt_999 |       27.37 |    40.38 |  1000.74 |
|     31 | 2024-09-19 15:00:51 | tochigi_mqtt_999 |       27.38 |     40.4 |  1000.77 |
|     32 | 2024-09-19 15:00:56 | tochigi_mqtt_999 |       27.38 |    40.53 |  1000.74 |
|     33 | 2024-09-19 15:01:01 | tochigi_mqtt_999 |       27.34 |     40.1 |  1000.68 |
|     34 | 2024-09-19 15:01:06 | tochigi_mqtt_999 |       27.34 |    40.66 |  1000.68 |
|     35 | 2024-09-19 15:01:11 | tochigi_mqtt_999 |       27.35 |    40.15 |  1000.75 |
|     36 | 2024-09-19 15:01:16 | tochigi_mqtt_999 |       27.35 |    40.23 |  1000.72 |
|     37 | 2024-09-19 15:01:21 | tochigi_mqtt_999 |       27.33 |    40.76 |  1000.69 |
|     38 | 2024-09-19 15:01:26 | tochigi_mqtt_999 |       27.33 |    40.61 |   1000.7 |
|     39 | 2024-09-19 15:01:31 | tochigi_mqtt_999 |       27.34 |    40.17 |  1000.77 |
|     40 | 2024-09-19 15:01:36 | tochigi_mqtt_999 |       27.35 |    40.23 |  1000.77 |
|     41 | 2024-09-19 15:01:41 | tochigi_mqtt_999 |       27.35 |    39.98 |  1000.72 |
|     42 | 2024-09-19 15:01:46 | tochigi_mqtt_999 |       27.35 |    40.02 |  1000.67 |
|     43 | 2024-09-19 15:01:51 | tochigi_mqtt_999 |       27.36 |    40.46 |  1000.66 |
|     44 | 2024-09-19 15:01:56 | tochigi_mqtt_999 |       27.36 |    40.26 |  1000.72 |
|     45 | 2024-09-19 15:02:01 | tochigi_mqtt_999 |       27.37 |    40.38 |  1000.65 |
|     46 | 2024-09-19 15:02:06 | tochigi_mqtt_999 |       27.38 |    40.05 |  1000.69 |
|     47 | 2024-09-19 15:02:11 | tochigi_mqtt_999 |       27.38 |    40.41 |  1000.74 |
|     48 | 2024-09-19 15:02:16 | tochigi_mqtt_999 |       27.37 |    40.02 |  1000.63 |
|     49 | 2024-09-19 15:02:21 | tochigi_mqtt_999 |       27.37 |    40.51 |  1000.66 |
|     50 | 2024-09-19 15:02:26 | tochigi_mqtt_999 |       27.37 |    40.08 |  1000.71 |
|     51 | 2024-09-19 15:27:41 | tochigi_mqtt_999 |       27.37 |    45.32 |  1000.47 |
|     52 | 2024-09-19 15:27:46 | tochigi_mqtt_999 |       27.38 |    45.22 |  1000.45 |
|     53 | 2024-09-19 15:27:51 | tochigi_mqtt_999 |        27.4 |    45.58 |  1000.49 |
|     54 | 2024-09-19 15:27:56 | tochigi_mqtt_999 |       27.43 |    45.97 |  1000.45 |
+--------+---------------------+------------------+-------------+----------+----------+
36 rows in set (0.001 sec)
```

#### 7.1.2 選択する行数の限定

データの数が増えてくると、一回のクエリで取り出すデータの数が膨大になります。データの数を限定して取り出します。次のクエリでは、取り出すデータの数を10行に限定します。`LIMIT`句により行数を指定します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient WHERE identifier = "tochigi_mqtt_999" LIMIT 10;
```

```sql
+--------+---------------------+------------------+-------------+----------+----------+
| row_id | timestamp           | identifier       | temperature | humidity | pressure |
+--------+---------------------+------------------+-------------+----------+----------+
|     19 | 2024-09-19 14:59:51 | tochigi_mqtt_999 |       27.39 |    40.63 |  1000.71 |
|     20 | 2024-09-19 14:59:56 | tochigi_mqtt_999 |        27.4 |    40.68 |  1000.76 |
|     21 | 2024-09-19 15:00:01 | tochigi_mqtt_999 |        27.4 |    40.64 |  1000.75 |
|     22 | 2024-09-19 15:00:06 | tochigi_mqtt_999 |       27.35 |     40.7 |  1000.73 |
|     23 | 2024-09-19 15:00:11 | tochigi_mqtt_999 |       27.36 |    40.65 |  1000.75 |
|     24 | 2024-09-19 15:00:16 | tochigi_mqtt_999 |       27.36 |     40.4 |  1000.76 |
|     25 | 2024-09-19 15:00:21 | tochigi_mqtt_999 |       27.36 |     40.4 |  1000.79 |
|     26 | 2024-09-19 15:00:26 | tochigi_mqtt_999 |       27.36 |    40.96 |   1000.8 |
|     27 | 2024-09-19 15:00:31 | tochigi_mqtt_999 |       27.37 |    40.98 |  1000.75 |
|     28 | 2024-09-19 15:00:36 | tochigi_mqtt_999 |       27.37 |    40.56 |  1000.76 |
+--------+---------------------+------------------+-------------+----------+----------+
10 rows in set (0.001 sec)
```

#### 7.1.3 並び順の指定・ソート

取り出したデータの並び順を変更します。データの並び順は昇順（値の小さいものから大きいものの順）・降順（値の大きいものから小さいものの順）があり、どのカラムを基準にするかを指定します。`ORDER BY`句を用いて、どのカラムを基準にするかを指定します。その後に`ASC`または`DESC`を指定します。`ASC`は昇順、`DESC`は降順となります。昇順を指定した場合は、一番値の小さいものから、降順を指定した場合は一番値の大きいものからデータを取り出します。

次のクエリは、日付・時刻を基準に古いデータから順に表示します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient ORDER BY timestamp ASC LIMIT 5;
```

```sql
+--------+---------------------+-----------------+-------------+----------+----------+
| row_id | timestamp           | identifier      | temperature | humidity | pressure |
+--------+---------------------+-----------------+-------------+----------+----------+
|      2 | 2024-09-06 20:03:00 | tochigi_iot_999 |       27.26 |    49.66 |   998.24 |
|      3 | 2024-09-09 18:07:19 | tochigi_iot_999 |       25.98 |     43.8 |   1001.8 |
|      4 | 2024-09-09 18:16:37 | tochigi_iot_999 |       25.76 |    42.79 |  1001.83 |
|      5 | 2024-09-11 15:44:57 | tochigi_iot_999 |       25.77 |    53.02 |  1001.27 |
|      6 | 2024-09-11 15:45:07 | tochigi_iot_999 |        25.8 |     53.3 |  1001.21 |
+--------+---------------------+-----------------+-------------+----------+----------+
5 rows in set (0.002 sec)
```

次のクエリは、日付・時刻を基準に新しいデータから順に表示します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient ORDER BY timestamp DESC LIMIT 5;
```

```sql
+--------+---------------------+------------------+-------------+----------+----------+
| row_id | timestamp           | identifier       | temperature | humidity | pressure |
+--------+---------------------+------------------+-------------+----------+----------+
|     54 | 2024-09-19 15:27:56 | tochigi_mqtt_999 |       27.43 |    45.97 |  1000.45 |
|     53 | 2024-09-19 15:27:51 | tochigi_mqtt_999 |        27.4 |    45.58 |  1000.49 |
|     52 | 2024-09-19 15:27:46 | tochigi_mqtt_999 |       27.38 |    45.22 |  1000.45 |
|     51 | 2024-09-19 15:27:41 | tochigi_mqtt_999 |       27.37 |    45.32 |  1000.47 |
|     50 | 2024-09-19 15:02:26 | tochigi_mqtt_999 |       27.37 |    40.08 |  1000.71 |
+--------+---------------------+------------------+-------------+----------+----------+
5 rows in set (0.001 sec)
```

#### 7.1.4 日付・時刻による期間の指定

このようなデータを取り扱うとき、特定の日時や時刻・期間を指定してデータを取り出し集計することになります。

次のクエリは、`timestamp`のカラム(日付・時刻)を基準に、`2024年09月11日16:00:00`以降に取得したデータを5行取り出します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient WHERE timestamp > '2024-09-11 16:00:00' LIMIT 5;
```

```sql
+--------+---------------------+------------------+-------------+----------+----------+
| row_id | timestamp           | identifier       | temperature | humidity | pressure |
+--------+---------------------+------------------+-------------+----------+----------+
|     17 | 2024-09-11 16:00:54 | tochigi_iot_999  |       25.78 |    49.92 |  1001.18 |
|     18 | 2024-09-11 16:01:04 | tochigi_iot_999  |       25.83 |    50.27 |  1001.11 |
|     19 | 2024-09-19 14:59:51 | tochigi_mqtt_999 |       27.39 |    40.63 |  1000.71 |
|     20 | 2024-09-19 14:59:56 | tochigi_mqtt_999 |        27.4 |    40.68 |  1000.76 |
|     21 | 2024-09-19 15:00:01 | tochigi_mqtt_999 |        27.4 |    40.64 |  1000.75 |
+--------+---------------------+------------------+-------------+----------+----------+
5 rows in set (0.002 sec)
```

次のクエリは、`timestamp`のカラム(日付・時刻)を基準に、`2024年09月11日9:00:00`から`2024年09月19日16:00:00`までの間に取得したデータすべて取り出します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient WHERE timestamp BETWEEN '2024-09-11 09:00:00' AND '2024-09-19 16:00:00';
```

```sql
+--------+---------------------+------------------+-------------+----------+----------+
| row_id | timestamp           | identifier       | temperature | humidity | pressure |
+--------+---------------------+------------------+-------------+----------+----------+
|      5 | 2024-09-11 15:44:57 | tochigi_iot_999  |       25.77 |    53.02 |  1001.27 |
|      6 | 2024-09-11 15:45:07 | tochigi_iot_999  |        25.8 |     53.3 |  1001.21 |
|      7 | 2024-09-11 15:45:18 | tochigi_iot_999  |       25.79 |    52.32 |   1001.2 |
|      8 | 2024-09-11 15:45:28 | tochigi_iot_999  |       25.78 |    52.95 |  1001.23 |
|      9 | 2024-09-11 15:45:38 | tochigi_iot_999  |       25.79 |     52.7 |  1001.19 |
|     10 | 2024-09-11 15:45:48 | tochigi_iot_999  |       25.79 |    52.61 |  1001.25 |
|     11 | 2024-09-11 15:45:58 | tochigi_iot_999  |       25.81 |    53.43 |  1001.26 |
|     12 | 2024-09-11 15:46:08 | tochigi_iot_999  |       25.82 |    53.22 |  1001.27 |
|     13 | 2024-09-11 15:46:18 | tochigi_iot_999  |       25.86 |    53.62 |  1001.25 |
|     14 | 2024-09-11 15:46:28 | tochigi_iot_999  |        25.9 |    53.89 |  1001.19 |
|     15 | 2024-09-11 15:46:38 | tochigi_iot_999  |       25.91 |    53.43 |  1001.22 |
|     16 | 2024-09-11 15:46:48 | tochigi_iot_999  |       25.84 |    52.71 |  1001.23 |
|     17 | 2024-09-11 16:00:54 | tochigi_iot_999  |       25.78 |    49.92 |  1001.18 |
|     18 | 2024-09-11 16:01:04 | tochigi_iot_999  |       25.83 |    50.27 |  1001.11 |
|     19 | 2024-09-19 14:59:51 | tochigi_mqtt_999 |       27.39 |    40.63 |  1000.71 |
|     20 | 2024-09-19 14:59:56 | tochigi_mqtt_999 |        27.4 |    40.68 |  1000.76 |
|     21 | 2024-09-19 15:00:01 | tochigi_mqtt_999 |        27.4 |    40.64 |  1000.75 |
|     22 | 2024-09-19 15:00:06 | tochigi_mqtt_999 |       27.35 |     40.7 |  1000.73 |
|     23 | 2024-09-19 15:00:11 | tochigi_mqtt_999 |       27.36 |    40.65 |  1000.75 |
|     24 | 2024-09-19 15:00:16 | tochigi_mqtt_999 |       27.36 |     40.4 |  1000.76 |
|     25 | 2024-09-19 15:00:21 | tochigi_mqtt_999 |       27.36 |     40.4 |  1000.79 |
|     26 | 2024-09-19 15:00:26 | tochigi_mqtt_999 |       27.36 |    40.96 |   1000.8 |
|     27 | 2024-09-19 15:00:31 | tochigi_mqtt_999 |       27.37 |    40.98 |  1000.75 |
|     28 | 2024-09-19 15:00:36 | tochigi_mqtt_999 |       27.37 |    40.56 |  1000.76 |
|     29 | 2024-09-19 15:00:41 | tochigi_mqtt_999 |       27.37 |    40.99 |   1000.7 |
|     30 | 2024-09-19 15:00:46 | tochigi_mqtt_999 |       27.37 |    40.38 |  1000.74 |
|     31 | 2024-09-19 15:00:51 | tochigi_mqtt_999 |       27.38 |     40.4 |  1000.77 |
|     32 | 2024-09-19 15:00:56 | tochigi_mqtt_999 |       27.38 |    40.53 |  1000.74 |
|     33 | 2024-09-19 15:01:01 | tochigi_mqtt_999 |       27.34 |     40.1 |  1000.68 |
|     34 | 2024-09-19 15:01:06 | tochigi_mqtt_999 |       27.34 |    40.66 |  1000.68 |
|     35 | 2024-09-19 15:01:11 | tochigi_mqtt_999 |       27.35 |    40.15 |  1000.75 |
|     36 | 2024-09-19 15:01:16 | tochigi_mqtt_999 |       27.35 |    40.23 |  1000.72 |
|     37 | 2024-09-19 15:01:21 | tochigi_mqtt_999 |       27.33 |    40.76 |  1000.69 |
|     38 | 2024-09-19 15:01:26 | tochigi_mqtt_999 |       27.33 |    40.61 |   1000.7 |
|     39 | 2024-09-19 15:01:31 | tochigi_mqtt_999 |       27.34 |    40.17 |  1000.77 |
|     40 | 2024-09-19 15:01:36 | tochigi_mqtt_999 |       27.35 |    40.23 |  1000.77 |
|     41 | 2024-09-19 15:01:41 | tochigi_mqtt_999 |       27.35 |    39.98 |  1000.72 |
|     42 | 2024-09-19 15:01:46 | tochigi_mqtt_999 |       27.35 |    40.02 |  1000.67 |
|     43 | 2024-09-19 15:01:51 | tochigi_mqtt_999 |       27.36 |    40.46 |  1000.66 |
|     44 | 2024-09-19 15:01:56 | tochigi_mqtt_999 |       27.36 |    40.26 |  1000.72 |
|     45 | 2024-09-19 15:02:01 | tochigi_mqtt_999 |       27.37 |    40.38 |  1000.65 |
|     46 | 2024-09-19 15:02:06 | tochigi_mqtt_999 |       27.38 |    40.05 |  1000.69 |
|     47 | 2024-09-19 15:02:11 | tochigi_mqtt_999 |       27.38 |    40.41 |  1000.74 |
|     48 | 2024-09-19 15:02:16 | tochigi_mqtt_999 |       27.37 |    40.02 |  1000.63 |
|     49 | 2024-09-19 15:02:21 | tochigi_mqtt_999 |       27.37 |    40.51 |  1000.66 |
|     50 | 2024-09-19 15:02:26 | tochigi_mqtt_999 |       27.37 |    40.08 |  1000.71 |
|     51 | 2024-09-19 15:27:41 | tochigi_mqtt_999 |       27.37 |    45.32 |  1000.47 |
|     52 | 2024-09-19 15:27:46 | tochigi_mqtt_999 |       27.38 |    45.22 |  1000.45 |
|     53 | 2024-09-19 15:27:51 | tochigi_mqtt_999 |        27.4 |    45.58 |  1000.49 |
|     54 | 2024-09-19 15:27:56 | tochigi_mqtt_999 |       27.43 |    45.97 |  1000.45 |
+--------+---------------------+------------------+-------------+----------+----------+
50 rows in set (0.001 sec)
```

#### 7.1.5 値による指定

数値の大小による指定でデータを取り出すことを考えます。次のクエリは、`temperature`の値が`23.0`以上のデータを5行取り出します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient WHERE temperature >= 23.0 LIMIT 5;
```

```sql
+--------+---------------------+-----------------+-------------+----------+----------+
| row_id | timestamp           | identifier      | temperature | humidity | pressure |
+--------+---------------------+-----------------+-------------+----------+----------+
|      2 | 2024-09-06 20:03:00 | tochigi_iot_999 |       27.26 |    49.66 |   998.24 |
|      3 | 2024-09-09 18:07:19 | tochigi_iot_999 |       25.98 |     43.8 |   1001.8 |
|      4 | 2024-09-09 18:16:37 | tochigi_iot_999 |       25.76 |    42.79 |  1001.83 |
|      5 | 2024-09-11 15:44:57 | tochigi_iot_999 |       25.77 |    53.02 |  1001.27 |
|      6 | 2024-09-11 15:45:07 | tochigi_iot_999 |        25.8 |     53.3 |  1001.21 |
+--------+---------------------+-----------------+-------------+----------+----------+
5 rows in set, 1 warning (0.001 sec)
```

次のクエリは、`temperature`の値が23.0以上かつ`humidity`の値が50.0以上のデータを5行取り出します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient WHERE temperature >= 23.0 AND humidity >= 50.0 LIMIT 5;
```

```sql
+--------+---------------------+-----------------+-------------+----------+----------+
| row_id | timestamp           | identifier      | temperature | humidity | pressure |
+--------+---------------------+-----------------+-------------+----------+----------+
|      5 | 2024-09-11 15:44:57 | tochigi_iot_999 |       25.77 |    53.02 |  1001.27 |
|      6 | 2024-09-11 15:45:07 | tochigi_iot_999 |        25.8 |     53.3 |  1001.21 |
|      7 | 2024-09-11 15:45:18 | tochigi_iot_999 |       25.79 |    52.32 |   1001.2 |
|      8 | 2024-09-11 15:45:28 | tochigi_iot_999 |       25.78 |    52.95 |  1001.23 |
|      9 | 2024-09-11 15:45:38 | tochigi_iot_999 |       25.79 |     52.7 |  1001.19 |
+--------+---------------------+-----------------+-------------+----------+----------+
5 rows in set, 1 warning (0.001 sec)
```

#### 7.1.6 平均値・最大値・最小値

選択する行を指定し、選択された行のなかで特定のカラムの平均値・最大値・最小値を求めることを考えます。関数 MAX()取り出された行の指定されたカラムの最大値を求めます。関数 MIN(), 関数 AVG()は、それぞれ最小値と平均値を求めます。

次のクエリは、`timestamp`のカラム(日付・時刻)を基準に、`2024年09月11日9:00:00`から`2024年09月11日16:00:00`までの間にノード`tochigi_iot_999`で取得した`temperature`データの最大値を求めます。

```sql
MariaDB [iot_storage]> SELECT MAX(temperature) FROM Ambient WHERE timestamp BETWEEN '2024-09-11 09:00:00' AND '2024-09-11 16:00:00' AND identifier = "tochigi_iot_999";
```

```sql
+------------------+
| MAX(temperature) |
+------------------+
|            25.91 |
+------------------+
1 row in set (0.001 sec)
```

次のクエリは、`timestamp`のカラム(日付・時刻)を基準に、`2024年09月19日9:00:00`から`2024年09月19日16:00:00`までの間にノード`tochigi_mqtt_999`で取得した`temperature`データの最大値を求めます。

```sql
MariaDB [iot_storage]> SELECT MAX(temperature) FROM Ambient WHERE timestamp BETWEEN '2024-09-19 09:00:00' AND '2024-09-19 16:00:00' AND identifier = "tochigi_mqtt_999";
```

```sql
+------------------+
| MAX(temperature) |
+------------------+
|            27.43 |
+------------------+
1 row in set (0.001 sec)
```

次のクエリは、`timestamp`のカラム(日付・時刻)を基準に、`2024年09月19日9:00:00`から`2024年09月19日16:00:00`までの間にノード`tochigi_mqtt_999`で取得した`humidity`データの平均を求めます。

```sql
MariaDB [iot_storage]> SELECT AVG(humidity) FROM Ambient WHERE timestamp BETWEEN '2024-09-19 9:00:00' AND '2024-09-19 16:00:00' AND identifier = "tochigi_mqtt_999";
```

```sql
+-------------------+
| AVG(humidity)     |
+-------------------+
| 41.00194444444444 |
+-------------------+
1 row in set, 1 warning (0.002 sec)
```

#### 7.1.7 １時間毎の平均値を集計

「１時間毎の平均」を求めることを考えます。下記のクエリは、`2024-09-19 00:00:00`以降の`temperature`、`humidity`、`pressure`データを１時間毎に集計し平均した値を古いデータから順に12行表示します。このように、ある一定の期間または値の範囲をまとめて集計するときには、`GROUP BY`を使用します。

```sql
MariaDB [iot_storage]> SELECT timestamp, AVG(temperature), AVG(humidity), AVG(pressure) FROM Ambient WHERE identifier = "tochigi_mqtt_999" AND timestamp >= "2024-09-19 00:00:00" GROUP BY CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp)) ORDER BY timestamp ASC LIMIT 12;
```

```sql
+---------------------+-------------------+-------------------+--------------------+
| timestamp           | AVG(temperature)  | AVG(humidity)     | AVG(pressure)      |
+---------------------+-------------------+-------------------+--------------------+
| 2024-09-19 14:59:51 |            27.395 |            40.655 |           1000.735 |
| 2024-09-19 15:00:01 | 27.36470588235294 | 41.02235294117647 | 1000.6914705882353 |
+---------------------+-------------------+-------------------+--------------------+
2 rows in set (0.001 sec)
```

`GROUP BY`の考え方について、次のクエリを実行し結果を確認してください。

```sql
MariaDB [iot_storage]> SELECT timestamp, temperature, CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp)) FROM Ambient WHERE identifier = "tochigi_mqtt_999" AND timestamp >= '2024-09-19 00:00:00' ORDER BY timestamp ASC;
```

このクエリの結果を下記に示します。句`CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp))`で示したカラムに注目してください。関数`CONCAT()`は、引数のデータを文字列として連結します。関数`YEAR()`は引数となった日付・日時の`年`の部分を取り出します。関数`MONTH()`,`DAY()`,`HOUR()`についても、引数となった日付・時刻のそれぞれ月・日・時の部分を取り出します。

このようにすると、`CONCAT(…)`の結果が１時間毎に同じ値になります。この結果を`GROUP BY`でまとめると、「１時間毎に」集計することが可能となります。

```sql
+---------------------+-------------+----------------------------------------------------------------------------+
| timestamp           | temperature | CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp)) |
+---------------------+-------------+----------------------------------------------------------------------------+
| 2024-09-19 14:59:51 |       27.39 | 202491914                                                                  |
| 2024-09-19 14:59:56 |        27.4 | 202491914                                                                  |
| 2024-09-19 15:00:01 |        27.4 | 202491915                                                                  |
| 2024-09-19 15:00:06 |       27.35 | 202491915                                                                  |
| 2024-09-19 15:00:11 |       27.36 | 202491915                                                                  |
| 2024-09-19 15:00:16 |       27.36 | 202491915                                                                  |
| 2024-09-19 15:00:21 |       27.36 | 202491915                                                                  |
| 2024-09-19 15:00:26 |       27.36 | 202491915                                                                  |
| 2024-09-19 15:00:31 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:00:36 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:00:41 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:00:46 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:00:51 |       27.38 | 202491915                                                                  |
| 2024-09-19 15:00:56 |       27.38 | 202491915                                                                  |
| 2024-09-19 15:01:01 |       27.34 | 202491915                                                                  |
| 2024-09-19 15:01:06 |       27.34 | 202491915                                                                  |
| 2024-09-19 15:01:11 |       27.35 | 202491915                                                                  |
| 2024-09-19 15:01:16 |       27.35 | 202491915                                                                  |
| 2024-09-19 15:01:21 |       27.33 | 202491915                                                                  |
| 2024-09-19 15:01:26 |       27.33 | 202491915                                                                  |
| 2024-09-19 15:01:31 |       27.34 | 202491915                                                                  |
| 2024-09-19 15:01:36 |       27.35 | 202491915                                                                  |
| 2024-09-19 15:01:41 |       27.35 | 202491915                                                                  |
| 2024-09-19 15:01:46 |       27.35 | 202491915                                                                  |
| 2024-09-19 15:01:51 |       27.36 | 202491915                                                                  |
| 2024-09-19 15:01:56 |       27.36 | 202491915                                                                  |
| 2024-09-19 15:02:01 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:02:06 |       27.38 | 202491915                                                                  |
| 2024-09-19 15:02:11 |       27.38 | 202491915                                                                  |
| 2024-09-19 15:02:16 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:02:21 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:02:26 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:27:41 |       27.37 | 202491915                                                                  |
| 2024-09-19 15:27:46 |       27.38 | 202491915                                                                  |
| 2024-09-19 15:27:51 |        27.4 | 202491915                                                                  |
| 2024-09-19 15:27:56 |       27.43 | 202491915                                                                  |
+---------------------+-------------+----------------------------------------------------------------------------+
36 rows in set (0.001 sec)
```

次のクエリは、`timestamp`のカラムを見やすくしたものです。

```sql
MariaDB [iot_storage]> SELECT CONCAT(YEAR(timestamp), "年", MONTH(timestamp), "月", DAY(timestamp), "日", HOUR(timestamp), "時") AS "日時", AVG(temperature) AS "１時間毎の平均気温[℃]" FROM Ambient WHERE identifier = "tochigi_mqtt_999" AND timestamp >= "2024-09-19 00:00:00" GROUP BY CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp)) ORDER BY timestamp ASC LIMIT 12;
```

各カラムの見出しは、`AS …`を用いて変更できます。

クエリの結果は次のようになります。

```sql
+-----------------------+----------------------------------+
| 日時                  | １時間毎の平均気温[℃]            |
+-----------------------+----------------------------------+
| 2024年9月19日14時     |                           27.395 |
| 2024年9月19日15時     |                27.36470588235294 |
+-----------------------+----------------------------------+
2 rows in set (0.001 sec)
```

### 7.2 集計したデータの表示

Pythonからクエリを実行し、MariaDB側で集計したデータをPythonで受け取り、表示するプログラムを考えます。

#### 7.2.1 単純なクエリの実行

「timestampのカラム(日付・時刻)を基準に、`2024年09月19日10:00:00`以降に取得したデータを5行取り出す」ことを考えます。SQLのクエリとその実行は下記のようになります。

```sql
MariaDB [iot_storage]> SELECT timestamp, identifier, temperature, humidity, pressure FROM Ambient WHERE timestamp > '2024-09-19 10:00:00' LIMIT 5;
```

```sql
+---------------------+------------------+-------------+----------+----------+
| timestamp           | identifier       | temperature | humidity | pressure |
+---------------------+------------------+-------------+----------+----------+
| 2024-09-19 14:59:51 | tochigi_mqtt_999 |       27.39 |    40.63 |  1000.71 |
| 2024-09-19 14:59:56 | tochigi_mqtt_999 |        27.4 |    40.68 |  1000.76 |
| 2024-09-19 15:00:01 | tochigi_mqtt_999 |        27.4 |    40.64 |  1000.75 |
| 2024-09-19 15:00:06 | tochigi_mqtt_999 |       27.35 |     40.7 |  1000.73 |
| 2024-09-19 15:00:11 | tochigi_mqtt_999 |       27.36 |    40.65 |  1000.75 |
+---------------------+------------------+-------------+----------+----------+
5 rows in set (0.001 sec)
```

このクエリをPythonから実行し、表示することを考えます。「4. MariaDBとPythonの連携」を参考に、テーブルの構造をこのテーブル(Ambient)に当てはめてプログラムを変更すると良いでしょう。

`bme280_select01.py`

```python
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
```

実行結果は次のようになります。

```bash
●実行するクエリ:  SELECT timestamp, identifier, temperature, humidity, pressure FROM Ambient WHERE timestamp > %s LIMIT %s;
timestamp                identifier              temperature     humidity        pressure
2024-09-19 14:59:51 ,    tochigi_mqtt_999 ,      27.39 ,         40.63 ,         1000.71
2024-09-19 14:59:56 ,    tochigi_mqtt_999 ,      27.4 ,          40.68 ,         1000.76
2024-09-19 15:00:01 ,    tochigi_mqtt_999 ,      27.4 ,          40.64 ,         1000.75
2024-09-19 15:00:06 ,    tochigi_mqtt_999 ,      27.35 ,         40.7 ,          1000.73
2024-09-19 15:00:11 ,    tochigi_mqtt_999 ,      27.36 ,         40.65 ,         1000.75
```

#### 7.2.2 プログラムの実行時に日付・時刻を指定する

表示を開始する日付と時刻をプログラムの実行時に指定することを考えます。キーボードからこれらの値を入力して、登録したデータの内容を閲覧するときの自由度を向上させます。

`bme280_select02.py`

```python
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

    #クエリのパラメータを入力
    #表示を開始する日付・時刻を入力する
    print('いつのデータから表示しますか？')
    s_year = input('年(例: 2024): ')
    s_month = input('月(例: 09): ')
    s_day = input('日(例: 19): ')
    s_hour = input('時(例: 10): ')
    datetime_start = f'{s_year}-{s_month}-{s_day} {s_hour}:00:00'
    print(f'{datetime_start}のデータからから何行のデータを表示しますか？')
 
    #入力したデータを数値に変換
    limit_count = int(input('数値を入力(例: 5) : '))

    #クエリのコマンド
    query = 'SELECT timestamp, identifier, temperature, humidity, pressure '\
            'FROM Ambient WHERE timestamp > %s LIMIT %s;'
    print('●実行するクエリ: ', query)
    sql_cursor.execute(query, (datetime_start, limit_count))

    print( 'timestamp       \t', 'identifier        \t', 'temperature   \t', 'humidity  \t', 'pressure')

    #クエリを実行した結果得られたデータを１行ずつ表示する
    for row in sql_cursor.fetchall():
        print(row[0], ', \t', row[1], ', \t', row[2], ', \t', row[3], ', \t', row[4])

main()
```

実行結果は次のようになります。

```bash
いつのデータから表示しますか？
年(例: 2024): 2024
月(例: 09): 09
日(例: 19): 19
時(例: 10): 10
2024-09-19 10:00:00のデータからから何行のデータを表示しますか？
数値を入力(例: 5) : 5
●実行するクエリ:  SELECT timestamp, identifier, temperature, humidity, pressure FROM Ambient WHERE timestamp > %s LIMIT %s;
timestamp                identifier              temperature     humidity        pressure
2024-09-19 14:59:51 ,    tochigi_mqtt_999 ,      27.39 ,         40.63 ,         1000.71
2024-09-19 14:59:56 ,    tochigi_mqtt_999 ,      27.4 ,          40.68 ,         1000.76
2024-09-19 15:00:01 ,    tochigi_mqtt_999 ,      27.4 ,          40.64 ,         1000.75
2024-09-19 15:00:06 ,    tochigi_mqtt_999 ,      27.35 ,         40.7 ,          1000.73
2024-09-19 15:00:11 ,    tochigi_mqtt_999 ,      27.36 ,         40.65 ,         1000.75
```

#### 7.2.3 １時間毎の集計値を表示する

「7.1.7 １時間毎の平均値を集計」のように、１時間毎に集計したデータを表示することを考えます。集計を開始する日付・時刻はキーボードから入力します。
クエリの結果得られた温度・湿度・気圧のデータは、pythonのround()関数を使って小数点第２位まで表示します。

`bme280_count_hour01.py`

```python
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
```

実行結果は次のようになります。

```bash
１時間ごとに平均したデータを表示します。
どのノードのデータを表示しますか？
ノードの Identifier(例: tochigi_mqtt_999): tochigi_mqtt_999
いつのデータから表示しますか？
年(例: 2024): 2024
月(例: 09): 09
日(例: 19): 19
時(例: 00): 00
2024-09-19 00:00:00のデータからから何行のデータを表示しますか？
数値を入力(例: 5) : 5
●実行するクエリ:  SELECT timestamp, identifier, AVG(temperature), AVG(humidity) , AVG(pressure) FROM Ambient WHERE identifier=%(target_id)s AND timestamp >= %(target_timestamp)s GROUP BY CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp)) ORDER BY timestamp ASC LIMIT %(target_limit_count)s; Data:  {'target_id': 'tochigi_mqtt_999', 'target_timestamp': '2024-09-19 00:00:00', 'target_limit_count': 5}
timestamp                identifier              temperature     humidity        pressure
●取得したデータを表示します
2024-09-19 14:59:51 ,    tochigi_mqtt_999 ,      27.39 ,         40.66 ,         1000.74
2024-09-19 15:00:01 ,    tochigi_mqtt_999 ,      27.36 ,         41.02 ,         1000.69
```

#### 7.2.4 モジュール化によるプログラムの整理

MariaDBに直接アクセスするコードを別のモジュールに分けて記述することで、機能の中核となるコードを見やすくすることを考えます。MariaDBに直接アクセスするプログラムを記述するモジュールを`db_ambient_count01.py`とします。

モジュール`db_ambient_count01.py`には、「指定された日時から１時間ごとに平均の気温・湿度・気圧をMariaDBにて集計し、その結果を得て辞書形式で渡す」メソッドを定義します。メソッドの引数には、開始する日時、ノードのIdentifier、開始する日時から何時間先のデータを取得するかを指定します。戻り値を辞書の配列として受け取ります。

`bme280_count_hour02.py`

```python
#coding: utf-8

#DB関連をまとめたモジュール
import db_ambient_count01

def main():
    #DBサーバに接続する
    db_ambient_count01.connect()

    #クエリのパラメータを入力
    #表示を開始する日付・時刻を入力する
    print('１時間ごとに平均したデータを表示します。')
    print('どのノードのデータを表示しますか？')
    node_id = input('ノードのIdentifier(例: tochigi_mqtt_999): ')

    print('いつのデータから表示しますか？')
    s_year = input('年(例: 2024): ')
    s_month = input('月(例: 09): ')
    s_day = input('日(例: 19): ')
    s_hour = input('時(例: 00): ')
    datetime_start = f'{s_year}-{s_month}-{s_day} {s_hour}:00:00'
    print(f'{datetime_start}のデータからから何行のデータを表示しますか？')

    #入力したデータを数値に変換
    limit_count = int(input('数値を入力(例: 5) : '))

    #クエリを実施して結果を得る
    result = db_ambient_count01.select_ave_one_hour(node_id, datetime_start, limit_count)

    #クエリの結果得られたデータを表示する
    print( 'timestamp       \t', 'identifier        \t', 'temperature   \t', 'humidity  \t', 'pressure')
    for data in result:
        print( data['timestamp'], ', \t', data['identifier'], ', \t', round(data['temperature'], 2), ', \t', round(data['humidity'], 2), ', \t', round(data['pressure'], 2))

main()
```

`db_ambient_count01.py`

```python
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
```

実行結果は次のようになります。

```bash
１時間ごとに平均したデータを表示します。
どのノードのデータを表示しますか？
ノードの Identifier(例: tochigi_mqtt_999): tochigi_mqtt_999
いつのデータから表示しますか？
年(例: 2024): 2024
月(例: 09): 09
日(例: 19): 19
時(例: 00): 00
2024-09-19 00:00:00のデータからから何行のデータを表示しますか？
数値を入力(例: 5) : 100
●実行するクエリ:  SELECT timestamp, identifier, AVG(temperature), AVG(humidity) , AVG(pressure) FROM Ambient WHERE identifier=%(target_id)s AND timestamp >= %(target_timestamp)s GROUP BY CONCAT(YEAR(timestamp), MONTH(timestamp), DAY(timestamp), HOUR(timestamp)) ORDER BY timestamp ASC LIMIT %(target_limit_count)s; Data:  {'target_id': 'tochigi_mqtt_999', 'target_timestamp': '2024-09-19 00:00:00', 'target_limit_count': 100}
timestamp                identifier              temperature     humidity        pressure
●取得したデータを表示します
2024-09-19 14:59:51 ,    tochigi_mqtt_999 ,      27.39 ,         40.66 ,         1000.74
2024-09-19 15:00:01 ,    tochigi_mqtt_999 ,      27.36 ,         41.02 ,         1000.69
2024-10-01 14:56:13 ,    tochigi_mqtt_999 ,      25.72 ,         57.19 ,         991.38
```
