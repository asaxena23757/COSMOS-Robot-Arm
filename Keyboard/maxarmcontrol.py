import pygame
import serial
import struct
import time

# --- Setup ---
SERIAL_PORT = '/dev/cu.usbserial-110'  # update to match your board's current port
BAUD = 9600

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

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

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("MaxArm Keyboard Control")

HOME_POS = (500, 500, 500)
base_pos, x_pos, y_pos = HOME_POS
last_base, last_x, last_y = base_pos, x_pos, y_pos

STEP = 6
running = True
clock = pygame.time.Clock()

moving = False          # animating toward move_target (E or F/G/H)
move_target = HOME_POS  # where we're currently animating toward

AXIS_ORDER = ['base', 'x', 'y']  # order in which axes move one-at-a-time toward a programmed position
current_axis_idx = 0

# --- Direct-jump timing (applies to ALL automated moves: E and F/G/H) ---
# Each axis moves to its target in ONE command, with the servo's travel time
# scaled linearly to the distance: time_ms = distance * TIME_PER_UNIT_MS.
# e.g. a 470-unit move -> 4700 ms. Axes move strictly one at a time.
TIME_PER_UNIT_MS = 10     # ms of servo travel time per pulse-unit of distance
direct_sent = False       # has the single big command for the current axis been sent yet?
direct_end_time = 0.0     # wall-clock time (time.time()) when the current axis's move should be done

# --- Saved position slots (F / G / H) ---
# Set any of these to a (base, x, y) tuple in code to hardcode that slot.
# Leave as None to let the first press of that key save the arm's CURRENT
# position into that slot live. Every press after a slot is set (whether
# hardcoded or saved live) moves the arm to that position.
SAVED_POSITIONS = {
    pygame.K_f: None,
    pygame.K_g: None,
    pygame.K_h: None,
}
SLOT_NAMES = {pygame.K_f: 'f', pygame.K_g: 'g', pygame.K_h: 'h'}

def start_move(target):
    """Begin an automated one-axis-at-a-time direct move toward target."""
    global moving, move_target, current_axis_idx, direct_sent
    moving = True
    move_target = target
    current_axis_idx = 0
    direct_sent = False

print("Controls: A/D = base rotate, W/S = X axis, Up/Down arrows = Y axis, "
      "E = reset to home, F/G/H = save (if unset) or go to slot, ESC to quit")

# Show any slots that were preset in code before the loop even starts
for _key, _pos in SAVED_POSITIONS.items():
    if _pos is not None:
        print(f"press {SLOT_NAMES[_key]} for {_pos}")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            start_move(HOME_POS)

        if event.type == pygame.KEYDOWN and event.key in SAVED_POSITIONS:
            name = SLOT_NAMES[event.key]
            if SAVED_POSITIONS[event.key] is None:
                # Not set yet -> save the current live position here, don't move
                SAVED_POSITIONS[event.key] = (base_pos, x_pos, y_pos)
                print(f"press {name} for {SAVED_POSITIONS[event.key]}")
            else:
                # Already set (hardcoded or previously saved) -> move there
                print(f"press {name} for {SAVED_POSITIONS[event.key]}")
                start_move(SAVED_POSITIONS[event.key])

    keys = pygame.key.get_pressed()

    if not moving:
        if keys[pygame.K_a]:
            base_pos += STEP
        if keys[pygame.K_d]:
            base_pos -= STEP
        if keys[pygame.K_w]:
            x_pos -= STEP
        if keys[pygame.K_s]:
            x_pos += STEP
        if keys[pygame.K_UP]:
            y_pos -= STEP
        if keys[pygame.K_DOWN]:
            y_pos += STEP

        base_pos = max(0, min(1000, base_pos))
        x_pos    = max(0, min(700, x_pos))
        y_pos    = max(470, min(1000, y_pos))

    if keys[pygame.K_ESCAPE]:
        running = False

    if moving:
        # Skip over any axes already at their target
        while current_axis_idx < len(AXIS_ORDER):
            axis = AXIS_ORDER[current_axis_idx]
            current_val = {'base': base_pos, 'x': x_pos, 'y': y_pos}[axis]
            target_val = {'base': move_target[0], 'x': move_target[1], 'y': move_target[2]}[axis]
            if current_val == target_val:
                current_axis_idx += 1
                direct_sent = False
                continue
            break

        if current_axis_idx >= len(AXIS_ORDER):
            moving = False
            current_axis_idx = 0
        else:
            axis = AXIS_ORDER[current_axis_idx]
            current_val = {'base': base_pos, 'x': x_pos, 'y': y_pos}[axis]
            target_val = {'base': move_target[0], 'x': move_target[1], 'y': move_target[2]}[axis]

            if not direct_sent:
                # One giant step for this axis: jump straight to target, with
                # travel time scaled linearly to the distance being covered.
                distance = abs(target_val - current_val)
                time_ms = distance * TIME_PER_UNIT_MS

                if axis == 'base':
                    base_pos = target_val
                elif axis == 'x':
                    x_pos = target_val
                else:
                    y_pos = target_val

                send_angle([base_pos, x_pos, y_pos], time_ms)
                last_base, last_x, last_y = base_pos, x_pos, y_pos  # suppress duplicate send below

                direct_end_time = time.time() + (time_ms / 1000.0)
                direct_sent = True
            else:
                # Wait for the servo's travel time to elapse before the next axis
                if time.time() >= direct_end_time:
                    current_axis_idx += 1
                    direct_sent = False

    if (base_pos, x_pos, y_pos) != (last_base, last_x, last_y):
        send_angle([base_pos, x_pos, y_pos], 400)
        last_base, last_x, last_y = base_pos, x_pos, y_pos

    screen.fill((30, 30, 30))
    font = pygame.font.SysFont(None, 28)
    lines = [
        f"Base (A/D): {base_pos}",
        f"X (W/S):    {x_pos}",
        f"Y (Up/Down): {y_pos}",
        "Moving..." if moving else "E = home | F/G/H = slots | ESC = quit"
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, (255, 255, 255)), (20, 30 + i * 35))
    pygame.display.flip()

    clock.tick(10)

ser.close()
pygame.quit()