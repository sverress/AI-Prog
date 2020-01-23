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
        return str(self.x_pos[0]) + str(self.x_pos[1]) + str(self.z_pos[0]) + str(self.x_pos[1])
