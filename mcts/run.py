from mcts.GameSimulator import GameSimulator
"""
FILE FOR SETTING UP A RUN OF THE MCTS ALGORITHM WITH CHOSEN PARAMETERS
"""
g = 1  # number of games in a batch
p = True  # starting-player option (True for we start, false for other start)
m = 1  # number of simulations (and hence rollouts) per actual game move.
n = 1  # starting number of pieces/stones in each game
k = 1  # maximum number of pieces that either player can take on their turn.
b_init = [0, 2, 0, 1]  # the initial board configuration.

game = GameSimulator(g, p, m, n, k, b_init)
game.run()
