/* This Arduino code sends data to an MQTT broker every 30 seconds using mosquitto and MQTTX as the client.

Created By Embedotronics Technologies */

#include "DHT.h"
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define DHTPIN D2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

float humidityData;
float temperatureData;

// WiFi credentials
const char* ssid = "REPLACE_WITH_YOUR_VALUE";
const char* password = "REPLACE_WITH_YOUR_VALUE";

// MQTT broker information
const char* mqtt_server = "192.168.194.88"; // Replace with your broker address (e.g., mosquitto IP)
const int mqtt_port = 1883;                   // MQTT broker port
const char* mqtt_topic_humidity = "kaiqi/humidity";  // Topic for humidity
const char* mqtt_topic_temperature = "kaiqi/temperature"; // Topic for temperature

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  delay(10);
  dht.begin();

  // Connect to WiFi
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // Set MQTT server
  client.setServer(mqtt_server, mqtt_port);

  // Attempt to connect to MQTT broker
  reconnect();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {  // You can set a unique client ID
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  humidityData = dht.readHumidity();
  temperatureData = dht.readTemperature();

  // Check if sensor reading is valid
  if (isnan(humidityData) || isnan(temperatureData)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Humidity: ");
    Serial.print(humidityData);
    Serial.print(" %\t");
    Serial.print("Temperature: ");
    Serial.print(temperatureData);
    Serial.println(" *C");

    // Publish data to MQTT topics
    String humidityStr = String(humidityData);
    String temperatureStr = String(temperatureData);

    client.publish(mqtt_topic_humidity, humidityStr.c_str());
    client.publish(mqtt_topic_temperature, temperatureStr.c_str());
  }

  delay(30000); // Interval
}
