#include <Arduino.h>

int contA_dir = 5;    // Direction pin
int contA_pwm = 6;    // PWM pin
char c = '0';

void setup() {
  Serial.begin(9600);
  pinMode(contA_dir, OUTPUT);
  pinMode(contA_pwm, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
    c = Serial.read();
    if (c == '1') {
      digitalWrite(contA_dir, HIGH);
      analogWrite(contA_pwm, 100);

      delay(500);
      digitalWrite(contA_pwm, LOW);

      digitalWrite(contA_dir, LOW);
      analogWrite(contA_pwm, 100);
      delay(50); 
    } else if (c == '0') {
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(contA_dir, LOW);
      analogWrite(contA_pwm, 0);
      delay(50);
    }
}
