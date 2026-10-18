#include <SoftwareSerial.h>
#include "DEV_Config.h"
#include "L76X.h"
GNRMC GPS1;


void setup()
{
 Serial.begin(9600);
DEV_Set_Baudrate(115200);
L76X_Send_Command(SET_NMEA_OUTPUT);
L76X_Send_Command(SET_NMEA_BAUDRATE_9600);
DEV_Delay_ms(500);

L76X_Send_Command(9600);
DEV_Set_Baudrate(9600);
DEV_Delay_ms(500);
L76X_Send_Command(SET_NMEA_OUTPUT);
}

void loop() // run over and over
{  
  GPS1 = L76X_Gat_GNRMC();
  Serial.print("\r\n");
  Serial.print("Time:");
  Serial.print(GPS1.Time_H);
  Serial.print(":");
  Serial.print(GPS1.Time_M); 
  Serial.print(":");
  Serial.print(GPS1.Time_S);
  Serial.print("\r\n");
}

