from hex.GameVisualizer import GameVisualizer
from hex.ANET import ANET


def model_match(models_directory, player1, player2, starting_player=1):
    models_dict = {}
    models = ANET.load_models(models_directory)
    board_size = ANET.infer_board_size_from_model(models[0].model)
    for model in models:
        models_dict[model.episode_number] = model
    player1 = models_dict.get(player1)
    player2 = models_dict.get(player2)
    game = GameVisualizer(
        board_size, player1=player1, player2=player2, starting_player=starting_player
    )
    game.run()


def main():
    model_match("/Users/svoss/KODE/AI-Prog/runs/4x4_stoch/trained_models", 200, 100, starting_player=1)


if __name__ == "__main__":
    main()
