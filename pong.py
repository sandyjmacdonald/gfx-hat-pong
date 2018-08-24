from __future__ import division
import random
import time
from gfxhat import lcd, backlight, touch, fonts
from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = lcd.dimensions()
BALL_RAD = 1
PAD_WIDTH = 2
PAD_HEIGHT = 12
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2

ball_pos = [0, 0]
ball_vel = [0, 0]
paddle1_vel = 0
paddle2_vel = 0
l_score = 0
r_score = 0

font = ImageFont.truetype(fonts.BitocraFull, 11)

started = False
winner = 0
winning_score = 2
won = False

def ball_init(right):
    global ball_pos, ball_vel
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    horz = random.randrange(2, 4)
    vert = random.randrange(1, 3)

    if right == False:
        horz = -horz

    ball_vel = [horz, -vert]

def init():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel, l_score, r_score
    global score1, score2

    paddle1_pos = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
    paddle2_pos = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT // 2]
    l_score = 0
    r_score = 0

    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)

    backlight.set_all(0, 255, 0)
    backlight.show()


def draw(canvas):
    global image, paddle1_pos, paddle2_pos, ball_pos, ball_vel, l_score, r_score, BALL_RAD, won, winner, started, winning_score

    if not won:
        canvas.line(((WIDTH // 2, 0), (WIDTH // 2, HEIGHT)), 1)
        canvas.line(((PAD_WIDTH, 0), (PAD_WIDTH, HEIGHT)), 1)
        canvas.line(((WIDTH - PAD_WIDTH - 1, 0), (WIDTH - PAD_WIDTH - 1, HEIGHT)), 1)

        paddle1_pos[1] += paddle1_vel
        if paddle1_pos[1] < HALF_PAD_HEIGHT:
            paddle1_pos[1] = HALF_PAD_HEIGHT
        elif paddle1_pos[1] > HEIGHT - HALF_PAD_HEIGHT:
            paddle1_pos[1] = HEIGHT - HALF_PAD_HEIGHT

        paddle2_pos[1] += paddle2_vel
        if paddle2_pos[1] < HALF_PAD_HEIGHT:
            paddle2_pos[1] = HALF_PAD_HEIGHT
        elif paddle2_pos[1] > HEIGHT - HALF_PAD_HEIGHT:
            paddle2_pos[1] = HEIGHT - HALF_PAD_HEIGHT

        ball_pos[0] += int(ball_vel[0])
        ball_pos[1] += int(ball_vel[1])

        canvas.rectangle(((ball_pos[0] - BALL_RAD, ball_pos[1] - BALL_RAD), (ball_pos[0] + BALL_RAD, ball_pos[1] + BALL_RAD)), 1)
        canvas.rectangle(((paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] - HALF_PAD_HEIGHT), (paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] + HALF_PAD_HEIGHT)), 1)
        canvas.rectangle(((paddle2_pos[0] - HALF_PAD_WIDTH - 1, paddle2_pos[1] - HALF_PAD_HEIGHT), (paddle2_pos[0] + HALF_PAD_WIDTH + 1, paddle2_pos[1] + HALF_PAD_HEIGHT)), 1)

        if int(ball_pos[1]) <= BALL_RAD:
            ball_vel[1] = - ball_vel[1]
        if int(ball_pos[1]) >= HEIGHT - BALL_RAD:
            ball_vel[1] = -ball_vel[1]

        if int(ball_pos[0]) <= BALL_RAD + PAD_WIDTH and int(ball_pos[1]) in range(paddle1_pos[1] - HALF_PAD_HEIGHT,paddle1_pos[1] + HALF_PAD_HEIGHT, 1):
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1
        elif int(ball_pos[0]) <= BALL_RAD + PAD_WIDTH:
            r_score += 1
            ball_init(True)

        if int(ball_pos[0]) >= WIDTH + 1 - BALL_RAD - PAD_WIDTH and int(ball_pos[1]) in range(paddle2_pos[1] - HALF_PAD_HEIGHT,paddle2_pos[1] + HALF_PAD_HEIGHT, 1):
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1
        elif int(ball_pos[0]) >= WIDTH + 1 - BALL_RAD - PAD_WIDTH:
            l_score += 1
            ball_init(False)

        canvas.text(((WIDTH // 2) - 10 - font.getsize(str(l_score))[0], 1), str(l_score), 1, font)
        canvas.text(((WIDTH // 2) + 10, 1), str(r_score), 1, font)
        if l_score == winning_score:
            winner = 0
            won = True
        elif r_score == winning_score:
            winner = 1
            won = True
        else:
            won = False
    else:
        message = "PLAYER %i WINS!" % (winner + 1)
        canvas.text(((WIDTH // 2) - (font.getsize(message)[0] // 2), (HEIGHT // 2) - (font.getsize(message)[1] // 2)), message, 1, font)
        started = False

def handler(ch, event):
    global paddle1_vel, paddle2_vel, started
    if event == 'press':
        if ch == 0:
            paddle1_vel = -8
        elif ch == 3:
            paddle2_vel = -8
        elif ch == 1:
            paddle1_vel = 8
        elif ch == 5:
            paddle2_vel = 8
        elif ch == 4:
            if not started:
                init()
                started = True
        else:
            pass
    else:
        if ch == 0 or ch == 1:
            paddle1_vel = 0
        elif ch == 3 or ch == 5:
            paddle2_vel = 0
        else:
            pass

for x in range(6):
    touch.on(x, handler)

while True:
    if not started and won:
        time.sleep(5)
        won = False
    if started:
        image = Image.new('P', (WIDTH, HEIGHT))
        canvas = ImageDraw.Draw(image)
        draw(canvas)
    else:
        image = Image.open("pong-start-screen.png")

    for x in range(WIDTH):
        for y in range(HEIGHT):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, not pixel)

    lcd.show()
