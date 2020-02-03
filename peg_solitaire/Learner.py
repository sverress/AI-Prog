from peg_solitaire.board import Diamond
from peg_solitaire.critic import Critic
from peg_solitaire.actor import Actor
import copy
from matplotlib import pyplot as plt


# Initialize board
num_episodes = 1000
board_size = 4
init_board = Diamond(board_size)

# Exploration constant
epsilon = 0.3
# Discount factor
gamma = 0.98
# Learning rate critic
alpha_c = 0.9
# Learning rate actor
alpha_a = 0.9
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
    # See progress
    if i % 50 == 0:
        print(i)
        actor.epsilon = actor.epsilon*0.8
    board = copy.deepcopy(init_board)
    action = actor.choose_action_epsilon(board)
    episode_history = []
    end_state = False
    while not end_state:
        episode_history.append((board.get_state(), board.get_sap(action)))
        board.do_action(action)

        # Initialize states and SAPs in actor and critic
        actor.init_saps_from_board(board)
        critic.init_state_from_board(board)

        reward = board.get_reward()
        optimal_action = actor.choose_action_epsilon(board)
        actor.set_elig_trace(board.get_sap(optimal_action), 1)
        delta = critic.calculate_td_error(episode_history[-1][0], board.get_state(), reward)
        critic.set_elig_trace(board.get_state(), 1) # (episode_history[-1][0], 1)
        for state_tuple in reversed(episode_history):
            critic.update_value_func(state_tuple[0], delta)
            critic.update_elig_trace(state_tuple[0])
            actor.update_policy(state_tuple[1], delta)
            actor.update_elig_trace(state_tuple[1])
        action = optimal_action
        end_state = board.is_end_state()
    result.append(board.get_num_stones())
    if board.get_num_stones() > 1:
        print(episode_history)
        for episode in episode_history:
            print("SAP policy value: ", actor.policy[episode[1]])
            print("state value function: ", critic.value_func[episode[0]])


plt.plot(result)
plt.show()
plt.savefig('30janrun.png')
