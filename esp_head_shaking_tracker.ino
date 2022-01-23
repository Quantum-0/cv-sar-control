#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>

#define WIFI_SSID "Insert Your Wi-Fi Network SSID here"
#define WIFI_PSK  "Insert Your Wi-Fi Password SSID here"
#define UDP_PORT 18782
#define threshold 150

WiFiUDP Udp;
char incomingPacket[256];

// Gyroscope ITG3200
#define GYRO 0x68 //  when AD0 is connected to GND ,gyro address is 0x68.
//#define GYRO 0x69   when AD0 is connected to VCC ,gyro address is 0x69  
#define G_SMPLRT_DIV 0x15
#define G_DLPF_FS 0x16
#define G_INT_CFG 0x17
#define G_PWR_MGM 0x3E
#define G_TO_READ 8 // 2 bytes for each axis x, y, z
// offsets are chip specific. 
int g_offx = 120-100;
int g_offy = 20-43;
int g_offz = 93-95;
int hx, hy, hz, turetemp;



////////// GYROSCOPE INITIALIZATION //////////
void initGyro()
{
 writeTo(GYRO, G_PWR_MGM, 0x00);
 writeTo(GYRO, G_SMPLRT_DIV, 0x07); // EB, 50, 80, 7F, DE, 23, 20, FF
 writeTo(GYRO, G_DLPF_FS, 0x1E); // +/- 2000 dgrs/sec, 1KHz, 1E, 19
 writeTo(GYRO, G_INT_CFG, 0x00);
}
void getGyroscopeData(int * result)
{
 int regAddress = 0x1B;
 int temp, x, y, z;
 byte buff[G_TO_READ];
 readFrom(GYRO, regAddress, G_TO_READ, buff); //read the gyro data from the ITG3200
 result[0] = ((buff[2] << 8) | buff[3]) + g_offx;
 result[1] = ((buff[4] << 8) | buff[5]) + g_offy;
 result[2] = ((buff[6] << 8) | buff[7]) + g_offz;
 result[3] = (buff[0] << 8) | buff[1]; // temperature
}

void setup() {
  Serial.begin(9600);
  delay(10);
  Serial.println("Hewwo");
  pinMode(D0, OUTPUT);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PSK);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    digitalWrite(D0, !digitalRead(D0));
  }
  Serial.println("Connected to wifi!");
  
  Wire.begin();
  initGyro();
}

int calib(int value)
{
  if (value > 32768)
    return value-65536;
  else
    return value;
}

// integrals
double shake_x = 0;
double shake_y = 0;
double shake_z = 0;
// sign
int last_x = 0;
int last_y = 0;
int last_z = 0;

// center
float center_x = 0;
float center_y = 0;
float center_z = 0;

void loop() {

  int gyro[4];
  getGyroscopeData(gyro);
  hx = calib(gyro[0]);
  hy = calib(gyro[1]);
  hz = calib(gyro[2]);

  hx = hx - center_x;
  center_x = 0.99 * center_x + 0.01 * hx;
  hy = hy - center_y;
  center_y = 0.99 * center_y + 0.01 * hy;
  hz = hz - center_z;
  center_z = 0.99 * center_z + 0.01 * hz;



  last_x = abs(hx) < threshold ? 0 : (hx > 0 ? 1 : -1);
  last_y = abs(hy) < threshold ? 0 : (hy > 0 ? 1 : -1);
  last_z = abs(hz) < threshold ? 0 : (hz > 0 ? 1 : -1);

  shake_x *= 0.92;
  shake_x += abs(hx);
  shake_y *= 0.92;
  shake_y += abs(hy);
  shake_z *= 0.92;
  shake_z += abs(hz);

  Serial.print(shake_x);
  Serial.print(',');
  Serial.print(shake_y);
  Serial.print(',');
  Serial.println(shake_z);
  double shake_max = max(shake_x, max(shake_y, shake_z));
  delay(100);

  if (shake_max > 5000) {
  IPAddress ipBroadcast(255, 255, 255, 255);
    String ReplyBuffer;
    if (shake_x == shake_max)
      ReplyBuffer = "{\"action\":\"shake\",\"axis\":\"X\"}";
    else if (shake_y == shake_max)
      ReplyBuffer = "{\"action\":\"shake\",\"axis\":\"Y\"}";
    else
      ReplyBuffer = "{\"action\":\"shake\",\"axis\":\"Z\"}";
    Udp.beginPacket(ipBroadcast, UDP_PORT);
    Udp.write(ReplyBuffer.c_str());
    // Serial.println(ReplyBuffer);
    Udp.endPacket();
    shake_x = 0;
    shake_y = 0;
    shake_z = 0;
    delay(1000);
  }
}

//////////// Transmission Functions: ///////////////

void writeTo(int DEVICE, byte address, byte val) {
  Wire.beginTransmission(DEVICE); //start transmission to ACC 
  Wire.write(address);        // send register address
  Wire.write(val);        // send value to write
  Wire.endTransmission(); //end transmission
}
//reads num bytes starting from address register on ACC in to buff array
 void readFrom(int DEVICE, byte address, int num, byte buff[]) {
 Wire.beginTransmission(DEVICE); //start transmission to ACC 
 Wire.write(address);        //sends address to read from
 Wire.endTransmission(); //end transmission
 
 Wire.beginTransmission(DEVICE); //start transmission to ACC
 Wire.requestFrom(DEVICE, num);    // request 6 bytes from ACC
 
 int i = 0;
 while(Wire.available())    //ACC may send less than requested (abnormal)
 { 
   buff[i] = Wire.read(); // receive a byte
   i++;
 }
 Wire.endTransmission(); //end transmission
}