# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 2. 開発環境のインストールと設定

### 2.1 Raspberry Piの設定

#### 2.1.1 IPアドレスの設定

![IPAdress](../images/raspberry.PNG)

![IPAdress](../images/raspberry2.PNG)

#### 2.1.2 インターフェースの有効化

![IPAdress](../images/raspberry3.PNG)

![IPAdress](../images/raspberry4.PNG)

RaspberryPi のメニューより「RaspberryPi の設定」を開き、インターフェースのタブより"I2C" の項目を「有効」にして"OK"を押します。この設定で I2C が有効になります。

### 2.2 開発環境のインストール

#### 2.2.1 リモートデスクトップ(RealVNC)環境のインストール

![IPAdress](../images/vnc.PNG)

![IPAdress](../images/vnc2.PNG)

![IPAdress](../images/vnc3.PNG)

![IPAdress](../images/vnc4.PNG)

![IPAdress](../images/vnc5.PNG)

![IPAdress](../images/vnc6.PNG)

![IPAdress](../images/vnc7.PNG)

![IPAdress](../images/vnc8.PNG)

![IPAdress](../images/vnc9.PNG)

![IPAdress](../images/vnc10.PNG)

![IPAdress](../images/vnc11.PNG)

![IPAdress](../images/vnc12.PNG)

![IPAdress](../images/vnc13.PNG)

![IPAdress](../images/vnc14.PNG)

#### 2.2.2 VSCodeのインストール

![IPAdress](../images/vscode.PNG)

![IPAdress](../images/vscode2.PNG)

![IPAdress](../images/vscode3.PNG)

![IPAdress](../images/vscode4.PNG)

![IPAdress](../images/vscode5.PNG)

![IPAdress](../images/vscode6.PNG)

![IPAdress](../images/vscode7.PNG)

![IPAdress](../images/vscode8.PNG)

![IPAdress](../images/vscode9.PNG)

![IPAdress](../images/vscode10.PNG)

![IPAdress](../images/vscode11.PNG)

![IPAdress](../images/vscode12.PNG)

![IPAdress](../images/vscode13.PNG)

![IPAdress](../images/vscode14.PNG)

![IPAdress](../images/vscode15.PNG)

![IPAdress](../images/vscode16.PNG)

![IPAdress](../images/vscode17.PNG)

![IPAdress](../images/vscode18.PNG)

![IPAdress](../images/vscode19.PNG)




### 2.2 Pythonの開発環境

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

### 2.3 RaspberryPi の設定

