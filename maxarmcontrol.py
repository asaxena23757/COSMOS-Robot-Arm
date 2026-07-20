import pygame
import serial
import struct
import time

# --- Setup ---
SERIAL_PORT = '/dev/cu.usbserial-10'  # update to match your board's current port
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

# Default/home position (center for all three)
HOME_POS = (500, 500, 500)

# Current servo positions, starting at center
base_pos, x_pos, y_pos = HOME_POS

# Track last sent position so we only send commands when something changes
last_base, last_x, last_y = base_pos, x_pos, y_pos

STEP = 10       # how much each key press moves the servo
running = True
clock = pygame.time.Clock()

resetting = False
reset_start_time = 0
reset_start_pos = HOME_POS
RESET_DURATION = 1.0  # seconds

resetting = True
reset_start_time = time.time()
reset_start_pos = (base_pos, x_pos, y_pos)

print("Controls: A/D = base rotate, W/S = X axis, Up/Down arrows = Y axis, E = reset to home, ESC to quit")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            resetting = True
            reset_start_time = time.time()
            reset_start_pos = (base_pos, x_pos, y_pos)

    keys = pygame.key.get_pressed()

    if not resetting:
        # Swapped: D now decreases, A now increases (fixes flipped direction)
        if keys[pygame.K_a]:
            base_pos += STEP
        if keys[pygame.K_d]:
            base_pos -= STEP
        if keys[pygame.K_w]:
            x_pos -= STEP
        if keys[pygame.K_s]:
            x_pos += STEP
        if keys[pygame.K_UP]:
            y_pos += STEP
        if keys[pygame.K_DOWN]:
            y_pos -= STEP

        # Clamp to safe ranges (matching what we found in ESPMax.cpp)
        base_pos = max(0, min(1000, base_pos))
        x_pos    = max(0, min(700, x_pos))
        y_pos    = max(470, min(1000, y_pos))

    if keys[pygame.K_ESCAPE]:
        running = False

    if resetting:
        elapsed = time.time() - reset_start_time
        t = min(elapsed / RESET_DURATION, 1.0)  # progress 0.0 -> 1.0

        base_pos = int(reset_start_pos[0] + (HOME_POS[0] - reset_start_pos[0]) * t)
        x_pos    = int(reset_start_pos[1] + (HOME_POS[1] - reset_start_pos[1]) * t)
        y_pos    = int(reset_start_pos[2] + (HOME_POS[2] - reset_start_pos[2]) * t)

        if t >= 1.0:
            base_pos, x_pos, y_pos = HOME_POS
            resetting = False

    # Only send a new command if something actually changed
    if (base_pos, x_pos, y_pos) != (last_base, last_x, last_y):
        send_angle([base_pos, x_pos, y_pos], 60)
        last_base, last_x, last_y = base_pos, x_pos, y_pos

    screen.fill((30, 30, 30))
    font = pygame.font.SysFont(None, 28)
    lines = [
        f"Base (A/D): {base_pos}",
        f"X (W/S):    {x_pos}",
        f"Y (Up/Down): {y_pos}",
        "Resetting..." if resetting else "E = reset | ESC = quit"
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, (255, 255, 255)), (20, 30 + i * 35))
    pygame.display.flip()

    clock.tick(10)

ser.close()
pygame.quit()