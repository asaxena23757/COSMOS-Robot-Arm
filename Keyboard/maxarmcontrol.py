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

def step_toward(current, target, step):
    if current < target:
        return min(current + step, target)
    elif current > target:
        return max(current - step, target)
    return current

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("MaxArm Keyboard Control")

HOME_POS = (500, 500, 500)
base_pos, x_pos, y_pos = HOME_POS
last_base, last_x, last_y = base_pos, x_pos, y_pos

STEP = 100
running = True
clock = pygame.time.Clock()

MOVE_STEP = 10           # units moved per tick on the active axis while animating, regardless of distance
moving = True           # generic "animating toward move_target" flag
move_target = HOME_POS  # where we're currently animating toward

AXIS_ORDER = ['base', 'x', 'y']  # order in which axes move one-at-a-time toward a programmed position
current_axis_idx = 0

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
            moving = True
            move_target = HOME_POS
            current_axis_idx = 0

        if event.type == pygame.KEYDOWN and event.key in SAVED_POSITIONS:
            name = SLOT_NAMES[event.key]
            if SAVED_POSITIONS[event.key] is None:
                # Not set yet -> save the current live position here, don't move
                SAVED_POSITIONS[event.key] = (base_pos, x_pos, y_pos)
                print(f"press {name} for {SAVED_POSITIONS[event.key]}")
            else:
                # Already set (hardcoded or previously saved) -> move there
                print(f"press {name} for {SAVED_POSITIONS[event.key]}")
                moving = True
                move_target = SAVED_POSITIONS[event.key]
                current_axis_idx = 0

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
        # Skip over any axes already at their target (e.g. an axis that
        # didn't need to move at all for this particular recall)
        while current_axis_idx < len(AXIS_ORDER):
            axis = AXIS_ORDER[current_axis_idx]
            current_val = {'base': base_pos, 'x': x_pos, 'y': y_pos}[axis]
            target_val = {'base': move_target[0], 'x': move_target[1], 'y': move_target[2]}[axis]
            if current_val == target_val:
                current_axis_idx += 1
                continue
            break

        if current_axis_idx >= len(AXIS_ORDER):
            moving = False
            current_axis_idx = 0
        else:
            axis = AXIS_ORDER[current_axis_idx]
            if axis == 'base':
                base_pos = step_toward(base_pos, move_target[0], MOVE_STEP)
            elif axis == 'x':
                x_pos = step_toward(x_pos, move_target[1], MOVE_STEP)
            else:
                y_pos = step_toward(y_pos, move_target[2], MOVE_STEP)

    if (base_pos, x_pos, y_pos) != (last_base, last_x, last_y):
        send_angle([base_pos, x_pos, y_pos], 600)
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