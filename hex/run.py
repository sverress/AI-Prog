from hex.GameSimulator import GameSimulator, StartingPlayerOptions
from hex.TOPP import TOPP
from libs.helpers import Timer

"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 10  # number of games in a batch
P = StartingPlayerOptions.P1  # starting-player option
M = 2000  # number of simulations (and hence rollouts) per actual game move.
verbose = True
max_tree_height = 6
c = 1.3
save_interval = 2  # number of games between each time we save a model

# SETTINGS FOR HEX
k = 4  # board size kxk, 3 <= k <= 10

actor_net_parameters = {
    "batch_size": 350,
    "max_size_buffer": 2000,
    "replay_buffer_cutoff_rate": 0.3,
    "epochs": 10,
    "verbose": 2 if verbose else 0,  # 2: one line per epoch
    "save_directory": "trained_models",
    "hidden_layers_structure": [],
}

training_timer = Timer(start=True)

# TRAIN AGAINST SELF
game = GameSimulator(
    G,
    P,
    M,
    verbose,
    max_tree_height,
    c,
    k,
    print_parameters=True,
    save_interval=save_interval,
    actor_net_parameters=actor_net_parameters,
)
game.run()

training_timer.stop()
print(f"Training time elapsed: {training_timer.time_str()}")

"""
TOPP parameters
"""
num_games_per_match = 2

# TOPP
turnament = TOPP(k, game.actor_network)
turnament.play(num_games_per_match)
