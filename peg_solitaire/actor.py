import random
from .board import Diamond
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
        self.policy[sap] = self.policy[sap] + self.alpha * delta * self.elig_trace[sap]

    def set_elig_trace(self, sap: str, value: float):
        """
        Sets the value of the state action pair in the eligibility trace dictionary
        :param sap: state action pair: str
        :param value: value of the sap: float
        """
        self.elig_trace[sap] = value

    def update_elig_trace(self, sap: str):
        self.elig_trace[sap] = self.gamma * self.epsilon * self.elig_trace[sap]

    def choose_action(self, board: Diamond):
        """
        Chooses the action with the highest desirability
        :param state: string representation of the state
        :return:
        """
        # Getting all state action pars from given state
        str_state = board.get_state()
        policies_from_state = list(filter(lambda key: key.startswith(str_state), self.policy.keys()))
        chosen_sap = random.choice(policies_from_state)
        return Action.create_action_from_string(chosen_sap[-6:])

    def init_saps_from_board_state(self, board: Diamond):
        current_saps = board.get_SAPS()
