from hex.GameSimulator import GameSimulator, StartingPlayerOptions
from hex.TOPP import TOPP
from libs.helpers import Timer

"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 60  # number of games in a batch
P = StartingPlayerOptions.P2  # starting-player option
M = 1500  # number of simulations (and hence rollouts) per actual game move.
verbose = True
max_tree_height = 6
c = 1.2

# SETTINGS FOR HEX
k = 4  # board size kxk, 3 <= k <= 10

TOPP.delete_models()

training_timer = Timer(start=True)

# TRAIN AGAINST SELF
game = GameSimulator(G, P, M, verbose, max_tree_height, c, k, print_parameters=True)
game.run()

training_timer.stop()
print(f"Training time elapsed: {training_timer.time_str()}")

"""
TOPP parameters
"""
num_games_per_match = 30

# TOPP
turnament = TOPP(board_size=k)
turnament.play(num_games_per_match)
