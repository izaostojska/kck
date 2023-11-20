from random import randint
from pytimedinput import timedInput
from colorama import Fore, init
import os
import sys

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
block_list = [[10 + 5 * i, 5 + 3 * j] for i in range(10) for j in range(4)]

# Score
score = 0

# File to store top scores
score_file = "top_scores.txt"

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


def print_field():
    for row in range(HEIGHT):
        for col in range(WIDTH):
            if [col, row] in block_list:
                print(Fore.YELLOW + 'X', end='')
            elif paddle[0] <= col <= paddle[0] + paddle_w - 1 and row == HEIGHT - 1:
                print(Fore.GREEN + '=', end='')
            elif col == ball[0] and row == ball[1]:
                print(Fore.RED + 'O', end='')
            else:
                print(' ', end='')
        print()

    # Print score
    print(Fore.WHITE + f"Score: {score}")

    # Print exit info
    print(Fore.WHITE + "Press q to exit the game")

def print_top_scores():
    print("TOP 3 SCORES:")
    for i, top_score in enumerate(top_scores, 1):
        print(f"{i}. {top_score}")
    print()

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


def update_game():
    global ball, dx, dy, paddle, block_list, score, top_scores

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
        print(Fore.RED + 'GAME OVER!')
        # Update top scores
        top_scores.append(score)
        top_scores.sort(reverse=True)
        top_scores = top_scores[:3]  # Keep only the top 3 scores
        save_top_scores()
        return False
    elif not block_list:
        print(Fore.GREEN + 'WIN!!!')
        # Update top scores
        top_scores.append(score)
        top_scores.sort(reverse=True)
        top_scores = top_scores[:3]  # Keep only the top 3 scores
        save_top_scores()
        return False

    return True

# Load top scores from file
top_scores = load_top_scores()

def exit_game():
    print("Exiting the game.")
    sys.exit()

def show_menu():
    print("MENU:")
    print("1. Start New Game")
    print("2. See Top Scores")
    print("3. Exit")
    choice = input("Enter your choice (1, 2 or 3): ")
    return choice


init(autoreset=True)

while True:
    # Show menu
    menu_choice = show_menu()

    if menu_choice == '1':
        # Reset game state for a new round
        paddle = [WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 1]
        ball = [randint(ball_radius, WIDTH - ball_radius), HEIGHT // 2]
        dx, dy = 1, -1
        block_list = [[10 + 5 * i, 5 + 3 * j] for i in range(10) for j in range(4)]
        score = 0

        while True:
            # Clear field
            os.system('cls' if os.name == 'nt' else 'clear')

            # Draw field
            print_field()

            # Get input (without waiting for enter)
            txt = timedInput('', timeout=0.1)[0]

            # Move paddle
            if txt == 'a' and paddle[0] > 0:
                paddle[0] -= paddle_speed
            elif txt == 'd' and paddle[0] + paddle_w < WIDTH:
                paddle[0] += paddle_speed

            # Update game
            if not update_game():
                break

            # Check for exit command
            if txt == 'q':
                exit_game()

    elif menu_choice == '2':
        # Show top scores
        print_top_scores()
        input("Press Enter to continue...")

    elif menu_choice == '3':
        exit_game()