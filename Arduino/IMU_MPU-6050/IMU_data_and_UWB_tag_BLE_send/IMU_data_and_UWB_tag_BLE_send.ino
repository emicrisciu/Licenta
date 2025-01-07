#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <BluetoothSerial.h>

Adafruit_MPU6050 mpu;
BluetoothSerial SerialBT;

const float accelThreshold = 15.0; // Pragul accelerației folosit la detectarea unui impact cu mingea
const float gyroThreshold = 200.0; // Pragul rotației folosit la detectarea unui impact cu mingea
unsigned long impactStartTime = 0;
const unsigned long impactDuration = 50; // 50ms = timpul în care se confirmă impactul

void setup(void) {
  Serial.begin(115200);
  SerialBT.begin("ESP32");

  while (!Serial)
    delay(10); // Se așteaptă deschiderea conexiunii seriale

  Serial.println("Adafruit MPU6050 test!");

  // Inițializarea IMU-ului
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);  // Am setat pe 2G range-ul accelerației pentru a măsura diferențe mai discrete
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);  // La fel ca mai sus, am setat range-ul la valoarea minimă și pentru rotație
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }

  Serial.println("");
  delay(100);
}

void loop() {
  // Se citesc evenimente înregistrate de senzor
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

   // Se calculează magnitudinea (valoarea) accelerației
  float accelMagnitude = sqrt(a.acceleration.x * a.acceleration.x +
                               a.acceleration.y * a.acceleration.y +
                               a.acceleration.z * a.acceleration.z);

  // Se calculează magnitudinea rotației
  float gyroMagnitude = sqrt(g.gyro.x * g.gyro.x +
                              g.gyro.y * g.gyro.y +
                              g.gyro.z * g.gyro.z);

  // Detectarea impactului
  float impactSignal = 0; // 0 înseamnă că nu avem impact
  if (accelMagnitude > accelThreshold || gyroMagnitude > gyroThreshold) {
    if (impactStartTime == 0) {
      impactStartTime = millis();
    } else if (millis() - impactStartTime > impactDuration) {
      //Serial.println("Confirmed Impact!");
      impactSignal = 100; // Se atribuie o valoare mare semnalului pentru a putea fi observat mai ușor în grafice
      impactStartTime = 0; // Resetăm după detecție
    }
  } else {
    impactStartTime = 0; // Resetăm și dacă nu se îndeplinesc condițiile
  }

  // Se construiește mesajul ce va conține date de la tag-ul UWB, precum poziția în spațiu
  String output = "";
  while(Serial.available() > 0)
  {
    char receivedChar = (char)Serial.read();
    output += receivedChar;
  }

  Serial.println(output); // Se afișează pe serial monitor pentru a verifica corectitudinea
  SerialBT.print(output); // Se trimite mesajul construit prin BLE către RaspberryPi

  // Se construiește mesajul cu date provenite de la IMU
  output = "MPU:";
  output += a.acceleration.x;
  output += ",";
  output += a.acceleration.y;
  output += ",";
  output += a.acceleration.z;
  output += ",";
  output += g.gyro.x;
  output += ",";
  output += g.gyro.y;
  output += ",";
  output += g.gyro.z;
  Serial.println(output); // Se afișează pe serial monitor pentru a verifica corectitudinea
  SerialBT.print(output); // Se trimite mesajul construit prin BLE către RaspberryPi

  delay(100); // Delay de 100ms între măsurători pentru a ne sincroniza cu restul senzorilor utilizați (ex: tag UWB)
}