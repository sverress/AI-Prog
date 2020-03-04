from abc import ABC, abstractmethod


class StateManager(ABC):
    """
    ABSTRACT CLASS FOR STATE MANAGER
    Class uses internal representation of state ([int], bool) to make computations.
    All communication with the outside is done with string representations
    """
    @staticmethod
    @abstractmethod
    def generate_child_states(state: str) -> [str]:
        """
        Takes in a parent state and returns the child states from this state
        :param state: string representing state of game
        :return: list of strings representing child states
        """

    @staticmethod
    @abstractmethod
    def init_game_state(**kwargs) -> str:
        """
        :param kwargs: parameters for game
        :return: string rep of all
        """

    @staticmethod
    @abstractmethod
    def is_end_state(state: str) -> str:
        """
        :param state: string representing state of game
        :return: a boolean stating if state is end state
        """

    @staticmethod
    @abstractmethod
    def pretty_state_string(state: str, **kwargs) -> str:
        """
        Game specific string representation of state
        :param state: string representing state of game
        :return: string representation
        """

    @staticmethod
    @abstractmethod
    def get_move_string(prev_state: str, state: str) -> str:
        """
        :param prev_state: string representing the previous state of game
        :param state: string representing state of game
        :return: string to be presented in verbose mode
        """

    @staticmethod
    def _get_internal_state_rep(state: str) -> ([int], bool):
        """
        Method to be used by subclass to convert from string state rep to internal representation
        :param state: string representing state of game
        :return: internal state representation
        """
        state_str, player_str = state.split(":")
        return [int(cell) for cell in state_str], player_str == "1"

    @staticmethod
    def _get_external_state_rep(state: ([int], bool)) -> str:
        """
        External representation format ´<state/board>:<player nr.>´
        :param state: internal representation of state
        :return: external representation of state
        """
        output = ""
        for cell in state[0]:
            output += str(cell)
        output += "1" if state[0] else "2"
        return output


class Nim(StateManager):
    @staticmethod
    def init_game_state(**kwargs) -> str:
        return StateManager._get_external_state_rep(([kwargs.get('N'), kwargs.get('K')], kwargs.get('P')))

    @staticmethod
    def is_end_state(state: str) -> bool:
        [remaining_pieces, max_to_remove], player = StateManager._get_internal_state_rep(state)
        return remaining_pieces == 0

    @staticmethod
    def get_move_string(prev_state: str, state: str) -> str:
        [prev_remaining_pieces, max_to_remove], player = StateManager._get_internal_state_rep(prev_state)
        [current_remaining_pieces, max_to_remove], player = StateManager._get_internal_state_rep(state)
        return f"removed {prev_remaining_pieces - current_remaining_pieces} pieces"

    @staticmethod
    def generate_child_states(state: str) -> [str]:
        if Nim.is_end_state(state):
            return []
        [remaining_pieces, max_to_remove], player = StateManager._get_internal_state_rep(state)
        min_remaining_pieces = remaining_pieces - max_to_remove
        min_remaining_pieces = min_remaining_pieces if min_remaining_pieces > 0 else 0
        return_statement = [([i, max_to_remove], not player) for i in range(remaining_pieces - 1, min_remaining_pieces - 1, -1)]
        return [StateManager._get_external_state_rep(child_state) for child_state in return_statement]

    @staticmethod
    def pretty_state_string(state: str, **kwargs) -> str:
        [remaining_pieces, max_to_remove], player = StateManager._get_internal_state_rep(state)
        output = f"Remaining pieces: {remaining_pieces}"
        if kwargs.get('include_max', False):
            output += f" (Max number of removed pieces per move: {max_to_remove}) "
        return output


class Ledge(StateManager):
    @staticmethod
    def get_move_string(prev_state: str, state: str) -> str:
        prev_board, prev_player = StateManager._get_internal_state_rep(prev_state)
        current_board, current_player = StateManager._get_internal_state_rep(state)
        if prev_board[0] - current_board[0] == 1:
            return "picks up copper"
        # Find changed indices
        from_cell_index, to_cell_index = [i for i in range(len(current_board)) if current_board[i] != prev_board[i]]
        # Determine type of piece
        moved_piece_string = "gold" if prev_board[from_cell_index] == 2 else "copper"
        return f"moves {moved_piece_string} from cell {from_cell_index} to {to_cell_index}"

    @staticmethod
    def generate_child_states(state: str) -> [str]:
        states = []
        if Ledge.is_end_state(state):
            return []
        board, player = StateManager._get_internal_state_rep(state)
        if board[0] > 0:
            states.append(([0]+board[1:], not player))
        for j in range(len(board)-1, 0, -1):
            if board[j] == 0:
                continue
            i = j - 1
            while state[0][i] == 0 and i >= 0:
                copy_list_state = board.copy()
                copy_list_state[i] = copy_list_state[j]
                copy_list_state[j] = 0
                states.append((copy_list_state, not state[1]))
                i -= 1
        return [StateManager._get_external_state_rep(in_state)for in_state in states]

    @staticmethod
    def init_game_state(**kwargs):
        return StateManager._get_external_state_rep((kwargs.get('B_init'), kwargs.get('p')))

    @staticmethod
    def is_end_state(state: str) -> bool:
        board, player = StateManager._get_internal_state_rep(state)
        return board[0] == 2

    @staticmethod
    def pretty_state_string(state: str, **kwargs) -> str:
        board, player = StateManager._get_internal_state_rep(state)
        return str(board)

