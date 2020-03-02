from mcts.GameSimulator import GameSimulator
"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH CHOSEN PARAMETERS
"""
G = 30  # number of games in a batch
P = True  # starting-player option (True for we start, false for other start)
M = 500  # number of simulations (and hence rollouts) per actual game move.
verbose = False
max_tree_height = 10

# Choosing witch game to play
GAME = GameSimulator.LEDGE

# SETTINGS FOR NIM GAME
N = 10  # starting number of pieces/stones in each game
K = 5  # maximum number of pieces that either player can take on their turn.

# SETTINGS FOR LEDGE
B_INIT = [0, 1, 0, 2, 1, 0, 1]  # the initial board configuration.

game = GameSimulator(G, P, M, GAME, N, K, B_INIT, verbose, max_tree_height)
game.run()
