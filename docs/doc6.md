# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 6. MQTT経由のデータの取得と蓄積

データの取得に使用するプロトコルであるMQTT通信を行うため、`mosquito`をインストールします。

```bash
pi@raspberrypi:~/python_sql $ sudo apt -y install mosquitto
```

```bash
pi@raspberrypi:~/python_sql $ sudo systemctl status mosquitto.service
```

```bash
● mosquitto.service - Mosquitto MQTT Broker
     Loaded: loaded (/lib/systemd/system/mosquitto.service; enabled; preset: enabled)
     Active: active (running) since Wed 2024-09-11 16:16:30 JST; 1min 2s ago
       Docs: man:mosquitto.conf(5)
             man:mosquitto(8)
    Process: 6633 ExecStartPre=/bin/mkdir -m 740 -p /var/log/mosquitto (code=exited, status=0/SUCCESS)
    Process: 6641 ExecStartPre=/bin/chown mosquitto /var/log/mosquitto (code=exited, status=0/SUCCESS)
    Process: 6642 ExecStartPre=/bin/mkdir -m 740 -p /run/mosquitto (code=exited, status=0/SUCCESS)
    Process: 6643 ExecStartPre=/bin/chown mosquitto /run/mosquitto (code=exited, status=0/SUCCESS)
   Main PID: 6644 (mosquitto)
      Tasks: 1 (limit: 3910)
        CPU: 50ms
     CGroup: /system.slice/mosquitto.service
             └─6644 /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf

 9月 11 16:16:30 raspberrypi systemd[1]: Starting mosquitto.service - Mosquitto MQTT Broker...
 9月 11 16:16:30 raspberrypi systemd[1]: Started mosquitto.service - Mosquitto MQTT Broker.
```

### 6.1 Mosquittoクライアントからのデータ取得

#### 6.1.1 サブスクライバーの操作

* ターミナル１

```bash
pi@raspberrypi:~/python_sql $ sudo apt -y install mosquitto-clients
```

MQTTブローカに接続して、データを取得します。コマンドを入力し、MQTTサブスクライバを起動します。コマンドの書式は、次のとおりです。

<code>mosquitto_sub  -d -h 接続先サーバ -p ポート番号 -t トピック名</code>

それぞれのパラメータの意味と設定値は次のとおりです。

| パラメータ | 意味 | 設定例 |
| --- | --- | --- |
| -h | サーバ名 | -h 

```bash
pi@raspberrypi:~/python_sql $ mosquitto_sub -d -t test
```

```bash
Client (null) sending CONNECT
Client (null) received CONNACK (0)
Client (null) sending SUBSCRIBE (Mid: 1, Topic: test, QoS: 0, Options: 0x00)
Client (null) received SUBACK
Subscribed (mid: 1): 0
```

* ターミナル２

```bash
pi@raspberrypi:~/python_sql $ mosquitto_pub -d -t test -m "Hello MQTT!"
```

```bash
Client (null) sending CONNECT
Client (null) received CONNACK (0)
Client (null) sending PUBLISH (d0, q0, r0, m1, 'test', ... (11 bytes))
Client (null) sending DISCONNECT
```

* ターミナル１

```bash
Hello MQTT!
```

