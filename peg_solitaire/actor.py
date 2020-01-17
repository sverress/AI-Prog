import random


class Actor:
    def __init__(self):
        self.policy = dict()

    def update_policy(self, state, action, alpha, delta, ):
        if delta < 0:
            self.policy[(state, action)] = self.policy[(state, action)] + alpha * delta * eligibility[(state, action)]

    def choose_action_greedy(self, state):
        return self.policy.get[state]

    def choose_action_epsilon_greedy(self, state, epsilon):
        if random.uniform(0, 1) < epsilon:
            return random.randint(1, 4)

        return self.policy.get[state]


if __name__ == '__main__':