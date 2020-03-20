from mcts.GameSimulator import GameSimulator, Games, StartingPlayerOptions
"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 15  # number of games in a batch
P = StartingPlayerOptions.PLAYER_ONE  # starting-player option
M = 1000  # number of simulations (and hence rollouts) per actual game move.
verbose = True
max_tree_height = 25
c = 1

# Choosing witch game to play
GAME = Games.LEDGE

# SETTINGS FOR NIM GAME
N = 70  # starting number of pieces/stones in each game
K = 8  # maximum number of pieces that either player can take on their turn.

# SETTINGS FOR LEDGE
B_INIT = [0,1,0,2,0,1,1]  # the initial board configuration.

game = GameSimulator(G, P, M, GAME, N, K, B_INIT, verbose, max_tree_height, c=c)
game.run()
