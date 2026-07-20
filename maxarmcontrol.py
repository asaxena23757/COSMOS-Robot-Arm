import pygame
import serial
import struct
import time

# --- Setup ---
SERIAL_PORT = '/dev/cu.usbserial-XXXX'  # update to match your board's current port
BAUD = 9600  # matches PC_rec's Serial.begin(9600) in the factory firmware

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("MaxArm Keyboard Control")

FUNC_SET_ANGLE = 0x01

def checksum(data):
    s = sum(data) & 0xFF
    return (~s) & 0xFF

def send_angle(pul, time_ms):
    msg = bytearray([0xAA, 0x55, FUNC_SET_ANGLE, 8])
    for p in pul:
        msg += struct.pack('<h', int(p))
    msg += struct.pack('<H', time_ms)
    msg.append(checksum(msg[2:]))
    ser.write(msg)

# Current servo positions, starting at center
base_pos = 500   # servo 1
x_pos    = 500   # servo 2 (cap 700)
y_pos    = 500   # servo 3 (floor 470)

STEP = 10       # how much each key press moves the servo
running = True
clock = pygame.time.Clock()

print("Controls: A/D = base rotate, W/S = X axis, Up/Down arrows = Y axis, ESC to quit")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        base_pos -= STEP
    if keys[pygame.K_d]:
        base_pos += STEP
    if keys[pygame.K_w]:
        x_pos -= STEP
    if keys[pygame.K_s]:
        x_pos += STEP
    if keys[pygame.K_UP]:
        y_pos += STEP
    if keys[pygame.K_DOWN]:
        y_pos -= STEP
    if keys[pygame.K_ESCAPE]:
        running = False

    # Clamp to safe ranges (matching what we found in ESPMax.cpp)
    base_pos = max(0, min(1000, base_pos))
    x_pos    = max(0, min(700, x_pos))
    y_pos    = max(470, min(1000, y_pos))

    send_angle([base_pos, x_pos, y_pos], 100)

    screen.fill((30, 30, 30))
    font = pygame.font.SysFont(None, 28)
    lines = [
        f"Base (A/D): {base_pos}",
        f"X (W/S):    {x_pos}",
        f"Y (Up/Down): {y_pos}",
        "ESC to quit"
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, (255, 255, 255)), (20, 30 + i * 35))
    pygame.display.flip()

    clock.tick(20)  # ~20 updates per second

ser.close()
pygame.quit()
