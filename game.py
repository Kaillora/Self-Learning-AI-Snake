import numpy as np
from collections import namedtuple
from enum import Enum
import pygame
import random

# Initialize Pygame
pygame.init()

# Game configuration
GAME_SPEED = 50
CELL_SIZE = 20

# Color definitions (RGB)
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
FOOD_COLOR = (200, 0, 0)
SNAKE_COLOR_DARK = (0, 255, 0)
SNAKE_COLOR_LIGHT = (0, 200, 0)
OBSTACLE_COLOR = (0, 0, 255)

# Game font
game_font = pygame.font.Font('arial.ttf', 25)

# Data structures
Point = namedtuple('Point', 'x, y')

class Direction(Enum):
    UP = 3
    DOWN = 4
    LEFT = 2
    RIGHT = 1

class SnakeGameAI:
    def __init__(self, w=800, h=600):
        # Window dimensions
        self.w = w
        self.h = h
        
        # Setup pygame window
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        
        # Initialize game
        self.reset()
    
    def reset(self):
        # Starting direction
        self.direction = Direction.RIGHT
        
        # Initialize snake position
        self.head = Point(self.w/2, self.h/2)
        self.snake = [
            self.head,
            Point(self.head.x - CELL_SIZE, self.head.y),
            Point(self.head.x - (2 * CELL_SIZE), self.head.y)
        ]
        
        # Game variables
        self.frame_iteration = 0
        self.score = 0
        self.food = None
        self.obstacle = None
        
        # Place initial items
        self._place_food()
        self._place_obstacle()
    
    def _move(self, action):
        # Movement logic based on action [straight, right, left]
        directions = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        current_idx = directions.index(self.direction)
        
        if np.array_equal(action, [1, 0, 0]):  # Straight
            self.direction = directions[current_idx]
        elif np.array_equal(action, [0, 1, 0]):  # Turn right
            self.direction = directions[(current_idx + 1) % 4]
        else:  # Turn left [0, 0, 1]
            self.direction = directions[(current_idx - 1) % 4]
        
        # Update head position
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
            
        # Check wall collision
        if pt.x < 0 or pt.x > self.w - CELL_SIZE or pt.y < 0 or pt.y > self.h - CELL_SIZE:
            return True
            
        # Check self collision
        if pt in self.snake[1:]:
            return True
            
        return False
    
    def _place_food(self):
        x = random.randint(0, (self.w - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (self.h - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        self.food = Point(x, y)
        
        # Ensure food doesn't spawn on snake
        if self.food in self.snake:
            self._place_food()
    
    def _place_obstacle(self):
        x = random.randint(0, (self.w - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (self.h - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        self.obstacle = Point(x, y)
        
        # Ensure obstacle doesn't spawn on snake
        if self.obstacle in self.snake:
            self._place_obstacle()
    
    def _update_ui(self):
        # Clear screen
        self.display.fill(BLACK_COLOR)
        
        # Draw snake
        for segment in self.snake:
            pygame.draw.rect(self.display, SNAKE_COLOR_DARK, 
                           pygame.Rect(segment.x, segment.y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.display, SNAKE_COLOR_LIGHT, 
                           pygame.Rect(segment.x + 4, segment.y + 4, 12, 12))
        
        # Draw food
        pygame.draw.rect(self.display, FOOD_COLOR, 
                       pygame.Rect(self.food.x, self.food.y, CELL_SIZE, CELL_SIZE))
        
        # Draw obstacle
        pygame.draw.rect(self.display, OBSTACLE_COLOR, 
                       pygame.Rect(self.obstacle.x, self.obstacle.y, CELL_SIZE, CELL_SIZE))
        
        # Display score
        score_text = game_font.render(f"Score: {self.score}", True, WHITE_COLOR)
        self.display.blit(score_text, [0, 0])
        
        # Update display
        pygame.display.flip()
    
    def play_step(self, action):
        self.frame_iteration += 1
        
        # Handle pygame events
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
            return reward, game_over, self.score
        
        # Check food collision
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        # Check obstacle collision
        elif self.head == self.obstacle:
            game_over = True
        else:
            # Remove tail if no food eaten
            self.snake.pop()
        
        # Update display
        self._update_ui()
        self.clock.tick(GAME_SPEED)
        
        return reward, game_over, self.score