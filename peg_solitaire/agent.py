from peg_solitaire.board import Triangle, Diamond
from peg_solitaire.actor import Actor
from peg_solitaire.critic import Critic
from peg_solitaire.action import Action
from peg_solitaire.helpers import *
import copy
from matplotlib import pyplot as plt
import json
import time


class Agent:
    def __init__(self, parameters):
        # Init parameters from parameter dict
        self.board_type = None
        self.open_positions = []
        self.board_size = 3
        self.num_episodes = None
        # Exploration rate (prob of taking random action)
        self.epsilon = None
        # Learning rate
        self.alpha_a = None
        self.alpha_c = None
        # Trace decay factor
        self.lambd = None
        # Discount factor
        self.gamma = None
        self.epsilon_decay_rate = None
        self.frame_rate = None
        # Neural net parameters
        self.use_nn = False
        self.layers = None
        self.autoplay = None
        self.__dict__ = parameters
        # Converting string lists to tuple lists
        self.open_positions = convert_string_list_to_tuple_list(self.open_positions)
        # Init board
        if self.board_type == "diamond":
            self.init_board = Diamond(self.board_size, self.open_positions)
            self.board = copy.deepcopy(self.init_board)
        elif self.board_type == "triangle":
            self.init_board = Triangle(self.board_size, self.open_positions)
            self.board = copy.deepcopy(self.init_board)
        else:
            raise ValueError("board_type should be a string with either diamond or triangle")

        self.create_critic()

        # Initialize actor
        self.actor = Actor(self.alpha_a, self.gamma, self.epsilon, self.lambd)
        # Initialize all SAPs from init state in policy
        self.actor.init_saps_from_board(self.init_board)

    def create_critic(self):
        # Initialize critic
        self.critic = Critic(self.gamma, self.alpha_c, self.lambd)
        if self.use_nn:
            self.critic.init_nn(self.layers, self.init_board.get_num_tiles())
        else:
            # Initialize state in value function
            self.critic.init_state_from_board(self.init_board)

    @staticmethod
    def create_agent_from_config_file(config_file_path):
        """
        Method for creating agents from config file
        :param config_file_path: path to json config file
        :return: new Agent object
        """
        with open(config_file_path) as json_file:
            data = json.load(json_file)
            return Agent(data)

    def do_action(self, action: Action):
        """
        Does action s -> s' on board making the board object represent the new state s'
        :param action: action object
        """
        self.board.do_action(action)
        # Initialize states and SAPs in self.actor and self.critic
        self.actor.init_saps_from_board(self.board)
        self.critic.init_state_from_board(self.board)

    def train(self, plot_result=True, log=False):
        """
        Train agent to find optimal solution from given init state
        :param plot_result: true for plot remaining pegs against episode number: bool
        :param log: bool
        """
        result = []
        interval = 20
        print_loader(0, self.num_episodes, interval)
        train_start_time = time.time()
        for i in range(1, self.num_episodes+1):
            # See progress
            episode_start_time = time.time()
            runtimes = []
            if i % interval == 0:
                print_loader(i, self.num_episodes, interval)
                self.actor.epsilon = self.actor.epsilon * self.epsilon_decay_rate

            # Return to init board
            current_state = copy.deepcopy(self.init_board)
            # Choose action
            current_state_action = self.actor.choose_epsilon_greedy_action(current_state)
            # Reset eligibilities
            self.actor.elig_trace.clear()
            self.critic.elig_trace.clear()

            episode_history = []
            end_state = False
            while not end_state:

                episode_history.append((current_state.get_state(), current_state.get_sap(current_state_action)))

                # Do action a from state s, moving the system to state s’ and receiving reinforcement r
                next_state = copy.deepcopy(current_state)  # s' in pseudocode
                next_state.do_action(current_state_action)

                # Initialize new SAPs in policy
                self.actor.init_saps_from_board(next_state)
                if not self.use_nn:
                    # Initialize new state in value function
                    self.critic.init_state_from_board(next_state)

                    # (the critic needs state-based eligibilities)
                    self.critic.set_eligibility_trace(current_state.get_state(), 1)

                # Get reward from state s'
                reward = next_state.get_reward()

                # The action dictated by the current policy for state s’
                next_state_action = self.actor.choose_epsilon_greedy_action(next_state)

                # (the actor keeps SAP-based eligibilities)
                self.actor.set_elig_trace(current_state.get_sap(current_state_action), 1)

                # Calculate TD-error
                delta = self.critic.calculate_td_error(current_state.get_state(), next_state.get_state(), reward)


                # Update policy and value function for previous states in episode
                for state, sap in reversed(episode_history):
                    self.critic.update_value_func(state, delta, runtimes)
                    if not self.use_nn:
                        self.critic.update_eligibility_trace(state)
                    self.actor.update_policy(sap, delta)
                    self.actor.update_elig_trace(sap)

                # Move to next state s'
                current_state_action = next_state_action
                end_state = next_state.is_end_state()
                current_state = next_state

            result.append(current_state.get_num_stones())
            episode_end_time = time.time()
            #print(f'total_{i}: {episode_end_time-episode_start_time}, sum: {sum(runtimes)} percent: {sum(runtimes)/(episode_end_time-episode_start_time)}')

            if log and current_state.get_num_stones() == 1:
                print('---------------------')
                for episode in episode_history:
                    saps = list(filter(lambda key: key.startswith(episode[0]), self.actor.policy.keys()))
                    for sap in saps:
                        print('action: ', self.actor.policy.get(sap))
                    print("SAP policy value: ", self.actor.policy[episode[1]])
                    print("state value function: ", self.critic.get_state_value(episode[0]))
        if plot_result:
            plt.plot(result)
            plt.xlabel('Episodes')
            plt.ylabel('Remaining pegs')
            plt.show()
        train_end_time = time.time()
        print(f"training finished. Time elapsed: {train_end_time-train_start_time}")