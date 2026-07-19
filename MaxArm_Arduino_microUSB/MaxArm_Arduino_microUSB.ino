#include "ESPMax.h"
#include "Buzzer.h"
#include "ESP32PWMServo.h"
#include "SuctionNozzle.h"
#include "PC_rec.h"

PC_REC pc_rec;

void setup() {
  // 初始化
  Buzzer_init(); //蜂鸣器
  ESPMax_init(); //总线舵机
  Nozzle_init(); //吸嘴
  PWMServo_init(); //PWM舵机
  Valve_on(); //
  go_home(2000);
  Valve_off();
  delay(100);
  SetPWMServo(1, 1500, 1000);
  Serial.println("start...");
}

void loop() {
  Serial.println("Testing servo 1...");
  set_servo_in_range(1, 400, 800);
  delay(1000);
  set_servo_in_range(1, 600, 800);
  delay(1000);

  Serial.println("Testing servo 2...");
  set_servo_in_range(2, 400, 800);
  delay(1000);
  set_servo_in_range(2, 600, 800);
  delay(1000);

  Serial.println("Testing servo 3...");
  set_servo_in_range(3, 500, 800);
  delay(1000);
  set_servo_in_range(3, 650, 800);
  delay(1000);

  Serial.println("Reading back angles...");
  short int angles[3];
  read_angles(angles);
  Serial.print("Angles: ");
  Serial.print(angles[0]); Serial.print(" ");
  Serial.print(angles[1]); Serial.print(" ");
  Serial.println(angles[2]);

  Serial.println("=== Cycle done, repeating ===");
  delay(2000);
}
