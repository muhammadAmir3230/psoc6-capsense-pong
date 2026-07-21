"""
PSoC 6 CapSense Pong — 1 or 2 player
------------------------------------
Reads paddle position from PSoC 6 board(s) over UART (lines like "P42").
Both boards run IDENTICAL firmware; they're told apart by COM port.

Setup:
    pip install pygame pyserial

Run:
    python pong.py COM5 COM7   two boards, two players
    python pong.py COM5        one board vs AI
    python pong.py             keyboard test (P1: W/S, P2: arrows)

Board firmware must print "P<0-100>\n" whenever the slider is touched.
"""

import sys
import threading
import random

import pygame

# ----------------------------- serial readers -----------------------------
# index 0 = player 1 (left), index 1 = player 2 (right)
slider_pos = [50.0, 50.0]
serial_ok = [False, False]

def serial_thread(port, idx):
    try:
        import serial
        ser = serial.Serial(port, 115200, timeout=1)
        serial_ok[idx] = True
        buf = b""
        while True:
            data = ser.read(64)
            if not data:
                continue
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if line.startswith(b"P"):
                    try:
                        slider_pos[idx] = float(line[1:])
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Serial error on {port}: {e}")
        serial_ok[idx] = False

# ------------------------------- game -------------------------------------
W, H = 800, 600
PADDLE_W, PADDLE_H = 14, 110
BALL = 14

def main():
    ports = sys.argv[1:3]                     # up to two COM ports
    for i, port in enumerate(ports):
        threading.Thread(target=serial_thread, args=(port, i), daemon=True).start()
    two_player = len(ports) >= 2

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("PSoC 6 Pong")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 40)
    small = pygame.font.SysFont("consolas", 20)

    # Nokia-ish palette
    BG = (155, 188, 15)
    FG = (15, 56, 15)

    player_y = H / 2
    ai_y = H / 2
    ball_x, ball_y = W / 2, H / 2
    ball_vx, ball_vy = 5.0, 3.0
    score_p, score_a = 0, 0

    def reset_ball(direction):
        nonlocal ball_x, ball_y, ball_vx, ball_vy
        ball_x, ball_y = W / 2, H / 2
        ball_vx = 5.0 * direction
        ball_vy = random.choice([-1, 1]) * random.uniform(2.5, 4.5)

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()

        # ---- player 1 (left): slider on first port, else W/S keys
        if serial_ok[0]:
            player_y = (slider_pos[0] / 100.0) * (H - PADDLE_H) + PADDLE_H / 2
        else:
            if keys[pygame.K_w]:
                player_y -= 8
            if keys[pygame.K_s]:
                player_y += 8
        player_y = max(PADDLE_H / 2, min(H - PADDLE_H / 2, player_y))

        # ---- player 2 (right): slider on second port, keys, or AI
        if serial_ok[1]:
            ai_y = (slider_pos[1] / 100.0) * (H - PADDLE_H) + PADDLE_H / 2
        elif two_player:
            if keys[pygame.K_UP]:
                ai_y -= 8
            if keys[pygame.K_DOWN]:
                ai_y += 8
        else:
            # simple AI: follows ball with limited speed
            if ai_y < ball_y - 10:
                ai_y += 5.2
            elif ai_y > ball_y + 10:
                ai_y -= 5.2
        ai_y = max(PADDLE_H / 2, min(H - PADDLE_H / 2, ai_y))

        # ---- ball physics
        ball_x += ball_vx
        ball_y += ball_vy
        if ball_y <= BALL / 2 or ball_y >= H - BALL / 2:
            ball_vy = -ball_vy

        # player paddle (left)
        if (ball_x - BALL / 2 <= 30 + PADDLE_W
                and abs(ball_y - player_y) < PADDLE_H / 2 + BALL / 2
                and ball_vx < 0):
            ball_vx = -ball_vx * 1.05
            ball_vy += (ball_y - player_y) * 0.06

        # AI paddle (right)
        if (ball_x + BALL / 2 >= W - 30 - PADDLE_W
                and abs(ball_y - ai_y) < PADDLE_H / 2 + BALL / 2
                and ball_vx > 0):
            ball_vx = -ball_vx * 1.05
            ball_vy += (ball_y - ai_y) * 0.06

        # scoring
        if ball_x < 0:
            score_a += 1
            reset_ball(direction=1)
        elif ball_x > W:
            score_p += 1
            reset_ball(direction=-1)

        # ---- draw
        screen.fill(BG)
        for y in range(0, H, 30):                       # center dashed line
            pygame.draw.rect(screen, FG, (W / 2 - 2, y, 4, 18))
        pygame.draw.rect(screen, FG, (30, player_y - PADDLE_H / 2, PADDLE_W, PADDLE_H))
        pygame.draw.rect(screen, FG, (W - 30 - PADDLE_W, ai_y - PADDLE_H / 2, PADDLE_W, PADDLE_H))
        pygame.draw.rect(screen, FG, (ball_x - BALL / 2, ball_y - BALL / 2, BALL, BALL))
        screen.blit(font.render(f"{score_p}   {score_a}", True, FG), (W / 2 - 60, 20))
        p1 = "SLIDER" if serial_ok[0] else "KEYS W/S"
        p2 = "SLIDER" if serial_ok[1] else ("KEYS UP/DN" if two_player else "AI")
        screen.blit(small.render(f"P1: {p1}    P2: {p2}", True, FG), (10, H - 26))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
