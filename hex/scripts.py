from hex.GameVisualizer import GameVisualizer
from hex.ANET import ANET
import matplotlib.pyplot as plt


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
        "epochs": 100,
        "verbose": 2,  # 2: one line per epoch
        "save_directory": "trained_models",
        "hidden_layers_structure": [25, 15],
        "learning_rate": 0.1,
    }
    anet, history = ANET.train_network_from_cases(cases_directory, actor_net_parameters)
    plt.plot(history.history['loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()


def main():
    train_from_cases_and_show_loss()
    #model_match("/Users/svoss/KODE/AI-Prog/runs/overnight/trained_models", 0, 300, starting_player=1)


if __name__ == "__main__":
    main()
