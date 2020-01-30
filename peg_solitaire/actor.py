import random
from board import *

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

    def choose_action(self, state: str):
        """
        Chooses the action with the highest desirability
        :param state: string representation of the state
        :return:
        """
        # Getting all state action pars from given state
        policies_from_state = list(filter(lambda key: key.starts_width(state), self.policy.keys()))
        filtered_policy = self.policy[policies_from_state]
        raise NotImplemented()


