import random
from .board import Board
from peg_solitaire.action import Action


class Actor:
    def __init__(self, alpha, gamma, epsilon, lambd):
        """
        Class representing the actor in the actor-critic model

        :param alpha: Learning rate
        :param gamma: Discount factor
        :param epsilon: Exploration rate (prob of taking random action)
        """
        self.policy = dict()
        self.elig_trace = dict()
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.lambd = lambd

    def set_policy(self, sap: str, value: float):
        """
        Sets the value of the state action pair in the policy dictionary
        :param sap: state action pair: str
        :param value: value of the sap: float
        """
        self.policy[sap] = value

    def update_policy(self, sap: str, delta: float):
        """
        Method updating the value of the policy for a given state action pair
        :param sap: State action pair
        :param delta: TD-Error
        """
        self.policy[sap] = self.policy.get(sap) + self.alpha * delta * self.elig_trace.get(sap)
        a = 1

    def set_elig_trace(self, sap: str, value: float):
        """
        Sets the value of the state action pair in the eligibility trace dictionary
        :param sap: state action pair: str
        :param value: value of the sap: float
        """
        self.elig_trace[sap] = value

    def update_elig_trace(self, sap: str):
        """
        :param sap: state action pair: str
        :return: the updated eligibility trace for the sap
        """
        self.elig_trace[sap] = self.gamma * self.lambd * self.elig_trace.get(sap)

    def choose_greedy_action(self, board: Board):
        """
        Choosing the action in the state action pair with the highest policy value
        :param board: board representing the state
        :return: the action object corresponding to the highest policy value from current state
        """

        # Get all sap strings from state
        policies = self.get_policies_from_state(board)
        # Filter policy to only contain the saps in policies
        filtered_policy_dict = { your_key: self.policy[your_key] for your_key in policies }
        # Get max value
        max_val = max(filtered_policy_dict.values())
        # If tie in max value; choose random among the tied
        keys = [key for key, value in filtered_policy_dict.items() if value == max_val]
        chosen_sap = random.choice(keys)
        #chosen_sap = max(self.get_policies_from_state(board), key=self.policy.get)
        return Action.create_action_from_string(chosen_sap[-6:])

    def choose_random_action(self, board: Board):
        chosen_sap = random.choice(self.get_policies_from_state(board))
        return Action.create_action_from_string(chosen_sap[-6:])

    def choose_epsilon_greedy_action(self, board: Board):
        """
        Chooses the action with the highest desirability with some exploration (epsilon)
        :param board: board representing the state
        :return: chosen action object
        """
        # temp fix:
        if board.is_end_state():
            return Action.create_action_from_string("000000")

        if random.random() < self.epsilon:
            return self.choose_random_action(board)
        else:
            return self.choose_greedy_action(board)

    def get_policies_from_state(self, board: Board):
        """
        :param board: board representing the state
        :return: list of SAPs from current state in policy
        """
        # Getting all state action pairs from given state
        str_state = board.get_state()
        return list(filter(lambda key: key.startswith(str_state), self.policy.keys()))

    def init_saps_from_board(self, board: Board):
        """
        Method for adding values to unseen state action pairs in policy and eligibility trace
        :param board: board representing the state
        """
        current_saps = board.get_saps()
        # Filter out saps already present in policy
        new_saps = list(filter(lambda key: key not in self.policy, current_saps))
        for sap in new_saps:
            self.set_policy(sap, 0.0)
