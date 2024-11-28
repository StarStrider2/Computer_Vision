import pygame
import random
import time

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)

WIDTH, HEIGHT = 600, 600
GRID_SIZE = 15
CELL_SIZE = WIDTH // GRID_SIZE

FPS = 10
font = pygame.font.SysFont("Arial", 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Snake:
    def __init__(self):
        self.body = [(7, 7)]
        self.direction = (1, 0)
        self.length = 1

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_SIZE, (head_y + dir_y) % GRID_SIZE)
        self.body = [new_head] + self.body[:-1]

    def grow(self):
        tail_x, tail_y = self.body[-1]
        self.body.append((tail_x, tail_y))

    def check_collision(self):
        head = self.body[0]
        return head in self.body[1:]

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            pygame.draw.rect(screen, GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, DARK_GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)  # Контур змейки
        head_x, head_y = self.body[0]
        pygame.draw.circle(screen, BLACK, (head_x * CELL_SIZE + CELL_SIZE // 4, head_y * CELL_SIZE + CELL_SIZE // 4), 2)
        pygame.draw.circle(screen, BLACK, (head_x * CELL_SIZE + 3 * CELL_SIZE // 4, head_y * CELL_SIZE + CELL_SIZE // 4), 2)


class Apple:
    def __init__(self, snake_body):
        self.position = self.random_position(snake_body)

    def random_position(self, snake_body):
        while True:
            position = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if position not in snake_body:
                return position

    def draw(self, screen):
        apple_x, apple_y = self.position
        pygame.draw.circle(screen, RED, (apple_x * CELL_SIZE + CELL_SIZE // 2, apple_y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
        pygame.draw.circle(screen, DARK_RED, (apple_x * CELL_SIZE + CELL_SIZE // 2, apple_y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3, 3)


snake = Snake()
apple = Apple(snake.body)
clock = pygame.time.Clock()
score = 0

running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != (0, 1):
                snake.direction = (0, -1)
            elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                snake.direction = (0, 1)
            elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                snake.direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                snake.direction = (1, 0)

    snake.move()

    if snake.check_collision():
        running = False

    head_x, head_y = snake.body[0]
    apple_x, apple_y = apple.position
    if (head_x, head_y) == (apple_x, apple_y):
        snake.grow()
        apple = Apple(snake.body)
        score += 1

    snake.draw(screen)
    apple.draw(screen)

    score_text = font.render(f"Счет: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

    clock.tick(FPS)


game_over_text = font.render(f"Игра окончена. Счет: {score}", True, WHITE)
screen.fill(BLACK)
screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
pygame.display.flip()
time.sleep(2)
pygame.quit()
