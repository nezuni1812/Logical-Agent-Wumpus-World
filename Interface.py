from Program import *

class Interface:
    def __init__(self, program):
        self.program = program
        self.agent_cell = None

    def convert_wumpus_to_matrix(self, position):
        x, y = position
        return (self.program.grid_size - x, y - 1)

    def convert_matrix_to_wumpus(self, position):
        x, y = position
        return (self.program.grid_size - x, y + 1)

    def set_agent_cell(self, position):
        self.agent_cell = self.convert_wumpus_to_matrix(position)

    def get_percepts(self):
        if self.agent_cell:
            return self.program.get_cell_info(*self.agent_cell)
        return None

    def log_state(self, state):
        self.program.log_state(state)

    def get_grid_size(self):
        return self.program.grid_size