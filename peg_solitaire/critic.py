from peg_solitaire.board import Board
import random

class Critic:

    def __init__(self, gamma, alpha, lambd):
        self.value_func = dict()
        self.elig_trace = dict()
        self.gamma = gamma # Discount factor
        self.alpha = alpha # Learning rate
        self.lambd = lambd # Trace-decay factor

    def calculate_TDerror(self, parent_state: str, child_state: str, reward: float):
        """
        Calculates the Temporal Difference error denoted delta
        :param parent_state: Previous state: str
        :param child_state: Current state: str
        :param reward: Reward from going to "child state": float
        :return: the TD error; delta
        """

        delta = reward + self.gamma * self.get_state_value(child_state) - self.get_state_value(parent_state)

        return delta

    def set_value_func(self, state, value):
        self.value_func[state] = value

    def set_elig_trace(self, state, value):
        self.elig_trace[state] = value

    def get_state_value(self, state: str):
        """
        Fetch the state value from the value function by state key.
        :param state: state key: str
        :return: state value: float
        """
        try:
            return self.value_func[state]
        except IndexError:
            self.update_value_func(state, random.uniform(0, 0.2))
            return self.value_func[state]

    def get_elig_trace_value(self, state: str):
        return self.elig_trace[state]

    def update_value_func(self, state: str, delta: float):
        """
        Finds and sets the new state value to the value func dict
        :param state: str representation of string
        :param delta: TD-error
        """
        state_value = self.get_state_value(state)
        elig_trace_value = self.get_elig_trace_value(state)
        new_state_value = state_value + self.alpha*delta*elig_trace_value
        self.set_value_func(state, new_state_value)

    def update_elig_trace(self, state: str):
        """
        Finds and sets the eligibility trace value to the elig_trace dict
        :param state: str representation of string
        :param delta: TD-error
        """
        elig_trace_value = self.get_elig_trace_value(state)
        new_elig_trace_value = self.gamma*self.lambd*elig_trace_value
        self.set_elig_trace(state, new_elig_trace_value)