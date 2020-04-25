from hex.GameSimulator import GameSimulator, StartingPlayerOptions
from hex.TOPP import TOPP
from libs.helpers import Timer

"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 300  # number of games in a batch
P = StartingPlayerOptions.P2  # starting-player option
M = 40  # number of simulations (and hence rollouts) per actual game move.
verbose = False
max_tree_height = 10
c = 1.5
save_interval = 30  # number of games between each time we save a model

# SETTINGS FOR HEX
k = 4  # board size kxk, 3 <= k <= 10

actor_net_parameters = {
    "batch_size": 350,
    "max_size_buffer": 2000,
    "replay_buffer_cutoff_rate": 0.3,
    "epochs": 5,
    "verbose": 2 if verbose else 0,  # 2: one line per epoch
    "model": None,
    "episode_number": 0,
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
num_games_per_match = 20

# TOPP
turnament = TOPP(k, game.actor_network)
turnament.play(num_games_per_match)
