class Critic:

    def __init__(self):
        self.valueFunc = dict()
        self.elig_trace = dict()

    def calculate_TDerror(self, reward, gamma):
        """
        :param  alpha: learning rate: float [0,1]
                gamma: discount factor: float [0,1]
                lamb: trace-decay factor: float [0,1]
        :return: the TD error related to the prev and current state
        """
        # TD error: delta

        delta = reward + gamma * self.valueFunc(childState) - self.valueFunc(state)

        return delta

    def update_value_func(self, state, value):
        self.valueFunc[state] = value

    def update_elig_trace(self, state, action, value):
        self.valueFunc[state] = value

# eligibility trace

# elig_trace(state) = gamma * lam

# Updated value function

# V(state) = V(state) + alpha*delta*elig_trace(state)