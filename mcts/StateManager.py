from abc import ABC, abstractmethod


class StateManager(ABC):
    @staticmethod
    @abstractmethod
    def generate_child_states(state: ([int], bool)):
        """
        Takes in a parent state and returns the child states from this state
        :param state: list representing state of game
        :return: list of lists representing the state of child states
        """

    @staticmethod
    @abstractmethod
    def init_game_state(**kwargs):
        """
        :param args: parameters for game
        :return: Initial state of game
        """

    @staticmethod
    @abstractmethod
    def is_end_state(state: ([int], bool)):
        """
        :param state: list representing state of game
        :return: a boolean stating if we are in end state
        """

    @staticmethod
    def state_to_string(state: ([int], bool)):
        key = ""
        for i in state[0]:
            key += str(i)
        key += str(state[1])
        return key

class Nim(StateManager):
    @staticmethod
    def generate_child_states(state: ([int], bool)):
        return [[i, state[0][1]] for i in range(state[0][0] - 1, state[0][0] - state[0][1], -1)]

    @staticmethod
    def init_game_state(**kwargs):
        return [kwargs.get('N'), kwargs.get('K')]

    @staticmethod
    def is_end_state(state: ([int], bool)):
        return state[0][0] == 0


class Lodge(StateManager):
    @staticmethod
    def generate_child_states(state: ([int], bool)):
        states = []
        if state[0][0] > 0:
            states.append(([0]+state[0][1:], not state[1]))
        for j in range(len(state[0])-1, 0, -1):
            if state[0][j] == 0:
                continue
            i = j - 1
            while state[0][i] == 0 and i >= 0:
                copy_state = state.copy()
                copy_state[0][i] = copy_state[0][j]
                copy_state[0][j] = 0
                copy_state[1] = not copy_state[1]
                states.append(copy_state)
                i -= 1
        return states

    @staticmethod
    def init_game_state(**kwargs):
        return kwargs.get('B_init')

    @staticmethod
    def is_end_state(state: ([int], bool)):
        return state[0][0] == 2
