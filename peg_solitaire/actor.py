import random
from .board import Diamond

class Actor:
    def __init__(self, initial_board):
        self.policy = dict()
        self.elig_trace = dict()

    def update_policy(self, state, action, alpha, delta, ):
        if delta < 0:
            self.policy[(state, action)] = self.policy[(state, action)] + alpha * delta * eligibility[(state, action)]

    def add_SAPs(self, board, actions):
        for a in actions:
            sap = board.get_sap()
            self.policy[]

    def choose_action_greedy(self, state):
        return self.policy.get[state]

    def choose_action_epsilon_greedy(self, state, epsilon):
        if random.uniform(0, 1) < epsilon:
            return random.randint(1, 4)

        return self.policy.get[state]
