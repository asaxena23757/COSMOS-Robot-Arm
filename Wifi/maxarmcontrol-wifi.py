import pygame
import socket
import time

# --- WiFi Setup ---
ESP32_IP = "192.168.4.1"  # update if yours differs
ESP32_PORT = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect((ESP32_IP, ESP32_PORT))

def send_angle(pul, time_ms):
    b, x, y = pul
    msg = f"{b},{x},{y}\n"
    sock.sendall(msg.encode())

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("MaxArm Keyboard Control")

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
        # A increases base_pos, D decreases (matches corrected direction)
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

    clock.tick(10)  # 10 confirmed best for minimizing jitter

sock.close()
pygame.quit()
