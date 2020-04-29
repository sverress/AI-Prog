from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers
import numpy as np

from hex.HexNet import HexNet


class ActorNet(HexNet):
    def __init__(self, size_of_board, **kwargs):
        super().__init__(size_of_board, **kwargs)

    def build_model(self, model, hidden_layers_structure, learning_rate):
        if model is None:
            # Deleting current models in directory
            HexNet.delete_models(self.save_directory)
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

    @staticmethod
    def create_hex_net(board_size, **kwargs):
        return ActorNet(board_size, **kwargs)

    def save_model(self, episode_number):
        super().save_model(episode_number)
        self.model.save(f"{self.save_directory}/model_{episode_number}.h5")

    def add_case(self, state, target):
        generated_cases = self.gen_cases(state, target)
        for case in generated_cases:
            state = case[0]
            target = case[1]
            super().add_case(state, target)

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