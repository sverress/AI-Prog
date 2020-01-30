from peg_solitaire.board import Diamond
from peg_solitaire.critic import Critic
from peg_solitaire.actor import Actor
import random
import copy


# Initialize board
num_episodes = 100
board_size = 4
init_board = Diamond(board_size)

# Exploration constant
epsilon = 0.2
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
critic.init_state_from_board(init_board)

# Initialize actor
actor = Actor(alpha_a, gamma, epsilon)
# Initialize all SAPs from init state
actor.init_saps_from_board(init_board)

result = []

for i in range(num_episodes):
    board = copy.deepcopy(init_board)
    action = actor.choose_action(board)
    episode_history = []
    endstate = False
    while endstate == False:
        episode_history.append((board.get_state(), board.get_SAP(action)))
        board.do_action(action)

        if board.is_end_state():
            break

        # Initialize states and SAPs in actor and critic
        actor.init_saps_from_board(board)
        critic.init_state_from_board(board)

        reward = board.get_reward()
        optim_action = actor.choose_action_epsilon(board)
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

print(result)