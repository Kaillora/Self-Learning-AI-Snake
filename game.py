import numpy as np
from collections import namedtuple
from enum import Enum
import pygame
import random

pygame.init()

GAME_SPEED = 50 #user can change speed at which the snake moves
CELL_SIZE = 20

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
FOOD_COLOR = (255, 255, 255)
SNAKE_COLOR_DARK = (0, 255, 0)
SNAKE_COLOR_LIGHT = (0, 200, 0)
OBSTACLE_COLOR = (0, 0, 255)

game_font = pygame.font.Font('arial.ttf', 25)

Point = namedtuple('Point', 'x, y')

class Direction(Enum):
    UP = 3
    DOWN = 4
    LEFT = 2
    RIGHT = 1

class SnakeGameAI:
    def __init__(self, w=800, h=600):
        self.w = w
        self.h = h

        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        
        self.high_score = 0 #tracks highscore
        
        self.reset()
    
    def reset(self):
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2, self.h/2) #initializes position of the snake
        self.snake = [
            self.head,
            Point(self.head.x - CELL_SIZE, self.head.y),
            Point(self.head.x - (2 * CELL_SIZE), self.head.y)
        ]
        
        self.frame_iteration = 0
        self.score = 0
        self.food = None
        self.obstacle = None
        
        self._place_food()
        self._place_obstacle()
    
    def _move(self, action):
        directions = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        current_idx = directions.index(self.direction)
        
        if np.array_equal(action, [1, 0, 0]):  # Straight
            self.direction = directions[current_idx]
        elif np.array_equal(action, [0, 1, 0]):  # Turn right
            self.direction = directions[(current_idx + 1) % 4]
        else:  # Turn left [0, 0, 1]
            self.direction = directions[(current_idx - 1) % 4]
        
        x, y = self.head.x, self.head.y
        
        if self.direction == Direction.UP:
            y -= CELL_SIZE
        elif self.direction == Direction.DOWN:
            y += CELL_SIZE
        elif self.direction == Direction.LEFT:
            x -= CELL_SIZE
        elif self.direction == Direction.RIGHT:
            x += CELL_SIZE
            
        self.head = Point(x, y)
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
            
        if pt.x < 0 or pt.x > self.w - CELL_SIZE or pt.y < 0 or pt.y > self.h - CELL_SIZE:
            return True
            
        if pt in self.snake[1:]:
            return True
            
        return False
    
    def _place_food(self):
        x = random.randint(0, (self.w - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (self.h - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        self.food = Point(x, y)
        
        if self.food in self.snake: #makes sure food does not spawn on snake
            self._place_food()
    
    def _place_obstacle(self):
        x = random.randint(0, (self.w - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (self.h - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        self.obstacle = Point(x, y)
        
        if self.obstacle in self.snake: #makes sure obstacle does not spawn on the snake
            self._place_obstacle()
    
    def _update_ui(self):
        self.display.fill(BLACK_COLOR)
        
        for segment in self.snake:
            pygame.draw.rect(self.display, SNAKE_COLOR_DARK, 
                           pygame.Rect(segment.x, segment.y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.display, SNAKE_COLOR_LIGHT, 
                           pygame.Rect(segment.x + 4, segment.y + 4, 12, 12))
        
        pygame.draw.rect(self.display, FOOD_COLOR, 
                       pygame.Rect(self.food.x, self.food.y, CELL_SIZE, CELL_SIZE))
        
        pygame.draw.rect(self.display, OBSTACLE_COLOR, 
                       pygame.Rect(self.obstacle.x, self.obstacle.y, CELL_SIZE, CELL_SIZE))
        
        score_text = game_font.render(f"Score: {self.score}", True, WHITE_COLOR)
        self.display.blit(score_text, [0, 0])
        
        high_score_text = game_font.render(f"High Score: {self.high_score}", True, WHITE_COLOR)
        self.display.blit(high_score_text, [0, 30])
        
        pygame.display.flip()
    
    def play_step(self, action):
        self.frame_iteration += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # Execute movement
        self._move(action)
        self.snake.insert(0, self.head)
        
        # Initialize reward
        reward = 0
        game_over = False
        
        # Check for game over conditions
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            # Update high score if current score is higher
            if self.score > self.high_score:
                self.high_score = self.score
            return reward, game_over, self.score
        
        # Check food collision
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        # Check obstacle collision
        elif self.head == self.obstacle:
            game_over = True
            # Update high score here too
            if self.score > self.high_score:
                self.high_score = self.score
        else:
            # Remove tail if no food eaten
            self.snake.pop()
        
        # Update display
        self._update_ui()
        self.clock.tick(GAME_SPEED)
        
        return reward, game_over, self.score