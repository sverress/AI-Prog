import unittest

from hex.GameVisualizer import GameVisualizer
from hex.StateManager import StateManager


class TestStateManager(unittest.TestCase):
    def setUp(self) -> None:
        self.state_manager = StateManager(8, 1)
        self.valid_action = "0,0:1"

    def test_build_board(self):
        # Check board shape
        self.assertSequenceEqual(
            self.state_manager.board.shape,
            (self.state_manager.board_size, self.state_manager.board_size),
        )

    def test_check_and_extract_action_string(self):
        self.assertEqual(
            self.state_manager.check_and_extract_action_string(self.valid_action),
            (0, 0, 1),
        )

    def test_perform_action(self):
        # Test update of board and state
        correct_board_string = "1" + (":" + str(2)).zfill(
            self.state_manager.board_size ** 2 + 1
        )
        self.state_manager.perform_action(self.valid_action)
        self.assertEqual(self.state_manager.board[0, 0], 1)
        self.assertEqual(self.state_manager.get_state(), correct_board_string)
        # Do some moves
        self.state_manager.perform_action("3,3:2")
        self.state_manager.perform_action("2,3:1")
        self.state_manager.perform_action("3,2:2")
        # Check that the moves are in the graphs
        self.assertSequenceEqual(list(self.state_manager.P2graph.nodes), ["3,3:2", "3,2:2"])
        self.assertSequenceEqual(list(self.state_manager.P1graph.nodes), ["0,0:1", "2,3:1"])
        # Check that there is an edge between the two adjacent pieces
        self.assertTrue(self.state_manager.P2graph.has_edge("3,3:2", "3,2:2"))
        # There should not be an edge between the nodes of the other player
        self.assertFalse(self.state_manager.P1graph.has_edge("0,0:1", "2,3:1"))

