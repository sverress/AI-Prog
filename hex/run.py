from hex.GameSimulator import GameSimulator, StartingPlayerOptions
from hex.TOPP import TOPP
from libs.helpers import Timer

"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 300  # number of games in a batch
P = StartingPlayerOptions.P1  # starting-player option
verbose = False
save_interval = 30  # number of games between each time we save a model

# SETTINGS FOR HEX
k = 3  # board size kxk, 3 <= k <= 10

actor_net_parameters = {
    "batch_size": 350,
    "max_size_buffer": 2000,
    "replay_buffer_cutoff_rate": 0.3,
    "epochs": 100,
    "verbose": 2 if verbose else 0,  # 2: one line per epoch
    "save_directory": "trained_models",
    "hidden_layers_structure": [(k ** 2 + 5) * 4, (k ** 2 + 5) * 8, (k ** 2 + 5) * 4],
    "learning_rate": 0.001,
}
mcts_parameters = {
    "max_tree_height": 10,
    "c": 1.5,  # Exploration constant
    "number_of_simulations": 10,  # number of simulations (and hence roll-outs) per actual game move
    "verbose": verbose,
}

training_timer = Timer(start=True)

# TRAIN AGAINST SELF
game = GameSimulator(
    G,
    P,
    verbose,
    k,
    print_parameters=True,
    save_interval=save_interval,
    actor_net_parameters=actor_net_parameters,
    mcts_parameters=mcts_parameters
)
game.run()

training_timer.stop()
print(f"Training time elapsed: {training_timer.time_str()}")

"""
TOPP parameters
"""
num_games_per_match = 2

# TOPP
turnament = TOPP(game.actor_network.save_directory)
turnament.play(num_games_per_match)
