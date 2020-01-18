from .actor import Actor
from .board import Diamond
from .critic import Critic
import random

num_episodes = 100
board_size = 4
init_board = Diamond(board_size)
init_state = init_board.get_state()

#Initialize critic
critic = Critic()
critic.valueFunc[init_state] = random.uniform(0, 0.2)
critic.elig_trace[init_state] = 0

# Initialize actor
actor = Actor(init_board)
actor.policy[init_state] = 0
actor.elig_trace[init_state] = 0
actions = init_board.get_legal_actions(board_size)

for i in range(num_episodes):
    state = init_state
    action = actor.choose_action_epsilon_greedy(state, epsilon)
    endstate = False
    while endstate == False:

        endstate = state.is_end_state()