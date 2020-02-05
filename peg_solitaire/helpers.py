import sys


def print_loader(progress, total, interval):
    bar = "=" * int(progress / interval) + ">" + " " * (int(total / interval) - int(i / interval))
    sys.stdout.write(f"\r[{bar}] {int(progress / total * 100)}%")
    sys.stdout.flush()
