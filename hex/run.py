from hex.GameSimulator import GameSimulator, StartingPlayerOptions
from hex.TOPP import TOPP
from libs.helpers import Timer

"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 30  # number of games in a batch
P = StartingPlayerOptions.P2  # starting-player option
M = 2  # number of simulations (and hence rollouts) per actual game move.
verbose = False
max_tree_height = 10
c = 1
save_interval = 10  # number of games between each time we save a model

# SETTINGS FOR HEX
k = 3  # board size kxk, 3 <= k <= 10

training_timer = Timer(start=True)

# TRAIN AGAINST SELF
game = GameSimulator(G, P, M, verbose, max_tree_height, c, k, print_parameters=True, save_interval=save_interval)
game.run()

training_timer.stop()
print(f"Training time elapsed: {training_timer.time_str()}")

"""
TOPP parameters
"""
num_games_per_match = 20

# TOPP
turnament = TOPP(k, game.actor_network)
turnament.play(num_games_per_match)
