import json
from peg_solitaire.board import Board, Triangle, Diamond
from peg_solitaire.actor import Actor
from peg_solitaire.critic import Critic
import copy
from matplotlib import pyplot as plt


class Agent:
    def __init__(self, parameters, board_type: str):
        # Init parameters from parameter dict
        self.open_positions = []
        self.board_size = 3
        self.num_episodes = None
        self.epsilon = None
        self.alpha_a = None
        self.lambd = None
        self.alpha_c = None
        self.gamma = None
        self.__dict__ = parameters
        self.open_positions = [(int(string_pos[0]), int(string_pos[1])) for string_pos in self.open_positions]
        # Init board
        if board_type == "diamond":
            self.init_board = Diamond(self.board_size, self.open_positions)
        elif board_type == "triangle":
            self.init_board = Triangle(self.board_size, self.open_positions)
        else:
            raise ValueError("board_type should be a string with either diamond or triangle")

        # Initialize critic
        self.critic = Critic(self.gamma, self.alpha_c, self.lambd)
        self.critic.init_state_from_board(self.init_board)

        # Initialize actor
        self.actor = Actor(self.alpha_a, self.gamma, self.epsilon)
        # Initialize all SAPs from init state
        self.actor.init_saps_from_board(self.init_board)

    @staticmethod
    def create_agent_from_config_file(config_file_path, board_type: str):
        """
        Method for creating agents from config file
        :param board_type:
        :param config_file_path: path to json config file
        :return: new Agent object
        """
        with open(config_file_path) as json_file:
            data = json.load(json_file)
            return Agent(data, board_type)

    def train(self, plot_result=True, log=False):
        result = []

        for i in range(self.num_episodes):
            # See progress
            if i % 50 == 0:
                print(i)
                self.actor.epsilon = self.actor.epsilon * 0.8
            board = copy.deepcopy(self.init_board)
            action = self.actor.choose_action_epsilon(board)
            episode_history = []
            end_state = False
            while not end_state:
                episode_history.append((board.get_state(), board.get_sap(action)))
                board.do_action(action)

                # Initialize states and SAPs in self.actor and self.critic
                self.actor.init_saps_from_board(board)
                self.critic.init_state_from_board(board)

                reward = board.get_reward()
                optimal_action = self.actor.choose_action_epsilon(board)
                self.actor.set_elig_trace(board.get_sap(optimal_action), 1)
                delta = self.critic.calculate_td_error(episode_history[-1][0], board.get_state(), reward)
                self.critic.set_elig_trace(board.get_state(), 1)  # (episode_history[-1][0], 1)
                for state_tuple in reversed(episode_history):
                    self.critic.update_value_func(state_tuple[0], delta)
                    self.critic.update_elig_trace(state_tuple[0])
                    self.actor.update_policy(state_tuple[1], delta)
                    self.actor.update_elig_trace(state_tuple[1])
                action = optimal_action
                end_state = board.is_end_state()
            result.append(board.get_num_stones())

            if board.get_num_stones() > 1 and log:
                print(episode_history)
                for episode in episode_history:
                    print("SAP policy value: ", self.actor.policy[episode[1]])
                    print("state value function: ", self.critic.value_func[episode[0]])
        if plot_result:
            plt.plot(result)
            plt.show()
            plt.savefig('30janrun.png')


agent = Agent.create_agent_from_config_file("config.json", "diamond")
agent.train()
