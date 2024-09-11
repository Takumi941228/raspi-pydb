# Raspberry Piを活用したデータ処理とグラフの表示

## 5. データの継続的な取得と蓄積

MariaDB と Python を使って、データを継続的に蓄積するシステムを構築します。
本書では、温度・湿度・気圧センサである BME280 を使用してこれらのデータを取得し、蓄積することを考えます。

### 5.1 BME280の接続と使用

RaspberryPi に BME280 を接続します。BME280 は、I2C で接続します。

#### 5.1.1 配線

RaspberryPi と BME280 センサは、次のように配線します。BME280 側の SCK と SDI 端子は 10kΩの抵抗でプルアップします。下記の配線図と RaspberryPi ピン配置を参考に、配線してください。

#### 5.1.2 I2Cの確認

コマンド"i2cdetect"を使って、I2C バスに接続されている機器を一覧します。接続されている機器のアドレスが一覧されます。BME280 のアドレスは"76"なので、下記のように表示されます。

```bash
pi@raspberrypi:~ $ i2cdetect -y 1
```

```bash
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- 76 -- 
```

#### 5.1.3 ライブラリのインストール

I2C 通信を簡単に取扱うためのライブラリ"smbus2"をインストールします。

```bash
pi@raspberrypi:~ $ sudo apt -y install python3-smbus2
```

```bash
pi@raspberrypi:~ $ pip list | grep smbus2
```

### 5.2 データの取得

BME280 センサから I2C バス経由で温度・湿度・気圧データを読み込みます。Arduino でこのセンサを用いたときと同様に、このプログラムは非常に複雑になります。
下記で配布されているサンプルプログラムを参考にして、データの取得をおこないます。

