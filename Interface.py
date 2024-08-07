from Program import *
from State import *

class Interface:
    def __init__(self, program):
        self.program = program
        self.output_file = program.output_file
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
        state_str = (f"Position: {state[State.POSITION.value]} "
                    f"Direction: {state[State.DIRECTION.value]} "
                    f"Action: {state[State.EVENT.value]} "
                    f"Point: {state[State.POINT.value]} "
                    f"HP: {state[State.HP.value]} "
                    f"Heal_Potions: {state[State.HEAL_POTIONS.value]}")
        with open(self.output_file, 'a') as file:
            file.write(state_str + '\n')
        state[State.POSITION.value] = self.convert_wumpus_to_matrix(state[State.POSITION.value])

        if state[State.DIRECTION.value] == 'N':
            state[State.DIRECTION.value] = (-1, 0)
        elif state[State.DIRECTION.value] == 'S':
            state[State.DIRECTION.value] = (1, 0)
        else:
            state[State.DIRECTION.value] = directions[State.DIRECTION.value]
        self.program.log_state(state)

    def get_grid_size(self):
        return self.program.grid_size