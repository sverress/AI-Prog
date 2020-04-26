from hex.GameSimulator import GameSimulator, StartingPlayerOptions
from hex.TOPP import TOPP
from libs.helpers import Timer

"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 100  # number of games in a batch
P = StartingPlayerOptions.P1  # starting-player option
M = 3000  # number of simulations (and hence rollouts) per actual game move.
verbose = True
max_tree_height = 6
c = 1.3
save_interval = 20  # number of games between each time we save a model

# SETTINGS FOR HEX
k = 5  # board size kxk, 3 <= k <= 10

TOPP.delete_models()

training_timer = Timer(start=True)

# TRAIN AGAINST SELF
game = GameSimulator(G, P, M, verbose, max_tree_height, c, k, print_parameters=True, save_interval=save_interval)
game.run()

training_timer.stop()
print(f"Training time elapsed: {training_timer.time_str()}")

"""
TOPP parameters
"""
num_games_per_match = 2

# TOPP
turnament = TOPP(board_size=k)
turnament.play(num_games_per_match)
