import random
from .board import Diamond

class Actor:
    def __init__(self, initial_board):
        self.policy = dict()
        self.elig_trace = dict()

    def update_policy(self, sap, value):
        self.policy[sap] = value

    def choose_action_greedy(self, state):
        return self.policy.get[state]

    def choose_action_epsilon_greedy(self, board, epsilon):
        if random.uniform(0, 1) < epsilon:
            return random.randint(1, 4)

        return self.policy.get[state]
