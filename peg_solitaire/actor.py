import random
from .board import Diamond

class Actor:
    def __init__(self):
        self.policy = dict()
        self.elig_trace = dict()

    def set_policy(self, sap: str, value: float):
        self.policy[sap] = value

    def update_policy


    def set_elig_trace(self, sap: str, value: float):
        self.elig_trace[sap] = value

    def update_elig_trace(self):

    def choose_action_greedy(self, state):
        return self.policy.get[state]

    def choose_action_epsilon_greedy(self, board, epsilon):


