import unittest
import networkx as nx
from hex.StateManager import StateManager


class TestBigStateManager(unittest.TestCase):
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
        self.assertSequenceEqual(
            list(self.state_manager.P2graph.nodes), ["3,3:2", "3,2:2"]
        )
        self.assertSequenceEqual(
            list(self.state_manager.P1graph.nodes), ["0,0:1", "2,3:1"]
        )
        # Check that there is an edge between the two adjacent pieces
        self.assertTrue(self.state_manager.P2graph.has_edge("3,3:2", "3,2:2"))
        # There should not be an edge between the nodes of the other player
        self.assertFalse(self.state_manager.P1graph.has_edge("0,0:1", "2,3:1"))

    def test_generate_possible_actions(self):
        # Creating list of tuple with state and corresponding number of possible states
        state_list = [
            (self.state_manager.get_state(), self.state_manager.board_size ** 2,),
            ("1" * 60 + "0" * 4 + ":1", 4),
        ]
        for state_tuple in state_list:
            self.assertEqual(
                len(self.state_manager.generate_possible_actions(state_tuple[0])),
                state_tuple[1],
            )
        # checking if the actions are correct
        self.assertEqual(
            self.state_manager.generate_possible_actions(("10" + "1" * 62 + ":2")),
            ["0,1:2"],
        )
        self.assertSequenceEqual(
            self.state_manager.generate_possible_actions(("1" * 61 + "001:1")),
            ["7,5:1", "7,6:1"],
        )

    def test_generate_child_states(self):
        initial_state = self.state_manager.get_state()
        # checking number of child states
        self.assertEqual(
            len(self.state_manager.generate_child_states(initial_state)),
            self.state_manager.board_size ** 2,
        )
        self.assertEqual(
            len(self.state_manager.generate_child_states("2" * 63 + "0:1")), 1
        )
        # Check that the player switches
        self.assertEqual(
            self.state_manager.generate_child_states("2" * 63 + "0:1")[0][-1], "2"
        )
        self.assertEqual(
            self.state_manager.generate_child_states("2" * 63 + "0:2")[0][-1], "1"
        )
        # Checking that output is correct
        self.assertSequenceEqual(
            self.state_manager.generate_child_states("2" * 63 + "0:1"),
            ["2" * 63 + "1:2"],
        )
        self.assertSequenceEqual(
            self.state_manager.generate_child_states("2" * 30 + "00" + "1" * 32 + ":2"),
            ["2" * 30 + "20" + "1" * 32 + ":1", "2" * 30 + "02" + "1" * 32 + ":1"],
        )

    def test_set_state_manager(self):
        initial_state = (
            "2112102122011010211221002101022212201222022111011220021110221001:1"
        )
        self.state_manager.set_state_manager(initial_state)
        path2 = [
            "0,0:2",
            "1,0:2",
            "2,0:2",
            "3,0:2",
        ]
        path1 = [
            "0,4:1",
            "1,3:1",
            "2,2:1",
            "3,1:1",
            "4,0:1",
        ]

        # Check some of the paths in the state
        def check_path(path, correct_graph, invalid_graph):
            for i in range(len(path) - 1):
                self.assertTrue(correct_graph.has_edge(path[i], path[i + 1]))
                self.assertFalse(invalid_graph.has_edge(path[i], path[i + 1]))
            self.assertTrue(nx.has_path(correct_graph, path[0], path[-1]))

        check_path(path2, self.state_manager.P2graph, self.state_manager.P1graph)
        check_path(path1, self.state_manager.P1graph, self.state_manager.P2graph)

    def test_is_end_state(self):
        end_state_p1 = (
            "2112102122011010211221002101022212201222122111011220021110221001:2"
        )
        self.state_manager.set_state_manager(end_state_p1)
        self.assertTrue(self.state_manager.is_end_state())

    def test_convert_flattened_index_to_cords(self):
        # index 8 should be second row first col
        self.assertSequenceEqual(
            self.state_manager.convert_flattened_index_to_cords(8), (1, 0)
        )
        self.assertSequenceEqual(
            self.state_manager.convert_flattened_index_to_cords(18), (2, 2)
        )


class TestSmallStateManager(unittest.TestCase):
    def setUp(self) -> None:
        self.state_manager = StateManager(3, 1)
        self.valid_action = "0,0:1"

    def test_is_end_state(self):
        end_state_p1 = (
            "121000221:2"
        )
        self.state_manager.set_state_manager(end_state_p1)
        self.assertFalse(self.state_manager.is_end_state())

