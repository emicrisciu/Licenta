#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <BluetoothSerial.h>

#define RX_PIN 18  // Pinul 18 de pe ESP32 este pinul de recepție pentru interfața serială UART
#define TX_PIN 19  // Pinul 19 de pe ESP32 este pinul de transmisie pentru interfața serială UART

Adafruit_MPU6050 imu; // Declararea obiectului ce reprezintă unitatea de măsurare inerțială (IMU) MPU-6050
BluetoothSerial Serial_Bluetooth; // Declararea obiectului ce reprezintă conexiunea Bluetooth

sensors_event_t accelerometru, giroscop, temperatura; // Declararea obiectelor de tip eveniment ce vor stoca informațiile despre accelerația, rotația și temperatura măsurate de IMU

String mesaj_bluetooth = ""; // Variabilă globală ce va stoca mesajul ce va fi trimis prin Bluetooth către RaspberryPi

String proceseaza_date_UWB(String date) {
  /*
  Funcție ce procesează datele primite prin interfața serială UART de la eticheta UWB
  */

  // Se verifică dacă toate ancorele necesare trilaterației sunt funcționale
  int checkIndex2 = date.indexOf("DIST2:0x");
  int checkIndex3 = date.indexOf("DIST3:0x");
  if(checkIndex2 != -1 && checkIndex3 == -1)
  {
    return "ANCORA";
  }

  // Căutăm prefixul "POS:[" în linia curentă primită de la eticheta UWB
  int startIndex = date.indexOf("POS:[");
  if (startIndex == -1) return ""; // Nu am găsit șablonul, deci returnăm un mesaj gol

  int stopIndex = date.indexOf("]", startIndex);
  if (stopIndex == -1) return ""; // Nu am găsit închiderea șablonului, deci returnăm un mesaj gol

  // Extragem subșirul cu coordonatele, excluzând "POS:[" și "]" din mesajul identificat
  String coordonate = date.substring(startIndex + 5, stopIndex);
  
  // Separăm valorile pe baza virgulelor
  int primaVirgula = coordonate.indexOf(',');
  int aDouaVirgula = coordonate.indexOf(',', primaVirgula + 1);
  int aTreiaVirgula = coordonate.indexOf(',', aDouaVirgula + 1);

  // Dacă în șir nu există cele trei virgule, înseamnă că nu putem extrage cele patru valori de interes
  if (primaVirgula == -1 || aDouaVirgula == -1 || aTreiaVirgula == -1) return "";

  // Extragem coordonatele și factorul de calitate pe baza virgulelor din șir
  String x = coordonate.substring(0, primaVirgula);
  String y = coordonate.substring(primaVirgula + 1, aDouaVirgula);
  String z = coordonate.substring(aDouaVirgula + 1, aTreiaVirgula);
  String factor_calitate = coordonate.substring(aTreiaVirgula + 1);

  // Formăm și returnăm mesajul final: "T x y z factor_calitate"
  String mesaj = "T " + x + " " + y + " " + z + " " + factor_calitate;
  return mesaj;
}

void setup(void) {
  /*
  Funcție ce se execută la începutul programului o singură dată
  Inițializează și configurează componentele hardware și conexiunile
  */

  Serial_Bluetooth.begin("ESP32");  // Se inițializează conexiunea Bluetooth
  Serial2.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN); // Se inițialiează conexiunea prin interfața serială UART

  // Inițializarea senzorului IMU MPU-6050
  if (!imu.begin()) {
    Serial_Bluetooth.println("Nu a fost gasit senzorul IMU MPU-6050!");
    while (1) {
      delay(10);
    }
  }
  // Am setat pe +-8G intervalul de valori pentru accelerație deoarece aceasta poate avea valori destul de mari
  imu.setAccelerometerRange(MPU6050_RANGE_8_G);
  // Am setat pragul de frecvență pentru filtrul trece-jos la valoarea de 44Hz,
  // deoarece vrem să ignorăm zgomotele foarte puternice din exterior
  imu.setFilterBandwidth(MPU6050_BAND_44_HZ);

  delay(50);
}

void loop() {
  /*
  Funcție ce se execută ciclic, responsabilă cu implementarea funcționalității
  */

  // Se construiește mesajul ce va conține date despre coordonate de la eticheta UWB
  mesaj_bluetooth = "";
  while (Serial2.available()) {
    char caracterReceptionat = (char)Serial2.read();   // Se citește caracter cu caracter de pe UART
    mesaj_bluetooth += caracterReceptionat;
  }

  mesaj_bluetooth = proceseaza_date_UWB(mesaj_bluetooth); // Se aplică funcția de procesare peste mesajul recepționat prin UART
  Serial.println(mesaj_bluetooth); // Afișează mesajul pe serial pt debug (șterge)
  Serial_Bluetooth.println(mesaj_bluetooth); // Se trimite mesajul construit prin Bluetooth către RaspberryPi

  // Se citesc datele despre accelerație măsurate de senzorul IMU
  // Antetul funcției obligă existența a trei parametri, dar datele relevante în cazul meu sunt doar cele despre accelerație
  imu.getEvent(&accelerometru, &giroscop, &temperatura); 

  // Se construiește mesajul cu date despre accelerație provenite de la IMU
  mesaj_bluetooth = "MPU:";
  mesaj_bluetooth += accelerometru.acceleration.x;
  mesaj_bluetooth += ",";
  mesaj_bluetooth += accelerometru.acceleration.y;
  mesaj_bluetooth += ",";
  mesaj_bluetooth += accelerometru.acceleration.z;
  Serial_Bluetooth.println(mesaj_bluetooth); // Se trimite mesajul construit prin BLE către RaspberryPi

  delay(100); // Delay de 100ms între măsurători pentru a asigura sincronizarea cu eticheta UWB ce furnizează date la o frecvență de 10Hz
}