[GitHub Switch Science](https://github.com/SWITCHSCIENCE/samplecodes/blob/master/BME280/Python27/bme280_sample.py)

プログラムは下記のとおりです。

```python
#coding: utf-8

#bme280_read01.py
#BME280から温湿度・気圧データを取得する

from smbus2 import SMBus
import time

bus_number = 1
i2c_address = 0x76

bus = SMBus(bus_number)

digT = []
digP = []
digH = []

t_fine = 0.0

def writeReg(reg_address, data):
    bus.write_byte_data(i2c_address,reg_address,data)

def get_calib_param():
    calib = []

    for i in range (0x88,0x88+24):
        calib.append(bus.read_byte_data(i2c_address,i))
    calib.append(bus.read_byte_data(i2c_address,0xA1))
    for i in range (0xE1,0xE1+7):
        calib.append(bus.read_byte_data(i2c_address,i))

    digT.append((calib[1] << 8) | calib[0])
    digT.append((calib[3] << 8) | calib[2])
    digT.append((calib[5] << 8) | calib[4])
    digP.append((calib[7] << 8) | calib[6])
    digP.append((calib[9] << 8) | calib[8])
    digP.append((calib[11]<< 8) | calib[10])
    digP.append((calib[13]<< 8) | calib[12])
    digP.append((calib[15]<< 8) | calib[14])
    digP.append((calib[17]<< 8) | calib[16])
    digP.append((calib[19]<< 8) | calib[18])
    digP.append((calib[21]<< 8) | calib[20])
    digP.append((calib[23]<< 8) | calib[22])
    digH.append( calib[24] )
    digH.append((calib[26]<< 8) | calib[25])
    digH.append( calib[27] )
    digH.append((calib[28]<< 4) | (0x0F & calib[29]))
    digH.append((calib[30]<< 4) | ((calib[29] >> 4) & 0x0F))
    digH.append( calib[31] )
    
    for i in range(1,2):
        if digT[i] & 0x8000: digT[i] = (-digT[i] ^ 0xFFFF) + 1

    for i in range(1,8):
        if digP[i] & 0x8000:
            digP[i] = (-digP[i] ^ 0xFFFF) + 1

    for i in range(0,6):
        if digH[i] & 0x8000:
            digH[i] = (-digH[i] ^ 0xFFFF) + 1


def readData():
    data = []
    for i in range (0xF7, 0xF7+8):
        data.append(bus.read_byte_data(i2c_address,i))
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    compensate_T(temp_raw)
    compensate_P(pres_raw)
    compensate_H(hum_raw)

def compensate_P(adc_P):
    global t_fine
    pressure = 0.0

    v1 = (t_fine / 2.0) - 64000.0
    v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * digP[5]
    v2 = v2 + ((v1 * digP[4]) * 2.0)
    v2 = (v2 / 4.0) + (digP[3] * 65536.0)
    v1 = (((digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + ((digP[1] * v1) / 2.0)) / 262144
    v1 = ((32768 + v1) * digP[0]) / 32768

    if v1 == 0:
        return 0
    pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125 
    if pressure < 0x80000000:
        pressure = (pressure * 2.0) / v1 
    else:
        pressure = (pressure / v1) * 2
    v1 = (digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
    v2 = ((pressure / 4.0) * digP[7]) / 8192.0
    pressure = pressure + ((v1 + v2 + digP[6]) / 16.0)
 
    print("pressure : %7.2f hPa" % (pressure/100))

def compensate_T(adc_T):
    global t_fine
    v1 = (adc_T / 16384.0 - digT[0] / 1024.0) * digT[1]
    v2 = (adc_T / 131072.0 - digT[0] / 8192.0) * (adc_T / 131072.0 - digT[0] / 8192.0) * digT[2] 
    t_fine = v1 + v2
    temperature = t_fine / 5120.0
    print("temp : %-6.2f ℃" % (temperature) )

def compensate_H(adc_H):
    global t_fine
    var_h = t_fine - 76800.0
    if var_h != 0:
        var_h = (adc_H - (digH[3] * 64.0 + digH[4]/16384.0 * var_h)) * (digH[1] / 65536.0 * (1.0 + digH[5] / 67108864.0 * var_h * (1.0 + digH[2] / 67108864.0 * var_h)))
    else:
        return 0
    var_h = var_h * (1.0 - digH[0] * var_h / 524288.0)
    if var_h > 100.0:
        var_h = 100.0 
    elif var_h < 0.0:
        var_h = 0.0
    print("hum : %6.2f ％" % (var_h))


def setup():
    osrs_t = 1   #Temperature oversampling x 1
    osrs_p = 1   #Pressure oversampling x 1
    osrs_h = 1   #Humidity oversampling x 1
    mode = 3     #Normal mode
    t_sb = 5     #Tstandby 1000ms
    filter = 0   #Filter off
    spi3w_en = 0 #3-wire SPI Disable

    ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg = osrs_h

    writeReg(0xF2,ctrl_hum_reg)
    writeReg(0xF4,ctrl_meas_reg)
    writeReg(0xF5,config_reg)

setup()
get_calib_param()

if __name__ == '__main__':
    try:
        readData()
    except KeyboardInterrupt:
        pass 
```

実行した結果を確認してみましょう。

```bash
temp : 29.15  ℃
pressure :  997.21 hPa
hum :  51.99 ％
```

### 5.3 継続的データの取得

#### 5.3.1 測定プログラムのモジュール化

測定したデータを様々なかたちで利用するプログラムを作っていきますが、測定する手順は殆ど変わりません。このため、測定をおこなうプログラムをモジュール化し、簡単に呼び出して利用することができるようにします。

作成したモジュールは、`impprt …`を利用して呼び出すことができます。

```python
#coding: utf-8

#bme280_read02.py
#モジュール化を行う

#モジュールをインポート
import bme280mod

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init() #BME280センサを初期化
    bme280mod.read_data() #測定

    data = bme280mod.get_data() #データを取得
    temp = data['temperature']
    hum = data['humidity'] 
    press = data['pressure']

    print(f'温度: {temp:.2f} ℃, 湿度: {hum:.2f} %, 気圧: {press:.2f} hPa')

main()
```

```python
#coding: utf-8

#bme280mod.py:BME280 を簡単に取扱うためのモジュール

from smbus2 import SMBus
import time

bus_number = 1
i2c_address = 0x76
bus = SMBus(bus_number)

digT = []
digP = []
digH = []

t_fine = 0.0

#温度・湿度・気圧データ
result_temp = -273.15
result_hum = 0.0
result_press= 0.0

def init(): #センサの初期化
    setup()
    get_calib_param()

def read_data(): #値の読み取り
    readData()

def get_data(): #読み取った値を辞書形式で返す
    return {'temperature': result_temp,
            'humidity': result_hum, 
            'pressure': result_press
           }
 
def writeReg(reg_address, data):
    bus.write_byte_data(i2c_address,reg_address,data)

def get_calib_param():
    calib = []

    for i in range (0x88,0x88+24): 
        calib.append(bus.read_byte_data(i2c_address,i))
    calib.append(bus.read_byte_data(i2c_address,0xA1))
    for i in range (0xE1,0xE1+7):
        calib.append(bus.read_byte_data(i2c_address,i))

    digT.append((calib[1] << 8) | calib[0])
    digT.append((calib[3] << 8) | calib[2])
    digT.append((calib[5] << 8) | calib[4])
    digP.append((calib[7] << 8) | calib[6])
    digP.append((calib[9] << 8) | calib[8])
    digP.append((calib[11]<< 8) | calib[10])
    digP.append((calib[13]<< 8) | calib[12])
    digP.append((calib[15]<< 8) | calib[14])
    digP.append((calib[17]<< 8) | calib[16])
    digP.append((calib[19]<< 8) | calib[18])
    digP.append((calib[21]<< 8) | calib[20])
    digP.append((calib[23]<< 8) | calib[22])
    digH.append( calib[24] )
    digH.append((calib[26]<< 8) | calib[25])
    digH.append( calib[27] )
    digH.append((calib[28]<< 4) | (0x0F & calib[29]))
    digH.append((calib[30]<< 4) | ((calib[29] >> 4) & 0x0F))
    digH.append( calib[31] )

    for i in range(1,2):
        if digT[i] & 0x8000:
            digT[i] = (-digT[i] ^ 0xFFFF) + 1

    for i in range(1,8):
        if digP[i] & 0x8000:
            digP[i] = (-digP[i] ^ 0xFFFF) + 1

    for i in range(0,6):
        if digH[i] & 0x8000:
            digH[i] = (-digH[i] ^ 0xFFFF) + 1

def readData():
    data = []
    for i in range (0xF7, 0xF7+8):
        data.append(bus.read_byte_data(i2c_address,i))
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    compensate_T(temp_raw)
    compensate_P(pres_raw)
    compensate_H(hum_raw)

def compensate_P(adc_P):
    global t_fine
    global result_press
    pressure = 0.0

    v1 = (t_fine / 2.0) - 64000.0
    v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * digP[5]
    v2 = v2 + ((v1 * digP[4]) * 2.0)
    v2 = (v2 / 4.0) + (digP[3] * 65536.0)
    v1 = (((digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + ((digP[1] * v1) / 2.0)) / 262144
    v1 = ((32768 + v1) * digP[0]) / 32768

    if v1 == 0:
        result_press = 0
        return 0
    pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125
    if pressure < 0x80000000:
        pressure = (pressure * 2.0) / v1
    else:
        pressure = (pressure / v1) * 2

    v1 = (digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
    v2 = ((pressure / 4.0) * digP[7]) / 8192.0
    pressure = pressure + ((v1 + v2 + digP[6]) / 16.0)

    #print("pressure : %7.2f hPa" % (pressure/100)) 
    result_press = pressure/100

def compensate_T(adc_T):
    global t_fine
    global result_temp
    v1 = (adc_T / 16384.0 - digT[0] / 1024.0) * digT[1]
    v2 = (adc_T / 131072.0 - digT[0] / 8192.0) * (adc_T / 131072.0 - digT[0] / 8192.0) * digT[2]
    t_fine = v1 + v2
    temperature = t_fine / 5120.0
    #print("temp : %-6.2f ℃" % (temperature) )
    result_temp = temperature

def compensate_H(adc_H):
    global t_fine
    global result_hum
    var_h = t_fine - 76800.0
    if var_h != 0:
        var_h = (adc_H - (digH[3] * 64.0 + digH[4]/16384.0 * var_h)) * (digH[1] / 65536.0 * (1.0 + digH[5] / 67108864.0 * var_h * (1.0 + digH[2] / 67108864.0 * var_h)))
    else:
        return 0
    var_h = var_h * (1.0 - digH[0] * var_h / 524288.0)
    if var_h > 100.0:
        var_h = 100.0
    elif var_h < 0.0:
        var_h = 0.0
    #print("hum : %6.2f ％" % (var_h))
    result_hum = var_h

def setup():
    osrs_t = 1   #Temperature oversampling x 1
    osrs_p = 1   #Pressure oversampling x 1
    osrs_h = 1   #Humidity oversampling x 1
    mode = 3     #Normal mode
    t_sb = 5     #Tstandby 1000ms
    filter = 0   #Filter off
    spi3w_en = 0 #3-wire SPI Disable

    ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg = osrs_h

    writeReg(0xF2,ctrl_hum_reg)
    writeReg(0xF4,ctrl_meas_reg)
    writeReg(0xF5,config_reg)
```

実行結果は次のようになります。

```bash
温度: 27.65 ℃, 湿度: 49.01 %, 気圧: 997.62 hPa
```

#### 5.3.2 継続的な測定

継続的に測定を行うプログラムを考えます。10 秒毎に測定を行いデータを表示するプログラムを作成します。

```python
#coding: utf-8

#モジュールをインポート
import bme280mod #BME280センサ関連を取扱う
import time      #時間を取扱う
import datetime  #日付と時刻を取扱う

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init() #BME280センサを初期化

    print('測定時間[YYYY-MM-DD HH:MM:SS], 温度[℃], 湿度[%], 気圧[hPa]')

    while True:
        bme280mod.read_data() #測定
        data = bme280mod.get_data() #データを取得

        temp = data['temperature']
        hum = data['humidity']
        press = data['pressure']

        datetime_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f'{datetime_now},    {temp:.2f},    {hum:.2f},    {press:.2f}')

        time.sleep(10)
main()
```

実行結果は次のようになります。

```bash
測定時間[YYYY-MM-DD HH:MM:SS], 温度[℃], 湿度[%], 気圧[hPa]
2024-09-06 20:03:00,    27.26,    49.66,    998.24
2024-09-06 20:03:10,    27.26,    49.73,    998.27
2024-09-06 20:03:20,    27.28,    49.84,    998.25
2024-09-06 20:03:30,    27.26,    50.04,    998.16
2024-09-06 20:03:40,    27.27,    50.13,    998.21
2024-09-06 20:03:50,    27.28,    50.29,    998.28
```

### 5.4 データの蓄積

MariaDB にデータを格納し、測定したデータを蓄積します。

#### 5.4.1 データベースとテーブルの設計

#### データベースの新規作成

いままではデータベース"practice"を使っていましたが、新たに別のデータベースを使用しましょう。新しいデータベースの名前は"iot_storage"とします。

| データベース名 | iot_storage |

データベースを作成します。mariadb に root ユーザとしてログインして作業します。

```bash
pi@raspberrypi:~ $ sudo mariadb -u root
```

MariaDB にログインしたら、データベースを作成します。

```sql
MariaDB [(none)]> CREATE DATABASE iot_storage CHARACTER SET utf8mb4;
Query OK, 1 row affected (0.001 sec)
```

データベースが作成されたか、確認をおこないます。

```sql
MariaDB [(none)]> SHOW DATABASEs;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| iot_storage        |
| mysql              |
| performance_schema |
| practice           |
| sys                |
+--------------------+
6 rows in set (0.001 sec)
```

データベースに対してアクセス権を付与します。`iot_admin`にはすべての操作権限を、`iot_user`は限られた操作権限を付与します。

```sql
MariaDB [(none)]> GRANT select, update, insert, delete ON iot_storage.* TO 'iot_user'@'localhost'; 
Query OK, 0 rows affected (0.572 sec)
```

```sql
MariaDB [(none)]> use iot_storage;
Database changed
```

#### データを蓄積するテーブルの設計

テーブルはどのような構造にするかを考えていきます。
まず、取扱うデータの項目を考えます。取扱うデータの項目は、少なくとも「温度」「湿度」「気圧」です。そのほかには、それらのデータを取得した「日付と時刻」が必要です。さらに、「どのノードが測定したのか」というデータも必要です。
主キーはこれらのデータの他に整数型の重複しない番号を割り当てることにします。

| テーブル名 | Ambient |
| --- | --- |

| 内容 | カラム名 | データ型 | 制約 |
| --- | --- | --- | --- |
| 主キー | row_id | INT | PRIMARY KEY NOT NULL AUTO_INCREMENT |
| 取得した日付と時刻 | timestamp | TIMESTAMP | ^ |
| 取得したノードの識別子 | identifier | CHAR(24) | ^ |
| 温度 | temperature | DOUBLE | ^ |
| 湿度 | humidity | DOUBLE | ^ |
| 気圧 | pressure | DOUBLE | ^ |

主キーは重複しない値を割り当てる必要があります。MariaDB には、INT 型(整数)の値を順番に割り当てる機能がありますので、これを利用します。
「取得したノードの識別子」は、一連の測定システムの中で、それを測定した機器を特定できる識別子である必要があります。例えば、MAC アドレスなどがあります。今回は"hyogo_iot_001"のような文字列とします。
「取得した日付と時刻」は、データを取得した日付と時刻を示します。データベース上で日付を扱うときには、タイムゾーン（時差）を考慮する必要があります。日本のタイムゾーンは"JST"と表され、協定世界時(UTC)より+9 時間進んだ時刻です。

MariaDB に設定されているタイムゾーンを確認するには、下記のコマンドを利用します。

```sql
MariaDB [iot_storage]> SELECT @@system_time_zone;
+--------------------+
| @@system_time_zone |
+--------------------+
| JST                |
+--------------------+
1 row in set (0.000 sec)
```

テーブルを作成します。

```sql
MariaDB [iot_storage]> CREATE TABLE Ambient(
    -> row_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    -> timestamp TIMESTAMP,
    -> identifier CHAR(17),
    -> temperature DOUBLE,
    -> humidity DOUBLE,
    -> pressure DOUBLE );
Query OK, 0 rows affected (0.498 sec)
```

作成したテーブルを確認します。

```sql
MariaDB [iot_storage]> SHOW TABLES;
+-----------------------+
| Tables_in_iot_storage |
+-----------------------+
| Ambient               |
+-----------------------+
1 row in set (0.001 sec)
```

テーブルの内容を確認します。

```sql
MariaDB [iot_storage]>  SHOW COLUMNS FROM Ambient;
+-------------+-----------+------+-----+---------+----------------+
| Field       | Type      | Null | Key | Default | Extra          |
+-------------+-----------+------+-----+---------+----------------+
| row_id      | int(11)   | NO   | PRI | NULL    | auto_increment |
| timestamp   | timestamp | YES  |     | NULL    |                |
| identifier  | char(17)  | YES  |     | NULL    |                |
| temperature | double    | YES  |     | NULL    |                |
| humidity    | double    | YES  |     | NULL    |                |
| pressure    | double    | YES  |     | NULL    |                |
+-------------+-----------+------+-----+---------+----------------+
6 rows in set (0.002 sec)
```

テーブルが作成できたら、一旦 MariaDB をログアウトして、より権限の低い`iot_user`でログインし直しましょう。テーブルの作成ができたのであれば、高い権限でログインしている必要はありません。

```sql
MariaDB [iot_storage]> exit
Bye```

```bash
pi@raspberrypi:~/python_sql $ sudo mariadb -u iot_user -p
```

```sql
MariaDB [(none)]> use iot_storage;
```

#### 5.4.2 データ追加のテスト

テーブルが作成できましたので、データ追加のテストを行います。まず最初に、登録されているデータを確認します。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient;
Empty set (0.001 sec)
```

データがまだ何も登録されていない場合は、`Empty set` と表示されます。

データをテスト追加するにあたって、以前作成した `bme280_cyclic01.py`で測定した実際の測定値を利用してみましょう。
プログラムを実行すると、次のように表示されます。

```bash
測定時間[YYYY-MM-DD HH:MM:SS], 温度[℃], 湿度[%], 気圧[hPa]
2024-09-06 20:03:00,    27.26,    49.66,    998.24
```

このデータを利用して、次のようにクエリを作成してみましょう。

```sql
INSERT INTO Ambient(timestamp, identifier, temperature, humidity, pressure) VALUES('2024-09-06 20:03:00', 'tochigi_iot_999', '27.26', '49.66', '998.24');
Query OK, 1 row affected (0.107 sec)
```

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient;
+--------+---------------------+-----------------+-------------+----------+----------+
| row_id | timestamp           | identifier      | temperature | humidity | pressure |
+--------+---------------------+-----------------+-------------+----------+----------+
|      2 | 2024-09-06 20:03:00 | tochigi_iot_999 |       27.26 |    49.66 |   998.24 |
+--------+---------------------+-----------------+-------------+----------+----------+
1 row in set (0.001 sec)
```

#### 5.4.3 プログラムからのデータ追加　その１

センサからのデータ測定が可能となり、データベースの準備もできています。測定したデータをデータベースに挿入するプログラムを考えていきます。
※センサからのデータの取得には、以前作成した`bme280mod.py`を使用します。

```python
#coding: utf-8

#モジュールをインポート
import bme280mod #BME280センサ関連を取扱う
import time      #時間を取扱う
import datetime  #日付と時刻を取扱う
import pymysql.cursors #PythonからDBを取扱う


#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_iot_999';

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init() #BME280センサを初期化

    print('測定日時[YYYY-MM-DD HH:MM:SS], 温度[℃], 湿度[%], 気圧[hPa]')

    bme280mod.read_data() #測定
    data = bme280mod.get_data() #データを取得

    #ディクショナリからデータを取得
    new_temp = round(data['temperature'], 2) #小数点以下2桁で丸め
    new_hum = round(data['humidity'], 2)
    new_press = round(data['pressure'], 2)

    new_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f'{new_timestamp}, {new_temp:.2f}, {new_hum:.2f}, {new_press:.2f}') #データベースの操作を行う
    #DB サーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user', #データベースにログインするユーザ名
        passwd='password', #データベースユーザのパスワード
        host='localhost', #接続先DBのホストorIPアドレス
        db='iot_storage'
    )

    #cursor オブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()
    print('●クエリの実行(データの挿入)')
    #クエリを指定する。実データは後から指定する。
    query1 = "INSERT INTO Ambient(timestamp, identifier, temperature, humidity, pressure) " \
             " VALUES(%s, %s, %s, %s, %s)";

    #クエリを実行する
    result1 = sql_cursor.execute(query1,(new_timestamp, NODE_IDENTIFIER, new_temp, new_hum, new_press))

    print('実行するクエリ: ' + query1)

    #クエリを実行した。変更した row の数が戻り値となる
    print('クエリを実行しました。('+ str(result1) +' row affected.)')

    #変更を実際に反映させる
    sql_connection.commit()

main()
```

```sql
測定日時[YYYY-MM-DD HH:MM:SS], 温度[℃], 湿度[%], 気圧[hPa]
2024-09-09 18:07:19, 25.98, 43.80, 1001.80
●クエリの実行(データの挿入)
実行するクエリ: INSERT INTO Ambient(timestamp, identifier, temperature, humidity, pressure)  VALUES(%s, %s, %s, %s, %s)
クエリを実行しました。(1 row affected.)
```

MariaDB にログインして、追加されたデータを確認してください。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient;
+--------+---------------------+-----------------+-------------+----------+----------+
| row_id | timestamp           | identifier      | temperature | humidity | pressure |
+--------+---------------------+-----------------+-------------+----------+----------+
|      2 | 2024-09-06 20:03:00 | tochigi_iot_999 |       27.26 |    49.66 |   998.24 |
|      3 | 2024-09-09 18:07:19 | tochigi_iot_999 |       25.98 |     43.8 |   1001.8 |
+--------+---------------------+-----------------+-------------+----------+----------+
2 rows in set (0.001 sec)
```

#### 5.4.4 プログラムからのデータ追加　その２

追加するデータを一つのディクショナリ形式にまとめたコードを考えてみます。

```python
#coding: utf-8

#モジュールをインポート
import bme280mod       #BME280センサ関連を取扱う
import time            #時間を取扱う
import datetime        #日付と時刻を取扱う
import pymysql.cursors #PythonからDBを取扱う


#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_iot_999';

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init() #BME280センサを初期化

    print('測定日時[YYYY-MM-DD HH:MM:SS], 温度[℃], 湿度[%], 気圧[hPa]')

    bme280mod.read_data() #測定
    data = bme280mod.get_data() #データを取得

    #ディクショナリからデータを取得
    new_temp = round(data['temperature'], 2) #小数点以下 2 桁で丸め
    new_hum = round(data['humidity'], 2)

    new_press = round(data['pressure'], 2)
    new_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")

    #DB に渡すための新しいディクショナリ形式にまとめる。
    new_row ={"timestamp" : new_timestamp, "identifier" : NODE_IDENTIFIER, "temperature": new_temp, "humidity": new_hum,"pressure": new_press};

    print(f'{new_timestamp}, {new_temp:.2f}, {new_hum:.2f}, {new_press:.2f}')

    #データベースの操作を行う------

    #DB サーバに接続する
    sql_connection = pymysql.connect(
        user='iot_user', #データベースにログインするユーザ名
        passwd='password',#データベースユーザのパスワード
        host='localhost', #接続先DBのホストorIPアドレス
        db='iot_storage'
    )

    #cursor オブジェクトのインスタンスを生成
    sql_cursor = sql_connection.cursor()
    print('●クエリの実行(データの挿入)')

    #クエリを指定する。実データは後から指定する。
    query1 = "INSERT INTO Ambient(timestamp, identifier, temperature, humidity, pressure) " \
            " VALUES(%(timestamp)s, %(identifier)s, %(temperature)s, %(humidity)s, %(pressure)s)";

    #クエリを実行する
    result1 = sql_cursor.execute(query1, new_row)
    
    print('実行するクエリ: ' + query1)

    #クエリを実行した。変更した row の数が戻り値となる
    print('クエリを実行しました。('+ str(result1) +' row affected.)')

    #変更を実際に反映させる
    sql_connection.commit()

main()
```

```bash
測定日時[YYYY-MM-DD HH:MM:SS], 温度[℃], 湿度[%], 気圧[hPa]
2024-09-09 18:16:37 , 25.76, 42.79, 1001.83
●クエリの実行(データの挿入)
実行するクエリ: INSERT INTO Ambient(timestamp, identifier, temperature, humidity, pressure)  VALUES(%(timestamp)s, %(identifier)s, %(temperature)s, %(humidity)s, %(pressure)s)
クエリを実行しました。(1 row affected.)
```

MariaDB にログインして、追加されたデータを確認してみましょう。

```sql
MariaDB [iot_storage]> SELECT * FROM Ambient;
+--------+---------------------+-----------------+-------------+----------+----------+
| row_id | timestamp           | identifier      | temperature | humidity | pressure |
+--------+---------------------+-----------------+-------------+----------+----------+
|      2 | 2024-09-06 20:03:00 | tochigi_iot_999 |       27.26 |    49.66 |   998.24 |
|      3 | 2024-09-09 18:07:19 | tochigi_iot_999 |       25.98 |     43.8 |   1001.8 |
|      4 | 2024-09-09 18:16:37 | tochigi_iot_999 |       25.76 |    42.79 |  1001.83 |
+--------+---------------------+-----------------+-------------+----------+----------+
3 rows in set (0.001 sec)
```

#### 5.4.5 継続的なデータの追加

継続的に測定し、データを追加するプログラムを考えてみます。

```python
#coding: utf-8

#モジュールをインポート
import bme280mod #BME280センサ関連を取扱う
import time      #時間を取扱う
import datetime  #日付と時刻を取扱う
import pymysql.cursors #PythonからDBを取扱う


#このノードを識別するID
NODE_IDENTIFIER = 'tochigi_iot_999';

#DBへの接続情報
DB_USER = 'iot_user'
DB_PASS = 'password'
DB_HOST = 'localhost'
DB_NAME = 'iot_storage'

def main():
    #モジュール内に定義されているメソッドを呼び出す
    bme280mod.init() #BME280センサを初期化

    #DBサーバに接続する
    sql_connection = pymysql.connect(
        user= DB_USER,  #データベースにログインするユーザ名
        passwd = DB_PASS, #データベースユーザのパスワード
        host = DB_HOST,   #接続先DBのホストorIPアドレス
        db = DB_NAME
    )

    print("Database connection established!");
    
    while True:
        bme280mod.read_data()       #測定
        data = bme280mod.get_data() #データを取得

        #ディクショナリからデータを取得
        new_temp = round(data['temperature'], 2) #小数点以下2桁で丸め
        new_hum = round(data['humidity'], 2)
        new_press = round(data['pressure'], 2)
        new_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #DBに渡すための新しいディクショナリ形式にまとめる。
        new_row = {"timestamp" : new_timestamp, "identifier" : NODE_IDENTIFIER, "temperature": new_temp, "humidity" :        new_hum, "pressure" : new_press};

        print(f'●NEW_DATA● TIMESTAMP: {new_timestamp}, TEMP: {new_temp:.2f}, HUMIDITY: {new_hum:.2f}, PRESSURE: {new_press:.2f}')

        #データベースの操作を行う------

        #cursorオブジェクトのインスタンスを生成
        sql_cursor = sql_connection.cursor()
        print('-- クエリの実行(データの挿入)')
        #クエリを指定する。実データは後から指定する。
        query1 = "INSERT INTO Ambient(timestamp, identifier, temperature, humidity, pressure) " \
                " VALUES(%(timestamp)s, %(identifier)s, %(temperature)s, %(humidity)s, %(pressure)s)";

        #クエリを実行する
        result1 = sql_cursor.execute(query1, new_row) print('実行するクエリ: ' + query1)
        #クエリを実行した。変更したrowの数が戻り値となる
        print('クエリを実行しました。('+ str(result1) +' row affected.)')

        #変更を実際に反映させる
        sql_connection.commit()

        time.sleep(10)
main()
```
