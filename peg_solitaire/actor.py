import random
from .board import Board
from peg_solitaire.action import Action


class Actor:
    def __init__(self, alpha, gamma, epsilon):
        self.policy = dict()
        self.elig_trace = dict()
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

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
        self.policy[sap] += self.alpha * delta * self.elig_trace[sap]

    def set_elig_trace(self, sap: str, value: float):
        """
        Sets the value of the state action pair in the eligibility trace dictionary
        :param sap: state action pair: str
        :param value: value of the sap: float
        """
        self.elig_trace[sap] = value

    def update_elig_trace(self, sap: str):
        self.elig_trace[sap] = self.gamma * self.epsilon * self.elig_trace[sap]

    def choose_random_action(self, board: Board):
        """
        Chooses the action with the highest desirability
        :param board:
        :return: chosen action object
        """
        # Getting all state action pars from given state
        str_state = board.get_state()
        policies_from_state = list(filter(lambda key: key.startswith(str_state), self.policy.keys()))
        chosen_sap = random.choice(policies_from_state)
        return Action.create_action_from_string(chosen_sap[-6:])

    def choose_action_epsilon(self, board: Board):
        """
        Chooses the action with the highest desirability
        :param board:
        :return: chosen action object
        """
        # temp fix:
        if board.is_end_state():
            return Action.create_action_from_string("000000")

        # Getting all state action pairs from given state
        str_state = board.get_state()
        policies_from_state = list(filter(lambda key: key.startswith(str_state), self.policy.keys()))
        if random.random() < self.epsilon:
            chosen_sap = random.choice(policies_from_state)
            return Action.create_action_from_string(chosen_sap[-6:])
        else:
            sorted_saps = sorted(policies_from_state, key=self.policy.get, reverse=True)
            return Action.create_action_from_string(sorted_saps[0][-6:])

    def init_saps_from_board(self, board: Board):
        current_saps = board.get_saps()
        # Filter out saps already present in policy
        new_saps = list(filter(lambda key: key not in self.policy, current_saps))
        for sap in new_saps:
            self.set_policy(sap, 0)
            self.set_elig_trace(sap, 0)  # Should have separate "already present"-check for this?
