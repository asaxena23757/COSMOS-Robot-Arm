#include "Buzzer.h"

int Buzzer_freq = 2500;   // Frequency (频率)
int Buzzer_channel = 5;   // Channel (通道)
int Buzzer_resolution = 10;   // Resolution (分辨率)
const int Buzzer_Pin = 27; // Pin (引脚)

void Buzzer_init(){
    ledcSetup(Buzzer_channel,Buzzer_freq,Buzzer_resolution);
    ledcAttachPin(Buzzer_Pin, Buzzer_channel);
}

void Buzzer_on(){
    ledcWrite(Buzzer_channel, 300);  // Output PWM (输出PWM)
}

void Buzzer_off(){
    ledcWrite(Buzzer_channel, 0);
}

void setBuzzer(int s){
    Buzzer_on();
    delay(s);
    Buzzer_off();
}
