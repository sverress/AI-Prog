from hex.GameVisualizer import GameVisualizer
from hex.ANET import ANET
import matplotlib.pyplot as plt

from hex.TOPP import TOPP


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


def train_from_cases_and_show_loss():
    cases_directory = "/Users/svoss/KODE/AI-Prog/runs/overnight/cases"
    actor_net_parameters = {
        "buffer_batch_size": 350,
        "max_size_buffer": 3000,
        "replay_buffer_cutoff_rate": 0.3,
        "epochs": 200,
        "verbose": 2,  # 2: one line per epoch
        "save_directory": "trained_models",
        "hidden_layers_structure": [200, 200],
        "learning_rate": 0.05,
    }
    anet, history = ANET.train_network_from_cases(cases_directory, actor_net_parameters)
    anet.save_model(32)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()


def play_TOPP():
    tournament = TOPP("/Users/svoss/KODE/AI-Prog/runs/overnight/trained_models")
    tournament.play(4)


def main():
    #train_from_cases_and_show_loss()
    model_match("trained_models", None, 32, starting_player=1)


if __name__ == "__main__":
    main()
