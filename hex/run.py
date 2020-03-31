from hex.GameSimulator import GameSimulator, StartingPlayerOptions

"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH PARAMETERS
"""
G = 5  # number of games in a batch
P = StartingPlayerOptions.P2  # starting-player option
M = 5000  # number of simulations (and hence rollouts) per actual game move.
verbose = True
max_tree_height = 16
c = 1

# SETTINGS FOR HEX
k = 4  # board size kxk, 3 <= k <= 10

game = GameSimulator(G, P, M, verbose, max_tree_height, c, k)
game.run()
