from .actor import Actor
from peg_solitaire.board import Board
from peg_solitaire.board import Diamond
from .critic import Critic
import random

# Initialize board
num_episodes = 100
board_size = 4
init_board = Diamond(board_size)
init_state = init_board.get_state()

# Exploration constant
epsilon = 0.1
# Discount factor
gamma = 0.9
# Learning rate
alpha = 0.8

# Initialize critic
critic = Critic(gamma)
critic.update_value_func(init_state, random.uniform(0, 0.2))
critic.update_elig_trace(init_state, 0)

# Initialize actor
actor = Actor()
# Initialize all SAPs from init state

#actions = init_board.get_legal_actions(board_size)

for i in range(num_episodes):
    board = init_board #wrong
    action = actor.choose_action_epsilon_greedy(board, epsilon)
    episode_history = [(board.get_state(), board.get_SAP())]
    endstate = False
    while endstate == False:
        board.do_action(action)
        reward = board.get_reward()
        optim_action = actor.choose_action_epsilon_greedy(board, epsilon)
        actor.update_elig_trace(board.get_SAP(optim_action), 1)
        delta = critic.calculate_TDerror(episode_history[-1][0], board.get_state(), reward)
        critic.update_elig_trace(episode_history[-1][0], 1)

        for state_tuple in reversed(list(enumerate(episode_history))):
            print(i, e)

        action = optim_action
        endstate = board.is_end_state()