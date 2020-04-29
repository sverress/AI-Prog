from hex.HexNet import HexNet


class ActorNet(HexNet):
    def __init__(self, size_of_board, **kwargs):
        super().__init__(size_of_board, **kwargs)

def main():
    anet = ActorNet(4, epochs=3)

if __name__ == "__main__":
    main()