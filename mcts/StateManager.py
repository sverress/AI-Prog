from abc import ABC, abstractmethod


class StateManager(ABC):
    """
    ABSTRACT CLASS FOR STATE MANAGER
    """
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
    @abstractmethod
    def pretty_state_string(state: ([int], bool), **kwargs):
        """
        Game specific string representation of state
        :param state: list representing state of game
        :return: string representation
        """

    @staticmethod
    @abstractmethod
    def get_move_string(prev_state: ([int], bool), state: ([int], bool)):
        """
        :param prev_state: list representing the previous state of game
        :param state: list representing state of game
        :return: string to be presented in verbose mode
        """

    @staticmethod
    def copy_state(state: ([int], bool)):
        return state[0].copy(), state[1]

    @staticmethod
    def state_to_key(state: ([int], bool)):
        """
        Converts the state to a compact string representation
        :param state: list representing state of game
        :return: compact string representation
        """
        list_string = ""
        for char in state[0]:
            list_string += str(char)
        return f"{list_string}{str(state[1])}"


class Nim(StateManager):
    @staticmethod
    def get_move_string(prev_state: ([int], bool), state: ([int], bool)):
        return f"removed {prev_state[0][0] - state[0][0]} pieces"

    @staticmethod
    def generate_child_states(state: ([int], bool)):
        if Nim.is_end_state(state):
            return []
        min_remaining_pieces = state[0][0] - state[0][1]
        min_remaining_pieces = min_remaining_pieces if min_remaining_pieces > 0 else 0
        return_statement = [([i, state[0][1]], not state[1]) for i in range(state[0][0] - 1, min_remaining_pieces - 1, -1)]
        return return_statement

    @staticmethod
    def init_game_state(**kwargs):
        return [kwargs.get('N'), kwargs.get('K')], kwargs.get('P')

    @staticmethod
    def is_end_state(state: ([int], bool)):
        return state[0][0] == 0

    @staticmethod
    def pretty_state_string(state: ([int], bool), **kwargs):
        output = f"Remaining pieces: {state[0][0]}"
        if kwargs.get('include_max', False):
            output += f" (Max number of removed pieces per move: {state[0][1]}) "
        return output


class Lodge(StateManager):
    @staticmethod
    def get_move_string(prev_state: ([int], bool), state: ([int], bool)):
        if prev_state[0][0] - state[0][0] == 1:
            return "picks up copper"
        # Find changed indices
        indices = [i for i in range(len(state[0])) if state[0][i] != prev_state[0][i]]
        # Determine type of piece
        moved_piece = "gold" if prev_state[0][indices[1]] == 2 else "copper"
        return f"moves {moved_piece} from cell {indices[1]} to {indices[0]}"

    @staticmethod
    def generate_child_states(state: ([int], bool)):
        states = []
        if Lodge.is_end_state(state):
            return []
        if state[0][0] > 0:
            states.append(([0]+state[0][1:], not state[1]))
        for j in range(len(state[0])-1, 0, -1):
            if state[0][j] == 0:
                continue
            i = j - 1
            while state[0][i] == 0 and i >= 0:
                copy_list_state = state[0].copy()
                copy_list_state[i] = copy_list_state[j]
                copy_list_state[j] = 0
                states.append((copy_list_state, not state[1]))
                i -= 1
        return states

    @staticmethod
    def init_game_state(**kwargs):
        return kwargs.get('B_init'), kwargs.get('p')

    @staticmethod
    def is_end_state(state: ([int], bool)):
        return state[0][0] == 2

    @staticmethod
    def pretty_state_string(state: ([int], bool), **kwargs):
        return str(state[0])

