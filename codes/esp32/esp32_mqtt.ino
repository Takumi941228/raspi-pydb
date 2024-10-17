/* --------------------ヘッダファイルをインクルード-------------------- */
#include <ArduinoJson.h>
#include <SparkFunBME280.h>
#include <LCD_ST7032.h>
#include <Ticker.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <time.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

/* -------------------------定義分------------------------- */
/* wifi config */
/* 接続先wifiのSSIDとPASSを設定 */
#define WIFI_SSID "ssid"
#define WIFI_PASSWORD "password"

/* MQTT config */
#define MQTT_SERVER "MQTTブローカのIPアドレス"  //例:xx.xx.xx.xx
#define MQTT_PORT 1883
#define MQTT_BUFFER_SIZE 256
#define TOPIC "esp32/bme/00"
#define DEVICE_ID "esp001"  //デバイスIDは機器ごとにユニーク

/* PIN config */
#define SW1 25
#define SW2 33
#define SW3 32
#define R_LED 14
#define G_LED 27
#define Y_LED 26

/* -----------------------------インスタンス及び変数の作成------------------------------------ */
/* BME280用インスタンス作成 */
BME280 bme;
BME280_SensorMeasurements measurements;

/* ST7032用インスタンス作成 */
LCD_ST7032 lcd;

/* Ticker用インスタンス作成 */
Ticker tickerMeasure;

/* MQTT用インスタンス作成 */
//WiFiClientのクラスからこのプログラムで実際に利用するWiFiClientのオブジェクトをespClientとして作成
WiFiClient espClient;
//Clientからブローカへの通信を行うPublish、ブローカへデータの受信を要求するSubscribeの処理などの、MQTTの通信を行うためのPubsubClientのクラスから実際に処理を行うオブジェクトclientを作成
PubSubClient client(espClient);

/* MQTT Publish用変数 */
//JSONのオブジェクトを時間、温度、湿度、気圧用に4つの項目のため作成
const int message_capacity = JSON_OBJECT_SIZE(4);
//静的にJSONデータを生成するためにメモリを確保
StaticJsonDocument<message_capacity> json_message;
//JSONデータを格納する文字型配列のサイズを256に設定
char message_buffer[MQTT_BUFFER_SIZE];

/* NTPサーバ用インスタンス作成 */
WiFiUDP ntpUDP;                // UDP client
NTPClient timeClient(ntpUDP);  // NTP client

//表示モード用変数
unsigned int mode = 0;

/* ------------------------------各種関数定義------------------------ */
/* WiFiの設定及び接続 */
void WiFi_init(void) {
  //connect wifi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println(".");
    delay(100);
  }

  Serial.println("");
  Serial.print("Connected : ");
  Serial.println(WiFi.localIP());
  //sync Time
  configTime(3600L * 9, 0, "ntp.nict.jp", "ntp.jst.mfeed.ad.jp");
}

/* MQTTBrokerへの接続 */
void Mqtt_connect(void) {
  //サーバーへの接続を維持できるように、これを定期的に呼び出す必要がある
  client.loop();

  //MQTT未接続の場合は，再接続
  while (!client.connected()) {
    Serial.println("Mqtt Reconnecting");
    if (client.connect(DEVICE_ID)) {
      Serial.println("Mqtt Connected");
      break;
    }
  }
}

/* MQTTBrokerへのPublish */
void PublishSensorData(void) {
  //センサからデータの取得
  bme.readAllMeasurements(&measurements);

  //シリアルモニタに取得時間とセンサデータを表示
  Serial.println("Timestamp");
  Serial.println(timeClient.getFormattedTime());
  Serial.println("Humidity,Pressure,BME-Temp");
  Serial.print(measurements.humidity, 0);
  Serial.print(",");
  Serial.print(measurements.pressure / 100, 2);
  Serial.print(",");
  Serial.println(measurements.temperature, 2);

  /* ペイロードを作成して送信を行う．*/
  //JSONデータをクリア
  json_message.clear();

  //JSONの項目をキーと値を添えてJSONを作成
  json_message["timestamp"] = timeClient.getFormattedTime();
  json_message["humid"] = measurements.humidity;
  json_message["press"] = measurements.pressure / 100;
  json_message["temp"] = measurements.temperature;

  //json_messageの中のJSONデータをJSON形式の文字列message_bufferとしてシリアライズ化（文字列に変換）
  serializeJson(json_message, message_buffer, sizeof(message_buffer));

  //トピックをesp32/bmeして、JSON形式の文字列をパブリッシュする
  client.publish(TOPIC, message_buffer);
}

/* スイッチの状態確認 */
void Switch_check(void) {
  if (!digitalRead(SW1)) {
    lcd.clear();
    mode = 0;
    delay(50);
  }
  while (!digitalRead(SW1)) {
  }
  if (!digitalRead(SW2)) {
    lcd.clear();
    mode = 1;
    delay(50);
  }
  while (!digitalRead(SW2)) {
  }
  if (!digitalRead(SW3)) {
    lcd.clear();
    mode = 2;
    delay(50);
  }
  while (!digitalRead(SW3)) {
  }
}

/* setup関数 */
void setup() {
  Serial.begin(115200);

  Wire.begin();

  if (bme.beginI2C() == false)  //Begin communication over I2C
  {
    Serial.println("The sensor did not respond. Please check wiring.");
    while (1)
      ;  //Freeze
  }

  //WiFi接続
  WiFi_init();

  //インスタント化したオブジェクトclientの接続先のサーバを、アドレスとポート番号を設定
  client.setServer(MQTT_SERVER, MQTT_PORT);

  //5secごとにセンサデータを取得及びMQTTBrokerへPublish
  tickerMeasure.attach_ms(5000, PublishSensorData);

  //ST7032設定
  lcd.begin();
  lcd.setcontrast(20);

  //ntp設定
  timeClient.begin();               //init NTP
  timeClient.setTimeOffset(32400);  //0= GMT, 3600 = GMT+1, 32400 = GMT+9

  //PIN設定
  pinMode(SW1, INPUT_PULLUP);
  pinMode(SW2, INPUT_PULLUP);
  pinMode(SW3, INPUT_PULLUP);
  pinMode(R_LED, OUTPUT);
  pinMode(G_LED, OUTPUT);
  pinMode(Y_LED, OUTPUT);
}

/* loop関数 */
void loop() {
  Mqtt_connect();       //MQTTBrokerへの接続
  Switch_check();       //タクトSWの状態読取り
  timeClient.update();  //ntp更新

  switch (mode) {
    case 0:
      digitalWrite(R_LED, 1);
      digitalWrite(G_LED, 0);
      digitalWrite(Y_LED, 0);
      lcd.setCursor(0, 0);
      lcd.print("Temp");
      lcd.setCursor(1, 0);
      lcd.print(measurements.temperature);
      break;
    case 1:
      digitalWrite(R_LED, 0);
      digitalWrite(G_LED, 1);
      digitalWrite(Y_LED, 0);
      lcd.setCursor(0, 0);
      lcd.print("Humi");
      lcd.setCursor(1, 0);
      lcd.print(measurements.humidity);
      break;
    case 2:
      digitalWrite(R_LED, 0);
      digitalWrite(G_LED, 0);
      digitalWrite(Y_LED, 1);
      lcd.setCursor(0, 0);
      lcd.print("Press");
      lcd.setCursor(1, 0);
      lcd.print(measurements.pressure / 100);
      break;
    default:
      break;
  }
}