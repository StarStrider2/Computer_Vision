import pygame
import random
import time
import cv2
import mediapipe as mp
import numpy as np

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)

WIDTH, HEIGHT = 600, 600
CAMERA_WIDTH, CAMERA_HEIGHT = 300, 168
GRID_SIZE = 15
CELL_SIZE = WIDTH // GRID_SIZE

FPS = 8
font = pygame.font.SysFont("Arial", 30)

# Инициализация экрана
screen = pygame.display.set_mode((WIDTH + CAMERA_WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Hand Control")

# Инициализация MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

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
            pygame.draw.rect(screen, DARK_GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        head_x, head_y = self.body[0]
        pygame.draw.circle(screen, BLACK, (head_x * CELL_SIZE + CELL_SIZE // 4, head_y * CELL_SIZE + CELL_SIZE // 4), 2)
        pygame.draw.circle(screen, BLACK,
                           (head_x * CELL_SIZE + 3 * CELL_SIZE // 4, head_y * CELL_SIZE + CELL_SIZE // 4), 2)


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
        pygame.draw.circle(screen, RED, (apple_x * CELL_SIZE + CELL_SIZE // 2, apple_y * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 3)
        pygame.draw.circle(screen, DARK_RED,
                           (apple_x * CELL_SIZE + CELL_SIZE // 2, apple_y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3,
                           3)


def get_finger_direction(landmarks):
    if landmarks:
        x1, y1 = landmarks[8].x, landmarks[8].y
        x2, y2 = landmarks[7].x, landmarks[7].y
        dx, dy = x1 - x2, y1 - y2

        if abs(dx) > abs(dy):
            if dx > 0:
                return (-1, 0)  # Влево
            else:
                return (1, 0)  # Вправо
        else:
            if dy > 0:
                return (0, 1)  # Вниз
            else:
                return (0, -1)  # Вверх
    return (0, 0)


snake = Snake()
apple = Apple(snake.body)
clock = pygame.time.Clock()
score = 0

cap = cv2.VideoCapture(0)

direction_text = "Направление: ???"

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:

            direction = get_finger_direction(landmarks.landmark)
            snake.direction = direction

            if direction == (0, -1):
                direction_text = "Направление: Вверх"
            elif direction == (0, 1):
                direction_text = "Направление: Вниз"
            elif direction == (-1, 0):
                direction_text = "Направление: Влево"
            elif direction == (1, 0):
                direction_text = "Направление: Вправо"

            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)


    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            cv2.destroyAllWindows()
            exit()

    snake.move()

    if snake.check_collision():
        break

    head_x, head_y = snake.body[0]
    apple_x, apple_y = apple.position
    if (head_x, head_y) == (apple_x, apple_y):
        snake.grow()
        apple = Apple(snake.body)
        score += 1

    screen.fill(BLACK)
    snake.draw(screen)
    apple.draw(screen)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (300, 168))
    frame_surface = pygame.image.fromstring(frame_resized.tobytes(), (CAMERA_WIDTH, CAMERA_HEIGHT), 'RGB')

    screen.blit(frame_surface, (600, 0))

    score_text = font.render(f"Счет: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    direction_label = font.render(direction_text, True, WHITE)
    screen.blit(direction_label, (WIDTH-60, HEIGHT - 40))

    pygame.display.flip()

    clock.tick(FPS)


game_over_text = font.render(f"Игра окончена. Счет: {score}", True, WHITE)
screen.blit(game_over_text,
            (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
pygame.display.flip()
time.sleep(10)

cap.release()
pygame.quit()
cv2.destroyAllWindows()
