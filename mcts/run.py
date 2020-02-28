from mcts.GameSimulator import GameSimulator
"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH CHOSEN PARAMETERS
"""
G = 1  # number of games in a batch
P = True  # starting-player option (True for we start, false for other start)
M = 1  # number of simulations (and hence rollouts) per actual game move.

# SETTINGS FOR NIM GAME
PLAYING_NIM = False
N = 1  # starting number of pieces/stones in each game
K = 1  # maximum number of pieces that either player can take on their turn.

# SETTINGS FOR
B_INIT = [0, 2, 0, 1]  # the initial board configuration.

game = GameSimulator(G, P, M, N, K, B_INIT)
game.run()
