#include <Servo.h>

Servo myservo;   // serwo Y
Servo servo2;    // serwo X

const int VRX = A1;
const int VRY = A0;
const int SW  = 8;

int Xpos = 90;
int Ypos = 90;
int XposAK = 90;
int YposAK = 90;

int offsetX = 0;     // trwała korekta z joysticka
int offsetY = 0;

int personX = -1;
int personY = -1;

void setup() {
  Serial.begin(115200);
  pinMode(SW, INPUT_PULLUP);
  
  myservo.attach(7);   // Y
  servo2.attach(2);    // X
  
  myservo.write(Ypos); 
  servo2.write(Xpos);
}
void loop() {
  // ---- Odbiór danych z seriala ----
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    // Jeżeli linia pusta lub źle sformatowana, ignoruj
    if (line.length() == 0) return;

    int commaIndex = line.indexOf(',');
    if (commaIndex > 0) {
      personX = line.substring(0, commaIndex).toInt();
      personY = line.substring(commaIndex + 1).toInt();

      // Czyszczenie nadmiarowych danych w buforze
      while (Serial.available() > 0) {
        Serial.read(); // odczytaj i odrzuć
      }

      // Mapowanie na zakres serw 0-180
      Xpos = map(personX, 0, 1920, 0, 180);
      Ypos = map(personY, 0, 1080, 0, 180);

      // ograniczenie zakresu
      Xpos = constrain(Xpos, 0, 180);
      Ypos = constrain(Ypos, 0, 180);
    }
  }
  int joyX = analogRead(VRX);
  int joyY = analogRead(VRY);
  int dx = joyX - 512;
  int dy = joyY - 512;
  
  if (dx > 100) offsetX += 1;
  if (dx < -100) offsetX -= 1;
  if (dy > 100) offsetY -= 1;
  if (dy < -100) offsetY += 1;
  offsetX = constrain(offsetX, -120, 120);
  offsetY = constrain(offsetY, -120, 120);

  
  // ---- Płynny ruch serw ----
  if (XposAK+10 < Xpos) XposAK += 1;
  else if (XposAK-10 > Xpos) XposAK -= 1;

  if (YposAK+10 < Ypos) YposAK += 1;
  else if (YposAK-10 > Ypos) YposAK -= 1;

  myservo.write(YposAK - offsetY);
  servo2.write(XposAK + offsetX);

  // ---- Opcjonalny reset joystickiem ----
  if (!digitalRead(SW)) {
    Xpos = 90;
    Ypos = 90;
    Serial.println("Reset pozycji");
    delay(200);
  }

  delay(30); // krótka przerwa dla stabilności
}
