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