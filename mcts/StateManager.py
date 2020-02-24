from abc import ABC, abstractmethod


class StateManager(ABC):
    @staticmethod
    @abstractmethod
    def generate_child_states(state: [int]):
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
    def is_end_state(state: [int]):
        """
        :param state: list representing state of game
        :return: a boolean stating if we are in end state
        """


class Nim(StateManager):
    @staticmethod
    def generate_child_states(state: [int]):
        return [[i, state[1]] for i in range(state[0] - 1, state[0]-state[1], -1)]

    @staticmethod
    def init_game_state(**kwargs):
        return [kwargs['N'], kwargs['K']]

    @staticmethod
    def is_end_state(state: [int]):
        return state[0] == 0


class Lodge(StateManager):
    @staticmethod
    def generate_child_states(state: [int]):
        states = []
        if state[0] > 0:
            states.append([0]+state[1:])
        for j in range(len(state)-1, 0, -1):
            if state[j] == 0:
                continue
            i = j - 1
            while state[i] == 0 and i >= 0:
                copy_state = state.copy()
                copy_state[i] = copy_state[j]
                copy_state[j] = 0
                states.append(copy_state)
                i -= 1
        return states

    @staticmethod
    def init_game_state(**kwargs):
        return kwargs.get('B_init')

    @staticmethod
    def is_end_state(state: [int]):
        return state[0] == 2
