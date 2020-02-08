import sys


def print_loader(progress, total, interval):
    bar = "=" * int(progress / interval) + ">" + " " * (int(total / interval) - int(progress / interval))
    sys.stdout.write(f"\r[{bar}] {int(progress / total * 100)}%")
    sys.stdout.flush()


def convert_string_list_to_tuple_list(string_list):
    return [(int(string_pos[0]), int(string_pos[1])) for string_pos in string_list]
