from hex.GameSimulator import GameSimulator, StartingPlayerOptions

"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 10  # number of games in a batch
P = StartingPlayerOptions.P1  # starting-player option
M = 2  # number of simulations (and hence rollouts) per actual game move.
verbose = True
max_tree_height = 4
c = 1

# SETTINGS FOR HEX
k = 6  # board size kxk, 3 <= k <= 10

game = GameSimulator(G, P, M, verbose, max_tree_height, c, k)
game.run()