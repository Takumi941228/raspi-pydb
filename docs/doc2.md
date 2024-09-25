# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 2. 開発環境のインストールと設定

### 2.1 Raspberry Piの設定

#### 2.1.1 初期設定

* Next

![SetUP](../images/setup.JPG)

* Country
    * Japan
* Language
    * Japanese
* Timezone
    * Tokyo
* Next

![SetUP](../images/setup2.JPG)

* Enter username
    * pi
* Enter password
    * 任意
* Confirm password
    * 上記同様
* Next

![SetUP](../images/setup3.JPG)

* OK

![SetUP](../images/setup4.JPG)

* 接続先SSIDをクリック
* Next

![SetUP](../images/setup5.JPG)

* password
    * 任意
* Next

![SetUP](../images/setup6.JPG)

* Next

![SetUP](../images/setup7.JPG)

* Next

![SetUP](../images/setup8.JPG)

* Skip

![SetUP](../images/setup9.JPG)

* OK

![SetUP](../images/setup10.JPG)

* Restart

![SetUP](../images/setup11.JPG)

#### 2.1.1 IPアドレスの設定

別端末からSSH接続によるリモートアクセスができるように、Raspberry PiのIPアドレス等を手動で設定します。

接続するSSIDを選択し、パスワードを入力後、`高度なオプション`から、タブ`IPv4設定`でIPアドレス及びDNSサーバーを設定します。

![IPAdress](../images/raspberry5.PNG)

![IPAdress](../images/raspberry6.PNG)

![IPAdress](../images/raspberry2.PNG)

保存後、Raspberry Piの再起動させます。

```bash
pi@raspberrypi:~ $ sudo reboot
```

設定したIPアドレスが反省されているかを確認します。

```bash
pi@raspberrypi:~ $ ifconfig
```

![IPAdress](../images/raspberry7.PNG)

#### 2.1.2 インターフェースの有効化

RaspberryPi のメニューより「RaspberryPi の設定」を開き、インターフェースのタブより`SSH`、`VNC`、`SPI`、`I2C` の項目を「有効」にして"OK"を押します。この設定でインターフェースが有効になります。

![IPAdress](../images/raspberry3.PNG)

![IPAdress](../images/raspberry4.PNG)

### 2.2 開発環境のインストール

#### 2.2.1 リモートデスクトップ(RealVNC)環境のインストール

* ダブルクリック

![IPAdress](../images/vnc.PNG)

* OK

![IPAdress](../images/vnc2.PNG)

* Next

![IPAdress](../images/vnc3.PNG)

* チェックを入れる
    * Next

![IPAdress](../images/vnc4.PNG)

* Next

![IPAdress](../images/vnc5.PNG)

* Install

![IPAdress](../images/vnc6.PNG)

* Finish

![IPAdress](../images/vnc7.PNG)

* チェックを外す
    * ~~Sign in to get started~~
    * Use RealVNC Viewer without signing in

![IPAdress](../images/vnc8.PNG)

* ~~Cancel~~

![IPAdress](../images/vnc9.PNG)

* タブからRaspberry PiのIPアドレスを記入
    * Enterキー

![IPAdress](../images/vnc10.PNG)

* Continue

![IPAdress](../images/vnc11.PNG)

* チェックを入れる
    * UsernameとPasswordを記入
        * OK

![IPAdress](../images/vnc12.PNG)

* OK

![IPAdress](../images/vnc13.PNG)

* 接続完了

![IPAdress](../images/vnc14.PNG)

#### 2.2.2 VSCodeのインストール

* ダブルクリック

![IPAdress](../images/vscode.PNG)

* 同意する
    * 次へ

![IPAdress](../images/vscode2.PNG)

* 次へ

![IPAdress](../images/vscode3.PNG)

* チェックを外す
    * 次へ

![IPAdress](../images/vscode4.PNG)

* チェックを入れる
    * 次へ

![IPAdress](../images/vscode5.PNG)

* インストール

![IPAdress](../images/vscode6.PNG)

* 待つ

![IPAdress](../images/vscode7.PNG)

* ~~チェックを外す~~
* 完了

![IPAdress](../images/vscode8.PNG)

* 起動

![IPAdress](../images/vscode9.PNG)

* サイドバー`拡張機能`
    * `japanese`と検索
        * 一番上をクリック

![IPAdress](../images/vscode10.PNG)

* Install

![IPAdress](../images/vscode11.PNG)

* Change Language and Restart

![IPAdress](../images/vscode12.PNG)

* サイドバー`拡張機能`
    * `remote dev`と検索
        * 一番上をクリック
            * インストール

![IPAdress](../images/vscode13.PNG)

* サイドバー`リモートエクスプローラ`
    * SSH > `歯車`
        * C:~/.ssh/config

![IPAdress](../images/vscode14.PNG)

* Host `Raspberrypi`
    * HostName `Raspberry PiのIPアドレス`
        * User `Pi`
            * Enterキー

![IPAdress](../images/vscode15.PNG)

* Linux

![IPAdress](../images/vscode16.PNG)

* Raspberry PiのIPアドレス
    * Enterキー

![IPAdress](../images/vscode17.PNG)

* 完了

![IPAdress](../images/vscode18.PNG)

### 2.3 Pythonの開発環境

~~まず、aptパッケージのアップデートをします。~~

~~pi@raspberrypi:~ $ sudo apt update~~

~~pi@raspberrypi:~ $ sudo apt -y upgrade~~

- インストールにかなり時間がかかってしまうので、割愛します。

本実習では、開発環境として`Python3.11`を利用します。
下記のコマンドで、既にインストールされているPythonのバージョンを確認することができます。

```bash
pi@raspberrypi:~ $ python -V
Python 3.11.2
```

Python で MySQL を取扱うことができるように、ライブラリをインストールします。

```bash
pi@raspberrypi:~ $ sudo apt -y install python3-pymysql
```

### 2.4 MariaDB(MySQL)Serverの環境構築

下記のコマンドで`MariaDB Server`をインストールします。

```bash
pi@raspberrypi:~ $ sudo apt -y install mariadb-server
```
