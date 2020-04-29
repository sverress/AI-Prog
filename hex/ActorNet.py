from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers
from tensorflow.keras.models import load_model
import numpy as np
import re
import os
import glob

from hex.HexNet import HexNet
from hex.StateManager import StateManager


class ActorNet(HexNet):
    def __init__(self, size_of_board, **kwargs):
        super().__init__(size_of_board, **kwargs)

    def build_model(self, model, hidden_layers_structure, learning_rate):
        if model is None:
            # Deleting current models in directory
            self.delete_associated_models()
            # Building model
            model = Sequential()
            # Adding first layer with input size depending on board sizes
            model.add(
                Dense(
                    units=self.input_shape[0],
                    activation="relu",
                    input_shape=self.input_shape,
                    kernel_initializer="random_uniform",
                )
            )
            if hidden_layers_structure:
                for layer_units in hidden_layers_structure:
                    model.add(
                        Dense(
                            units=layer_units,
                            activation="relu",
                            kernel_initializer="random_uniform",
                        )
                    )
            else:
                for i in range(1, 3):
                    model.add(
                        Dense(
                            units=self.input_shape[0],
                            activation="relu",
                            kernel_initializer="random_uniform",
                        )
                    )
            model.add(
                Dense(
                    units=self.size_of_board ** 2,
                    activation="softmax",
                    kernel_initializer="random_uniform",
                )
            )
            model.compile(
                loss="categorical_crossentropy",
                optimizer=optimizers.SGD(learning_rate=learning_rate),
                metrics=["mse"],
            )
        return model

    def predict(self, state):
        input_data = np.array([HexNet.convert_state_to_network_format(state)])
        net_distribution_tensor = self.model(input_data)[0]
        net_distribution = []
        # Filter out taken cells in the board
        for index, share_of_distribution in np.ndenumerate(net_distribution_tensor):
            if StateManager.index_cell_is_occupied(index[0], state):
                net_distribution.append(0.0)
            else:
                net_distribution.append(float(share_of_distribution))
        # Normalize
        return np.array(net_distribution) / sum(net_distribution)

    @staticmethod
    def train_network_from_cases(cases_directory, anet_parameters):
        x_path = [
            filename
            for filename in os.listdir(cases_directory)
            if filename.startswith("x")
        ][0]
        y_path = [
            filename
            for filename in os.listdir(cases_directory)
            if filename.startswith("y")
        ][0]
        x, y = (
            np.load(f"{cases_directory}/{x_path}"),
            np.load(f"{cases_directory}/{y_path}"),
        )
        anet = ActorNet(int(x_path[2]), **anet_parameters)
        history = anet.model.fit(
            x, y, epochs=anet.epochs, verbose=anet.verbose, validation_split=0.2
        )
        return anet, history

    def save_model(self, episode_number):
        self.episode_number = episode_number
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)
        self.model.save(f"{self.save_directory}/model_{episode_number}.h5")

    def add_case(self, state, target):
        generated_cases = self.gen_cases(state, target)
        for case in generated_cases:
            state = case[0]
            target = case[1]
            super().add_case(state, target)

    @staticmethod
    def load_model(model_path: str):
        episode_number = int(re.search(f"/model_(.*?).h5", model_path).group(1))
        model = load_model(model_path)
        return ActorNet(
            HexNet.infer_board_size_from_model(model),
            model=model,
            episode_number=episode_number,
        )

    @staticmethod
    def load_models(directory: str):
        """
        Fetches all file paths in the trained_models folder. Loads all models and appends to list
        :return: list of player objects, list of the number of episodes trained for each model: [obj], [int]
        """
        # Get list of paths to all saved models
        all_models = glob.glob(directory + "/*.h5")
        return sorted(
            [ActorNet.load_model(model_path) for model_path in all_models],
            key=lambda model: model.episode_number,
        )

    def load_directory_models(self):
        return ActorNet.load_models(self.save_directory)

    def save_buffer_to_file(self, num_episodes, k, cases_directory="cases"):
        x = []
        y = []
        for case in self.replay_buffer:
            x.append(case[0])  # Add state as x
            y.append(case[1])  # Add distribution as y
        if not os.path.exists(cases_directory):
            os.mkdir(cases_directory)
        np.save(f"{cases_directory}/x_{k}x{k}_{num_episodes}", np.array(x))
        np.save(f"{cases_directory}/y_{k}x{k}_{num_episodes}", np.array(y))

    @staticmethod
    def delete_models(path_to_models: str):
        # Get list of paths to all saved models
        all_models = glob.glob(f"{path_to_models}/*.h5")
        for path_to_model in all_models:
            # Remove file
            os.remove(path_to_model)

    def delete_associated_models(self):
        ActorNet.delete_models(self.save_directory)

    def gen_cases(self, state, dist):
        """
        Flips the board 180 deg to create another training case.
        :param state:
        :param distribution_of_visit_counts:
        :return:
        """
        generated_cases = [(state, dist)]

        # reverse both board rep of state string and distribution
        state_180 = "".join(reversed(state[:-2])) + state[-2:]
        dist_180 = dist[::-1]
        tuple = (state_180, dist_180)
        generated_cases.append(tuple)

        # swith row and cols for case rot 90
        board_90 = np.zeros(self.size_of_board ** 2, dtype=int)
        dist_90 = np.zeros(self.size_of_board ** 2)
        for row in range(0, self.size_of_board):
            for col in range(0, self.size_of_board):
                flatten_position_board = row * self.size_of_board + col
                flatten_position_new_board = col * self.size_of_board + row
                if state[flatten_position_board] == "0":
                    board_90[flatten_position_new_board] = state[flatten_position_board]
                else:
                    board_90[flatten_position_new_board] = (
                        "1" if state[flatten_position_board] == "2" else "2"
                    )
                dist_90[flatten_position_new_board] = dist[flatten_position_board]

        player_str = "1" if state[-1] == "2" else "2"
        state_90 = "".join(board_90.astype(str)) + ":" + player_str

        tuple = (state_90, list(dist_90))
        generated_cases.append(tuple)

        # reverse both board rep of state string and distribution for the state_90
        state_270 = "".join(reversed(state_90[:-2])) + state_90[-2:]
        dist_270 = dist_90[::-1]
        tuple = (state_270, list(dist_270))
        generated_cases.append(tuple)

        if self.verbose == 2:
            print(generated_cases)
        return generated_cases


def main():
    anet = ActorNet(4, epochs=3)

if __name__ == "__main__":
    main()