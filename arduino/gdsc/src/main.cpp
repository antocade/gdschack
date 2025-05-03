#include <Arduino.h>

int contA_dir = 3;
int contA_pwm = 4;

int contB_dir = 5;
int contB_pwm = 6;

int detect = 0;

void setup() {
  Serial.begin(9600);
  pinMode(contA_dir, OUTPUT);
  pinMode(contA_pwm, OUTPUT);
  pinMode(contB_dir, OUTPUT);
  pinMode(contB_pwm, OUTPUT);
}

void loop() {
  // Serial.println("test");
  // delay(1000);

  if (Serial.available()) {
    detect = Serial.read();
  }

  switch(detect) {
    //Forward
    case 1:
      digitalWrite(contA_dir, HIGH);
      analogWrite(contA_pwm, 100);

      digitalWrite(contB_dir, HIGH);
      analogWrite(contB_pwm, 100);

      delay(500);
      digitalWrite(contA_pwm, LOW);
      digitalWrite(contB_pwm, LOW);
      break;

    //Back
    case 2:
      digitalWrite(contA_dir, LOW);
      analogWrite(contA_pwm, 100);

      digitalWrite(contB_dir, LOW);
      analogWrite(contB_pwm, 100);

      delay(500);
      digitalWrite(contA_pwm, LOW);
      digitalWrite(contB_pwm, LOW);
      break;
    default:
      //do nothing
      break;
  }
}
