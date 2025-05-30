// #include <Adafruit_MPU6050.h>
// #include <Adafruit_Sensor.h>
// #include <Wire.h>
// #include <BluetoothSerial.h>

// Adafruit_MPU6050 mpu;
// BluetoothSerial SerialBT;

// #define RXD2 16  // GPIO16 pe ESP32 – primește date de la DWM1001
// #define TXD2 17  // GPIO17 – nu îl folosești acum, dar îl inițializăm

// const float accelThreshold = 15.0; // Pragul accelerației folosit la detectarea unui impact cu mingea
// const float gyroThreshold = 200.0; // Pragul rotației folosit la detectarea unui impact cu mingea
// unsigned long impactStartTime = 0;
// const unsigned long impactDuration = 50; // 50ms = timpul în care se confirmă impactul

// sensors_event_t a, g, temp;

// float impactSignal = 0;

// String output = "";

// void setup(void) {
//   Serial.begin(115200);
//   Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
//   SerialBT.begin("ESP32");

//   while (!Serial) delay(10); // Se așteaptă deschiderea conexiunii seriale

//   // Inițializarea IMU-ului
//   if (!mpu.begin()) {
//     Serial.println("Failed to find MPU6050 chip");
//     while (1) {
//       delay(10);
//     }
//   }

//   mpu.setAccelerometerRange(MPU6050_RANGE_2_G);  // Am setat pe 2G range-ul accelerației pentru a măsura diferențe mai discrete
  
//   mpu.setGyroRange(MPU6050_RANGE_250_DEG);  // La fel ca mai sus, am setat range-ul la valoarea minimă și pentru rotație

//   mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

//   delay(50);
// }

// void loop() {
//   // Se citesc evenimente înregistrate de senzor
//   mpu.getEvent(&a, &g, &temp);

//   // Se calculează magnitudinea (valoarea) accelerației
//   float accelMagnitude = sqrt(a.acceleration.x * a.acceleration.x +
//                                a.acceleration.y * a.acceleration.y +
//                                a.acceleration.z * a.acceleration.z);

//   // Se calculează magnitudinea rotației
//   float gyroMagnitude = sqrt(g.gyro.x * g.gyro.x +
//                               g.gyro.y * g.gyro.y +
//                               g.gyro.z * g.gyro.z);

//   // Detectarea impactului
//   impactSignal = 0; // 0 înseamnă că nu avem impact
//   if (accelMagnitude > accelThreshold || gyroMagnitude > gyroThreshold) {
//     if (impactStartTime == 0) {
//       impactStartTime = millis();
//     } else if (millis() - impactStartTime > impactDuration) {
//       //Serial.println("Confirmed Impact!");
//       impactSignal = 100; // Se atribuie o valoare mare semnalului pentru a putea fi observat mai ușor în grafice
//       impactStartTime = 0; // Resetăm după detecție
//     }
//   } else {
//     impactStartTime = 0; // Resetăm și dacă nu se îndeplinesc condițiile
//   }

//   // Se construiește mesajul ce va conține date de la tag-ul UWB, precum poziția în spațiu
//   output = "";
//   while(Serial2.available() > 0)
//   {
//     char receivedChar = (char)Serial2.read();
//     output += receivedChar;
//   }

//   SerialBT.print(output); // Se trimite mesajul construit prin BLE către RaspberryPi

//   // Se construiește mesajul cu date provenite de la IMU
//   output = "MPU:";
//   output += a.acceleration.x;
//   output += ",";
//   output += a.acceleration.y;
//   output += ",";
//   output += a.acceleration.z;
//   output += ",";
//   output += g.gyro.x;
//   output += ",";
//   output += g.gyro.y;
//   output += ",";
//   output += g.gyro.z;
//   SerialBT.print(output); // Se trimite mesajul construit prin BLE către RaspberryPi

//   delay(100); // Delay de 100ms între măsurători pentru a ne sincroniza cu restul senzorilor utilizați (ex: tag UWB)
// }



#define RXD2 18  // GPIO16 pe ESP32 – primește date de la DWM1001
#define TXD2 19  // GPIO17 – nu îl folosești acum, dar îl inițializăm

void setup() {
  Serial.begin(115200); // Pentru debug (pe USB)
  
  // Inițializezi Serial2 (RX de pe DWM, TX inutil momentan)
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);

  Serial.println("ESP32 gata să primească date de la DWM1001");
}

void loop() {
  while (Serial2.available()) {
    char c = Serial2.read();   // Citește un caracter de pe UART (de la DWM)
    Serial.print(c);           // Trimite-l spre consola serială (pentru debug)
  }
}
