import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:

    def __init__(self):
        self.games_played = 0
        self.exploration_rate = 0  # randomness
        self.discount_factor = 0.9  # discount rate
        self.replay_memory = deque(maxlen=MAX_MEMORY)
        self.neural_network = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.neural_network, lr=LEARNING_RATE, gamma=self.discount_factor)

    def get_game_state(self, game):
        snake_head = game.snake[0]
        left_point = Point(snake_head.x - 20, snake_head.y)
        right_point = Point(snake_head.x + 20, snake_head.y)
        up_point = Point(snake_head.x, snake_head.y - 20)
        down_point = Point(snake_head.x, snake_head.y + 20)
        
        moving_left = game.direction == Direction.LEFT
        moving_right = game.direction == Direction.RIGHT
        moving_up = game.direction == Direction.UP
        moving_down = game.direction == Direction.DOWN

        state_vector = [
            # Danger straight ahead
            (moving_right and game.is_collision(right_point)) or 
            (moving_left and game.is_collision(left_point)) or 
            (moving_up and game.is_collision(up_point)) or 
            (moving_down and game.is_collision(down_point)),

            # Danger to the right
            (moving_up and game.is_collision(right_point)) or 
            (moving_down and game.is_collision(left_point)) or 
            (moving_left and game.is_collision(up_point)) or 
            (moving_right and game.is_collision(down_point)),

            # Danger to the left
            (moving_down and game.is_collision(right_point)) or 
            (moving_up and game.is_collision(left_point)) or 
            (moving_right and game.is_collision(up_point)) or 
            (moving_left and game.is_collision(down_point)),
            
            # Current direction
            moving_left,
            moving_right,
            moving_up,
            moving_down,
            
            # Food position relative to head
            game.food.x < game.head.x,  # food is left
            game.food.x > game.head.x,  # food is right
            game.food.y < game.head.y,  # food is up
            game.food.y > game.head.y   # food is down
        ]

        return np.array(state_vector, dtype=int)

    def store_experience(self, state, action, reward, next_state, game_over):
        self.replay_memory.append((state, action, reward, next_state, game_over))

    def experience_replay(self):
        if len(self.replay_memory) > BATCH_SIZE:
            batch = random.sample(self.replay_memory, BATCH_SIZE)
        else:
            batch = self.replay_memory

        states, actions, rewards, next_states, dones = zip(*batch)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def learn_from_move(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def choose_action(self, state):
        # Exploration vs exploitation
        self.exploration_rate = 80 - self.games_played
        action_vector = [0, 0, 0]
        
        if random.randint(0, 200) < self.exploration_rate:
            # Random exploration
            random_move = random.randint(0, 2)
            action_vector[random_move] = 1
        else:
            # Exploitation based on model
            state_tensor = torch.tensor(state, dtype=torch.float)
            q_values = self.neural_network(state_tensor)
            best_move = torch.argmax(q_values).item()
            action_vector[best_move] = 1

        return action_vector


def train_snake_ai():
    cumulative_score = 0
    high_score = 0
    ai_agent = Agent()
    snake_game = SnakeGameAI()
    
    while True:
        # Get current state
        current_state = ai_agent.get_game_state(snake_game)

        # Decide action
        next_move = ai_agent.choose_action(current_state)

        # Execute action and observe result
        reward, is_game_over, current_score = snake_game.play_step(next_move)
        new_state = ai_agent.get_game_state(snake_game)

        # Learn from this experience
        ai_agent.learn_from_move(current_state, next_move, reward, new_state, is_game_over)

        # Store for future learning
        ai_agent.store_experience(current_state, next_move, reward, new_state, is_game_over)

        if is_game_over:
            # Reset game and train on batch
            snake_game.reset()
            ai_agent.games_played += 1
            ai_agent.experience_replay()

            if current_score > high_score:
                high_score = current_score
                ai_agent.neural_network.save()

            print(f'Game #{ai_agent.games_played} | Score: {current_score} | Best: {high_score}')

            cumulative_score += current_score
            average_score = cumulative_score / ai_agent.games_played
            print(f'Average Score: {average_score:.2f}\n')


if __name__ == '__main__':
    train_snake_ai()