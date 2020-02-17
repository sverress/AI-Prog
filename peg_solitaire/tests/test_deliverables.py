import unittest
from peg_solitaire.agent import Agent


class TestConvergence:
    def check_convergence(self):
        while not self.agent.board.is_end_state():
            action = self.agent.actor.choose_greedy_action(self.agent.board)
            self.agent.do_action(action)
        self.assertEqual(self.agent.board.get_reward(), 1)

    def print_agent(self):
        with_string = "with" if self.agent.use_nn else "without"
        print(f"Testing {self.agent.board_type}_{self.agent.board_size} {with_string} neural network")

    def redefine_params_if_nn(self):
        if self.agent.use_nn:
            self.agent.alpha_c = 0.01
            self.agent.num_episodes = 150
            self.agent.create_critic()

    def test_convergence_table(self):
        self.agent.use_nn = False
        self.print_agent()
        self.agent.train(plot_result=False)
        self.check_convergence()

    def test_convergence_nn(self):
        self.agent.use_nn = True
        self.print_agent()
        self.agent.train(plot_result=False)
        self.check_convergence()


class TestDiamondLeft(unittest.TestCase, TestConvergence):
    def setUp(self):
        self.agent = Agent.create_agent_from_config_file("peg_solitaire/parameters/diamond_4_left_middle.json")


class TestDiamondRight(unittest.TestCase, TestConvergence):
    def setUp(self):
        self.agent = Agent.create_agent_from_config_file("peg_solitaire/parameters/diamond_4_right_middle.json")


class TestTriangle21(unittest.TestCase, TestConvergence):
    def setUp(self):
        self.agent = Agent.create_agent_from_config_file("peg_solitaire/parameters/triangle_5_21.json")
        self.redefine_params_if_nn()


class TestTriangle31(unittest.TestCase, TestConvergence):
    def setUp(self):
        self.agent = Agent.create_agent_from_config_file("peg_solitaire/parameters/triangle_5_31.json")
        self.redefine_params_if_nn()


class TestTriangle32(unittest.TestCase, TestConvergence):
    def setUp(self):
        self.agent = Agent.create_agent_from_config_file("peg_solitaire/parameters/triangle_5_32.json")
        self.redefine_params_if_nn()


if __name__ == '__main__':
    unittest.main()
