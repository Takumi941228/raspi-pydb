# Raspberry Piを活用したデータ処理とグラフ表示によるIoTシステム構築

## 課題

これまでの実習で、BME280及びRaspberryPiとBME280で取得した温度・湿度・気圧をMQTT経由で送信する」ことができました。また、「MQTTブローカからのデータをデータベースに追加する」ことができました。そして、蓄積したデータをグラフで表示することができました。

これまでに製作したプログラムを組み合わせて、以下の要素からなるシステムを製作してください。

* 自分のRaspberryPiをMQTTブローカとして、ESP32とRaspberryPiの二つに接続されたBME280で取得した温度・湿度・気圧をMQTT経由で送信する。

* 自分のRaspberryPiのMQTTブローカからのデータをデータベースにそれぞれ蓄積する。

* 蓄積したデータを使って、温度・湿度・気圧のグラフを２つずつリアルタイムに表示する。
