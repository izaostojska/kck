import curses
from random import randint
from colorama import Fore, init
import os
import sys
import keyboard
import time

WIDTH, HEIGHT = 50, 20
fps = 10

# Paddle settings
paddle_w = 10
paddle_h = 1
paddle_speed = 1
paddle = [WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 1]

# Ball settings
ball_radius = 1
ball_speed = 1
ball = [randint(ball_radius, WIDTH - ball_radius), HEIGHT // 2]
dx, dy = 1, -1

# Blocks settings
block_list = [[3 + 3 * i, 2 + 2 * j] for i in range(8) for j in range(4)]

# Score
score = 0

# File to store top scores
score_file = "top_scores.txt"

# Initialize curses
stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)


def detect_collision(dx, dy, ball, rect):
    if dx > 0:
        delta_x = ball[0] + ball_radius - rect[0]
    else:
        delta_x = rect[0] + paddle_w - ball[0] + ball_radius
    if dy > 0:
        delta_y = ball[1] + ball_radius - rect[1]
    else:
        delta_y = rect[1] + 1 - ball[1] + ball_radius

    if abs(delta_x - delta_y) < 1:
        dx, dy = -dx, -dy
    elif delta_x > delta_y:
        dy = -dy
    elif delta_y > delta_x:
        dx = -dx
    return dx, dy


def print_field(stdscr):
    stdscr.clear()
    for row in range(HEIGHT):
        for col in range(WIDTH):
            if [col, row] in block_list:
                stdscr.addch(row, col, 'X', curses.color_pair(1))
            elif paddle[0] <= col <= paddle[0] + paddle_w - 1 and row == HEIGHT - 1:
                stdscr.addch(row, col, '=', curses.color_pair(2))
            elif col == ball[0] and row == ball[1]:
                stdscr.addch(row, col, 'O', curses.color_pair(3))
            else:
                stdscr.addch(row, col, ' ')

    # Print score
    stdscr.addstr(HEIGHT, 0, f"Score: {score}", curses.color_pair(4))

    # Print exit info
    stdscr.addstr(HEIGHT + 1, 0, "Press q to exit the game", curses.color_pair(5))


def print_top_scores(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "TOP 3 SCORES:", curses.A_BOLD)
    for i, top_score in enumerate(top_scores, 1):
        stdscr.addstr(i, 0, f"{i}. {top_score}")
    stdscr.addstr(len(top_scores) + 2, 0, "Press Enter to continue...", curses.A_BOLD)
    stdscr.refresh()


def save_top_scores():
    with open(score_file, 'w') as file:
        for top_score in top_scores:
            file.write(f"{top_score}\n")


def load_top_scores():
    if os.path.exists(score_file):
        with open(score_file, 'r') as file:
            return [int(line.strip()) for line in file]
    else:
        return [0, 0, 0]

# Load top scores from file
top_scores = load_top_scores()

def update_game(stdscr):
    global ball, dx, dy, paddle, block_list, score, top_scores, ball_timer

    # Ball movement
    ball[0] += ball_speed * dx
    ball[1] += ball_speed * dy

    # Collision left/right
    if ball[0] < ball_radius or ball[0] > WIDTH - ball_radius:
        dx = -dx

    # Collision top
    if ball[1] < ball_radius:
        dy = -dy

    # Collision paddle
    if paddle[0] <= ball[0] <= paddle[0] + paddle_w - 1 and ball[1] == HEIGHT - 2:
        dx, dy = detect_collision(dx, dy, ball, paddle)

    # Collision blocks
    if ball in block_list:
        block_list.remove(ball)
        dx, dy = detect_collision(dx, dy, ball, ball)
        # Increase score when a block is hit
        score += 10

    # Win/game over
    if ball[1] > HEIGHT - 1:
        stdscr.addstr(0, 0, Fore.RED + 'GAME OVER!')
        # Update top scores
        top_scores.append(score)
        top_scores.sort(reverse=True)
        top_scores = top_scores[:3]
        save_top_scores()
        return False
    elif not block_list:
        stdscr.addstr(0, 0, Fore.GREEN + 'WIN!!!')
        # Update top scores
        top_scores.append(score)
        top_scores.sort(reverse=True)
        top_scores = top_scores[:3]
        save_top_scores()
        return False

    return True



def exit_game():
    print("Exiting the game.")
    sys.exit()


def show_menu(stdscr):
    ascii_art = """
             ,-"     "-.
            / o       o \\
           /   \\     /   \\
          /     )-"-(     \\
         /     ( 6 6 )     \\
        /       \\ " /       \\
       /         )=(         \\
      /   o   .--"-"--.   o   \\
     /    I  /  -   -  \\  I    \\
 .--(    (_}y/\\       /\\y{_)    )--.
(    ".___l\\/__/\\_____/__\\/l___,"    )
 \\                                 /
  "-._      o O o O o O o      _,-"
      `--Y--.___________.--Y--'
         |==.___________.==| 
         `==.___________.==' 
"""

    stdscr.clear()
    for i, line in enumerate(ascii_art.split('\n')):
        stdscr.addstr(i, 0, line)

    stdscr.addstr(len(ascii_art.split('\n')) + 1, 0, "MENU:", curses.A_BOLD)
    stdscr.addstr(len(ascii_art.split('\n')) + 2, 0, "1. Start New Game")
    stdscr.addstr(len(ascii_art.split('\n')) + 3, 0, "2. See Top Scores")
    stdscr.addstr(len(ascii_art.split('\n')) + 4, 0, "3. Exit")
    stdscr.addstr(len(ascii_art.split('\n')) + 5, 0, "Enter your choice (1, 2, or 3): ")
    stdscr.refresh()
    choice = stdscr.getch()
    if choice == ord('2'):
        print("Calling print_top_scores function")  # Add this line for debugging
        print_top_scores(stdscr)
        stdscr.getch()

    return chr(choice) if choice in [ord('1'), ord('2'), ord('3')] else None


curses.wrapper(lambda stdscr: show_menu(stdscr))
while True:
    # Show menu
    menu_choice = show_menu(stdscr)

    if menu_choice == '1':
        # Reset game state for a new round
        paddle = [WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 1]
        ball = [randint(ball_radius, WIDTH - ball_radius), HEIGHT // 2]
        dx, dy = 1, -1
        block_list = [[10 + 5 * i, 5 + 3 * j] for i in range(10) for j in range(4)]
        score = 0

        while True:
            # Move paddle based on currently pressed keys
            if keyboard.is_pressed("a") and paddle[0] > 0:
                paddle[0] -= paddle_speed
            elif keyboard.is_pressed("d") and paddle[0] + paddle_w < WIDTH:
                paddle[0] += paddle_speed

            # Update game
            if not update_game(stdscr):
                break

            # Clear field
            stdscr.clear()

            # Draw field
            print_field(stdscr)

            # Check for exit command
            if keyboard.is_pressed("q"):
                exit_game()

            # Adjust the frame rate
            time.sleep(1 / fps)

            # Refresh the screen
            stdscr.refresh()

    elif menu_choice == '2':
        # Show top scores
        print_top_scores(stdscr)
        stdscr.getch()

    elif menu_choice == '3':
        exit_game()
