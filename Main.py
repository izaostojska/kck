from random import randint
from colorama import Fore, init
import os
import sys
import keyboard

class Paddle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.speed = 5
        self.position = [width // 2 - self.width // 2, height - self.height - 1]

    def move_left(self):
        if self.position[0] > 0:
            self.position[0] -= self.speed

    def move_right(self):
        if self.position[0] + self.width < WIDTH:
            self.position[0] += self.speed

class Ball:
    def __init__(self, radius, width, height):
        self.radius = radius
        self.speed = 1
        self.position = [randint(radius, width - radius), height // 2]
        self.direction = [1, -1]

    def move(self):
        self.position[0] += self.speed * self.direction[0]
        self.position[1] += self.speed * self.direction[1]

class Block:
    def __init__(self, x, y):
        self.position = [x, y]

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle = Paddle(10, 1)
        self.ball = Ball(1, width, height)
        self.blocks = [Block(10 + 5 * i, 5 + 3 * j) for i in range(10) for j in range(4)]
        self.score = 0
        self.score_file = "top_scores.txt"
        self.top_scores = self.load_top_scores()
        self.reset_game()

    def detect_collision(self):
        dx, dy = self.ball.direction

        if (
            self.paddle.position[0] <= self.ball.position[0] <= self.paddle.position[0] + self.paddle.width - 1
            and self.ball.position[1] == self.height - 2
        ):
            dy = -dy
            self.ball.direction = [dx, dy]  # Update ball's direction

        return dx, dy

    def print_top_scores(self):
        print("TOP 3 SCORES:")
        for i, top_score in enumerate(self.top_scores, 1):
            print(f"{i}. {top_score}")
        print()

    def save_top_scores(self):
        with open(self.score_file, 'w') as file:
            for top_score in self.top_scores:
                file.write(f"{top_score}\n")

    def load_top_scores(self):
        if os.path.exists(self.score_file):
            with open(self.score_file, 'r') as file:
                return [int(line.strip()) for line in file]
        else:
            return [0, 0, 0]

    def update_game(self):
        self.ball.move()
        if self.ball.position[0] < self.ball.radius or self.ball.position[0] > self.width - self.ball.radius:
            self.ball.direction[0] = -self.ball.direction[0]

        if self.ball.position[1] < self.ball.radius:
            self.ball.direction[1] = -self.ball.direction[1]

        if (
            self.paddle.position[0] <= self.ball.position[0] <= self.paddle.position[0] + self.paddle.width - 1
            and self.ball.position[1] == self.height - 2
        ):
            self.detect_collision()

        for block in self.blocks:
            if self.ball.position == block.position:
                self.blocks.remove(block)
                self.score += 10
                self.detect_collision()

        if self.ball.position[1] > self.height -1:
            print(Fore.RED + 'GAME OVER!')
            # Update top scores
            self.top_scores.append(self.score)
            self.top_scores.sort(reverse=True)
            self.top_scores = self.top_scores[:3]  # Keep only the top 3 scores
            self.save_top_scores()
            return False
        elif not self.blocks:
            print(Fore.GREEN + 'WIN!!!')
            # Update top scores
            self.top_scores.append(self.score)
            self.top_scores.sort(reverse=True)
            self.top_scores = self.top_scores[:3]  # Keep only the top 3 scores
            self.save_top_scores()
            return False
        return True

    def print_field(self):
        for row in range(self.height):
            for col in range(self.width):
                if any(block.position == [col, row] for block in self.blocks):
                    print(Fore.YELLOW + 'X', end='')
                elif (
                        self.paddle.position[0] <= col <= self.paddle.position[0] + self.paddle.width - 1
                        and row == self.height - 1
                ):
                    print(Fore.GREEN + '=', end='')
                elif col == self.ball.position[0] and row == self.ball.position[1]:
                    print(Fore.RED + 'O', end='')
                else:
                    print(' ', end='')
            print()

        # Print score
        print(Fore.WHITE + f"Score: {self.score}")

        # Print exit info
        print(Fore.WHITE + "Press q to exit the game")

    def exit_game(self):
        print("Exiting the game.")
        self.save_top_scores()
        sys.exit()

    def show_menu(self):
        print("MENU:")
        print("1. Start New Game")
        print("2. See Top Scores")
        print("3. Exit")
        choice = input("Enter your choice (1, 2 or 3): ")
        return choice

    def reset_game(self):
        self.paddle = Paddle(10, 1)
        self.ball = Ball(1, self.width, self.height)
        self.blocks = [Block(10 + 5 * i, 5 + 3 * j) for i in range(10) for j in range(4)]
        self.score = 0


# The main part of the program
WIDTH, HEIGHT = 50, 20
fps = 10
init(autoreset=True)

while True:
    # Show menu
    game_instance = Game(WIDTH, HEIGHT)
    menu_choice = game_instance.show_menu()

    if menu_choice == '1':
        # Reset game state for a new round
        game_instance.reset_game()

        while True:
            # Move paddle based on currently pressed keys
            if keyboard.is_pressed("a"):
                game_instance.paddle.move_left()
            elif keyboard.is_pressed("d"):
                game_instance.paddle.move_right()

            # Update game
            if not game_instance.update_game():
                break

            # Clear field
            os.system('cls' if os.name == 'nt' else 'clear')

            # Draw field
            game_instance.print_field()

            # Check for exit command
            if keyboard.is_pressed("q"):
                game_instance.exit_game()

    elif menu_choice == '2':
        # Show top scores
        game_instance.print_top_scores()
        input("Press Enter to continue...")

    elif menu_choice == '3':
        game_instance.exit_game()

