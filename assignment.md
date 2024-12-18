# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 課題

これまでの実習で、「ESP32とBME280で取得した温度・湿度・気圧をMQTT経由で送信する」または「RaspberryPiとBME280で取得した温度・湿度・気圧をMQTT経由で送信する」ことができました。また、「MQTTブローカからのデータをデータベースに追加する」及び「蓄積されたデータをグラフによる可視化する」ことができました。

これまでに製作したプログラムを組み合わせて、以下の要素からなるシステムを製作してください。

### ハードウェアの課題

* 基板加工機と電子回路CADを用いて、ESP32が搭載された自作IoT基板を製作する。（回路は「6. MQTT経由のデータの取得と蓄積」を参照）

* 時間の都合上、取り下げします。~~ESP32に接続したBME280のデータをMQTTブローカへ送信するため、下図のような無線LAN環境を各自、構築する。~~
    * ESP32へのWiFi環境は、本実習で使用した設置済みのルータを使用してください。

        |WiFi|SSID|
        |---|---|
        |TP-Link|403-WiFi|

### ソフトウェアの課題

* ESP32のプログラムを変更する。
    * LCDの表示内容の変更
        * 常に１行目に現在時間を表示
        * ２行目に温度か湿度か気圧「タクトスイッチによる切り替え」を表示

        |行数|操作|内容|
        |---|---|---|
        |１行目|常に（SW押下中は、消えても良い）|時:分:秒|
        |２行目|黄SW押下|T:●●.●●|
        |２行目|緑SW押下|P:●●●●|
        |２行目|赤SW押下|H:●●.●●|

        * 黄SW押下、黄LEDが点灯、LCDに温度値を小数点第二位まで表示（例:「T:23.82」）
        * 緑SW押下、緑LEDが点灯、LCDに気圧値を整数のみ表示（例:「P:1013」100で割ったものをint型にキャスト変換する良い）
        * 赤SW押下、赤LEDが点灯、LCDに湿度値を小数点第二位まで表示（例:「H:29.76」）

    * 自分のRaspberryPiをMQTTブローカとして、ESP32に接続されたBME280で取得した温度・湿度・気圧と時間をTickerライブラリによるタイマ割り込みを用いて１０秒毎にMQTT経由で常に送信し続ける。
        * MQTTブローカアドレス:192.168.1xx.200
        * topic名:esp32/bme280
        * device名:esp32-1

* 課題用の新しいデータベースを作成する。
    * ユーザ名:sangi_自分の名前（例:sangi_Taro）
    * パスワード:Passw0rd
    * データベース名:sangi_storage
        * sangi_自分の名前に、以下の権限を付与する。

        |定義|内容|
        |---|---|
        |SELECT|参照|
        |INSERT|行の追加|
        |DELETE|行の削除|
        |UPDATE|値の変更|

    * テーブル名:Environment
        * カラム内容は以下の表に示す。

        | 内容 | カラム名 | データ型 | 制約 |
        | --- | --- | --- | --- |
        | 主キー | row_id | INT | PRIMARY KEY NOT NULL AUTO_INCREMENT |
        | 取得した日付と時刻 | timestamp | TIMESTAMP | - |
        | 取得したノードの識別子 | identifier | CHAR(24) | - |
        | 温度 | temperature | DOUBLE | - |
        | 湿度 | humidity | DOUBLE | - |
        | 気圧 | pressure | DOUBLE | - |

* 自分のRaspberryPiのMQTTブローカからのESP32のデータを受信し、識別ノードIDを付与して、新しく作成したデータベースに蓄積する。また、作成したPythonスクリプトは、継続的に蓄積させるため、常に実行し続けること。（「5. データの継続的な取得と蓄積」を参考）
    * 識別ノードID:sangi_mqtt_esp32

* 自分のRaspberryPiに接続されたBME280のデータを１０秒毎に、自分のRaspberryPiのMQTTブローカに送信する。
* 自分のRaspberryPiのMQTTブローカから受信したデータを新しく作成したデータベースに蓄積する。また、作成したPythonスクリプトは、継続的に蓄積させるため、常に実行し続けること。（「9. MQTTブローカを経由した測定データの蓄積」を参考）
    * 識別ノードID:sangi_mqtt_raspi
    * topic名:raspi/bme280

* 蓄積したデータを使って、キー入力によるサンプル数及び更新周期の設定後、温度・湿度・気圧の３つのグラフをリアルタイムに表示する。（「8. グラフによるデータの可視化」を参考）
    * パターン１
        * １行３列の形式で、温度・湿度・気圧の順で表示するようにする。
        * 以下のターミナルのように識別ノードIDをキー入力による選択で、グラフに表示するデータがESP32またはRaspberryPiに接続されたBME280のデータを切り替えれること。

        ```bash
        最新のデータをリアルタイムに表示します。
        どのノードのデータを表示しますか？
        ノードの Identifier(例: sangi_mqtt_esp32): sangi_mqtt_raspi
        何サンプル前のデータまで表示しますか？
        数値を入力(例: 20) : 20
        グラフの更新周期(秒)は？
        数値を入力(例: 10) : 10
        ```

        * 実行したグラフの例

        ![Figure](./images/pattern1.PNG)

    * パターン２
        * ESP32及びRaspberryPiに接続されたBME280のデータを２行３列の形式で、それぞれ温度・湿度・気圧の順で表示するようにする。

        ```bash
        最新のデータをリアルタイムに表示します。
        何サンプル前のデータまで表示しますか？
        数値を入力(例: 20) : 20
        グラフの更新周期(秒)は？
        数値を入力(例: 10) : 10
        ```

        * 実行したグラフの例

        ![Figure](./images/pattern2.PNG)

        * 文字が重なる場合の対処法

        グラフタイトルやラベル等の文字が重なって表示されてしまう場合、以下のコードを`While True`構文の中に表記し、更新する毎に、レイアウトを変更すると良い。

        ```python
        plt.tight_layout() #文字が重ならないようなレイアウトにする
        ```
