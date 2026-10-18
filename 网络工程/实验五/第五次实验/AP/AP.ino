#include "ESP8266WiFi.h"

const int RSSI_MAX = -50; // 定义最大信号强度(dBm)
const int RSSI_MIN = -100; // 定义最小信号强度(dBm)
const int displayEnc = 1; // 1：显示加密，0：不显示加密
const char* targetSSID = "REPLACE_WITH_YOUR_VALUE"; // 指定要监控的WiFi网络名称

void setup() {
  Serial.begin(115200);
  Serial.println("WiFi Signal Scan");
  // 将WiFi设置为站模式，并断开之前连接的AP
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(1000);
  Serial.println("Setup Done");
}

void loop() {
  Serial.println("WiFi Scan Started");
  // WiFi.scanNetworks将返回找到的网络数量
  int n = WiFi.scanNetworks();
  Serial.println("WiFi Scan Ended");
  if (n == 0) {
    Serial.println("No Networks Found");
  } else {
    Serial.print(n);
    Serial.println(" Networks Found");
    for (int i = 0; i < n; ++i) {
      // 检查是否是指定的SSID
      if (WiFi.SSID(i) == targetSSID) {
        // 打印指定网络的SSID和RSSI
        Serial.print("Found target network: ");
        Serial.print(WiFi.SSID(i));
        Serial.print("  channel: ");
        Serial.print(WiFi.channel(i));
        Serial.print("  RSSI: ");
        Serial.print(WiFi.RSSI(i));
        Serial.print(" dBm (");
        Serial.print(dBmtoPercentage(WiFi.RSSI(i)));
        Serial.print("% )");
        Serial.println("");
      }
      delay(5);
    }
  }
  Serial.println("");
  delay(5000);
  WiFi.scanDelete();
}

int dBmtoPercentage(int dBm) {
  int quality;
  if (dBm <= RSSI_MIN) {
    quality = 0;
  } else if (dBm >= RSSI_MAX) {
    quality = 100;
  } else {
    quality = 2 * (dBm + 100);
  }
  return quality;
}
