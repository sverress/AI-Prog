import unittest
from hex.MCTS import MCTS
from hex.StateManager import StateManager


class TestConstants:
    K = 4
    STARTING_PLAYER = 1


class MockActorNet:
    def __init__(self):
        self.prediction = 0


class TestMCTS(unittest.TestCase):
    def setUp(self) -> None:
        self.state_manager = StateManager(
            TestConstants.K, TestConstants.STARTING_PLAYER
        )
        self.a_net = MockActorNet()

        self.mcts = MCTS(self.state_manager, self.a_net)
        init_state = self.state_manager.get_state()
        self.changed_index = 3
        self.visited_state = f"{init_state[:self.changed_index]}{TestConstants.STARTING_PLAYER}" \
                             f"{init_state[self.changed_index+1:-1]}" \
                             f"{StateManager.get_opposite_player(TestConstants.STARTING_PLAYER)}"
        self.root_child_states = self.state_manager.generate_child_states(init_state)
        # Building first layer of tree
        for child in self.root_child_states:
            print(child)
            self.mcts.tree.add_state_node(child)
            self.mcts.tree.add_edge(init_state, child)

    def test_get_distribution(self):
        self.mcts.tree.increment_state_number_of_visits(self.visited_state)
        distribution = self.mcts.get_distribution(self.state_manager.get_state())
        # If there is only one visited state it should have the whole distribution
        self.assertEqual(distribution[self.changed_index], 1)
        self.mcts.tree.increment_state_number_of_visits(self.root_child_states[8])



