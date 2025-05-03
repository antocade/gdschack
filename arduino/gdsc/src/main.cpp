#include <Arduino.h>

int contA_dir = 3;
int contA_pwm = 4;

int detect = 0;

void setup() {
  Serial.begin(9600);
  pinMode(contA_dir, OUTPUT);
  pinMode(contA_pwm, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    detect = Serial.read();
  }

  switch(detect) {
    //Forward
    case 1:
      digitalWrite(contA_dir, HIGH);
      analogWrite(contA_pwm, 100);

      delay(500);
      digitalWrite(contA_pwm, LOW);

      digitalWrite(contA_dir, LOW);
      analogWrite(contA_pwm, 100);
      delay(500);      
      break;
    default:
      //do nothing
      break;
  }
}
