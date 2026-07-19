// Bus Servo
set_servo_in_range(1, 500, 1000);  // servo ID 1, rotates base of arm
set_servo_in_range(2, 500, 1000);  // servo ID 2, moves arm on x, max at 700
set_servo_in_range(3, 500, 1000);  // servo ID 3, moves arm on y, floor at 470

// Bus Servo XYZ
float pos[3] = {0, -200, 150};  // x, y, z
set_position(pos, 1000);

// Default
go_home(2000);  // 2000ms duration

// Read Bus Servo angles
short int angles[3];
read_angles(angles);

// Release Servo 
teaching_mode();

// Wrist Servo
SetPWMServo(1, 1500, 1000);  // channel 1, pulse ~500-2500 (1500 = center), 1000ms

// Suction
Valve_on();
Valve_off();
