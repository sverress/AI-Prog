from hex.GameSimulator import GameSimulator, StartingPlayerOptions
from hex.TOPP import TOPP
from libs.helpers import Timer


"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 50  # number of games in a batch
P = StartingPlayerOptions.P1  # starting-player option
verbose = False
save_interval = 10  # number of games between each time we save a model

# SETTINGS FOR HEX
k = 5  # board size kxk, 3 <= k <= 10

actor_net_parameters = {
    "buffer_batch_size": 350,
    "max_size_buffer": 3000,
    "replay_buffer_cutoff_rate": 0.3,
    "epochs": 50,
    "verbose": 1,  # 2: one line per epoch
    "save_directory": "trained_models",
    "hidden_layers_structure": [1500, 1500],
    "learning_rate": 0.03,
}
mcts_parameters = {
    "max_tree_height": 18,
    "c": 1.5,  # Exploration constant
    "number_of_simulations": 200,  # number of simulations (and hence roll-outs) per actual game move
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
turnament = TOPP('trained_models')
turnament.play(num_games_per_match)
