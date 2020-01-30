class Action:
    def __init__(self, x_pos: tuple, y_pos: tuple, z_pos: tuple):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos

    def __repr__(self):
        return f"{self.x_pos} -> {self.y_pos} -> {self.z_pos}"

    def get_leaving_positions(self):
        return self.x_pos, self.y_pos

    def get_entering_positions(self):
        return self.z_pos,

    def get_action_string(self):
        return f"{self.x_pos[0]}{self.x_pos[1]}{self.y_pos[0]}{self.y_pos[1]}{self.z_pos[0]}{self.z_pos[1]}"

    @staticmethod
    def create_action_from_string(action_string: str):
        return Action(
            (int(action_string[0]), int(action_string[1])),
            (int(action_string[2]), int(action_string[3])),
            (int(action_string[4]), int(action_string[5]))
        )

