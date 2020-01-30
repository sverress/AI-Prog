<<<<<<< HEAD
from actor import Actor
from board import *
from critic import Critic
from action import Action
=======
from peg_solitaire.board import Diamond
from peg_solitaire.critic import Critic
from peg_solitaire.actor import Actor
>>>>>>> 2f59f137df44950d37cf6d27c4412bc4cc1994ba
import random
import copy


# Initialize board
num_episodes = 100
board_size = 4
init_board = Diamond(board_size)
init_state = init_board.get_state()

# Exploration constant
epsilon = 0.1
# Discount factor
gamma = 0.9
# Learning rate critic
alpha_c = 0.8
# Learning rate actor
alpha_a = 0.8
# Trace-decay factor
lambd = 0.7

# Initialize critic
critic = Critic(gamma, alpha_c, lambd)
critic.set_value_func(init_state, random.uniform(0, 0.01))
critic.set_elig_trace(init_state, 0)

# Initialize actor
actor = Actor(alpha_a, gamma, epsilon)
# Initialize all SAPs from init state
<<<<<<< HEAD
for sap in init_board.get_SAPS():
    actor.set_policy(sap, 0)
    actor.set_elig_trace(sap, 0)

result = []

for i in range(num_episodes):
    board = copy.deepcopy(init_board)
    action = actor.choose_action_simple(board)
    episode_history = []
    endstate = False
    while endstate == False:
        episode_history.append((board.get_state(), board.get_SAP(action)))
        board.do_action(action)

        if board.is_end_state():
            break

        # All SAPs of the new state needs to be initialized to value = 0 in the actor policy
        # Temp fix for testing:
        critic.init_new_state(board)
        for sap in board.get_SAPS():
            actor.set_policy(sap, 0)
            actor.set_elig_trace(sap, 0)

        reward = board.get_reward()
        optim_action = actor.choose_action_simple(board)
=======
actor.init_saps_from_board_state(init_board)

for i in range(num_episodes):
    board = copy.deepcopy(init_board)
    action = actor.choose_action(board)
    episode_history = [(board.get_state(), board.get_SAP(action))]
    endstate = False
    while endstate == False:
        board.do_action(action)  # All SAPs of the new state needs to be initialized to value = 0 in the actor policy
        actor.init_saps_from_board_state(board)
        reward = board.get_reward()
        optim_action = actor.choose_action(board)
>>>>>>> 2f59f137df44950d37cf6d27c4412bc4cc1994ba
        actor.set_elig_trace(board.get_SAP(optim_action), 1)
        delta = critic.calculate_TDerror(episode_history[-1][0], board.get_state(), reward)
        critic.set_elig_trace(board.get_SAP(optim_action), 1) # (episode_history[-1][0], 1)
        for state_tuple in reversed(episode_history):
            critic.update_value_func(state_tuple[0], delta)
            critic.update_elig_trace(state_tuple[0])
            actor.update_policy(state_tuple[1], delta)
            actor.update_elig_trace(state_tuple[1])
        action = optim_action
        endstate = board.is_end_state()
    result.append(board.get_num_stones())
