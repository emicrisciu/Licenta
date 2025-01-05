// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <BluetoothSerial.h>

Adafruit_MPU6050 mpu;
BluetoothSerial SerialBT;

const float accelThreshold = 15.0; // Adjust based on testing
const float gyroThreshold = 200.0; // Adjust based on testing
unsigned long impactStartTime = 0;
const unsigned long impactDuration = 50; // 50ms to confirm impact

// Variables for position, velocity, and time tracking
// float posX = 0, posY = 0, posZ = 0; // Position
// float velX = 0, velY = 0, velZ = 0; // Velocity
// unsigned long lastTime;
// float deltaTime;

// float pitch = 0.0;
// float roll = 0.0;
// float alpha = 0.98; // Complementary filter weight

// float driftThreshold = 0.1; // Adjust based on sensor noise level

void setup(void) {
  Serial.begin(115200);
  SerialBT.begin("ESP32");

  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("Adafruit MPU6050 test!");

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);  // am setat pe 2G range-ul pt a masura diferente mai discrete
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
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);  // la fel ca mai sus
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

  // /* Get new sensor events with the readings */
  // sensors_event_t a, g, temp;
  // mpu.getEvent(&a, &g, &temp);

  // /* Print out the values */
  // Serial.print("Acceleration X: ");
  // Serial.print(a.acceleration.x);
  // Serial.print(", Y: ");
  // Serial.print(a.acceleration.y);
  // Serial.print(", Z: ");
  // Serial.print(a.acceleration.z);
  // Serial.println(" m/s^2");

  // Serial.print("Rotation X: ");
  // Serial.print(g.gyro.x);
  // Serial.print(", Y: ");
  // Serial.print(g.gyro.y);
  // Serial.print(", Z: ");
  // Serial.print(g.gyro.z);
  // Serial.println(" rad/s");

  // Serial.print("Temperature: ");
  // Serial.print(temp.temperature);
  // Serial.println(" degC");

  // Serial.println("");
  // delay(250);




  // Get new sensor events with the readings
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

   // Calculate acceleration magnitude
  float accelMagnitude = sqrt(a.acceleration.x * a.acceleration.x +
                               a.acceleration.y * a.acceleration.y +
                               a.acceleration.z * a.acceleration.z);

  // Calculate gyro magnitude (optional)
  float gyroMagnitude = sqrt(g.gyro.x * g.gyro.x +
                              g.gyro.y * g.gyro.y +
                              g.gyro.z * g.gyro.z);

   // Detect impact
  float impactSignal = 0; // Default to 0 (no impact)
  if (accelMagnitude > accelThreshold || gyroMagnitude > gyroThreshold) {
    if (impactStartTime == 0) {
      impactStartTime = millis();
    } else if (millis() - impactStartTime > impactDuration) {
      //Serial.println("Confirmed Impact!");
      impactSignal = 100; // Assign a high value for visualization
      impactStartTime = 0; // Reset after detection
    }
  } else {
    impactStartTime = 0; // Reset if conditions aren't met
  }

  String output = "";
  while(Serial.available() > 0)
  {
    char receivedChar = (char)Serial.read();
    output += receivedChar;
  }

  Serial.println(output);
  SerialBT.print(output);

  // Print values with labels for Arduino Serial Plotter
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
  Serial.println(output);
  SerialBT.print(output);
  // Serial.print("MPU:");
  // Serial.print(a.acceleration.x);
  // Serial.print(",");
  // Serial.print(a.acceleration.y);
  // Serial.print(",");
  // Serial.print(a.acceleration.z);
  // Serial.print(",");
  // Serial.print(g.gyro.x);
  // Serial.print(",");
  // Serial.print(g.gyro.y);
  // Serial.print(",");
  // Serial.println(g.gyro.z);
  // Serial.print("Temp:"); Serial.println(temp.temperature);
  // Serial.print("Impact:"); Serial.println(impactSignal);

  delay(100); // Adjust delay as needed for smoother plotting
}