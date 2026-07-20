#include "ESPMax.h"
#include "Buzzer.h"
#include "ESP32PWMServo.h"
#include "SuctionNozzle.h"
#include "PC_rec.h"

PC_REC pc_rec;

void setup() {
  // 初始化
  Buzzer_init();      // 蜂鸣器
  ESPMax_init();       // 总线舵机
  Nozzle_init();       // 吸嘴
  PWMServo_init();     // PWM舵机
  Valve_on();          //
  go_home(2000);
  Valve_off();
  delay(100);
  SetPWMServo(1, 1500, 1000);
  Serial.println("start...");
}

void loop() {
  pc_rec.rec_data();
  delay(10);
}
