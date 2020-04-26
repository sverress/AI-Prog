import sys, getopt

from hex.GameVisualizer import GameVisualizer


def main(argv):
    explanation_string = "visualize.py <board_size> <player_1> <player_2> -p <starting_player>"
    try:
        opts, args = getopt.getopt(argv, "p:")
    except getopt.GetoptError:
        print(explanation_string)
        sys.exit(2)
    for opt, arg in opts:
        print(opt, arg)
        if opt == "-h":
            print(explanation_string)
            sys.exit()
        elif opt == "-p":
            starting_player = arg


if __name__ == "__main__":
    main(sys.argv[1:])