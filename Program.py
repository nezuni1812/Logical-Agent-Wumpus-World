from State import State

class Program:
    def __init__(self, input_file, output_file):
        self.grid_size = 0
        self.grid = []
        self.output_file = output_file
        self.load_map(input_file)
        self.generate_percepts()
        self.states_log = []

    def load_map(self, input_file):
        with open(input_file, 'r') as file:
            self.grid_size = int(file.readline().strip())
            self.grid = [line.strip().split('.') for line in file.readlines()]
            for x in range(self.grid_size):
                for y in range(len(self.grid[x])):
                    cell_content = self.grid[x][y]
                    if cell_content != '-':
                        objects = cell_content.split(',')
                        percept_numbers = set()
                        
                        # Check and add percepts
                        if 'W' in objects:
                            percept_numbers.add('1')  # Wumpus
                        if 'P_G' in objects:
                            percept_numbers.add('3')  # Poisonous Gas
                        if 'P' in objects:
                            percept_numbers.add('2')  # Pit
                        if 'H_P' in objects:
                            percept_numbers.add('4')  # Healing Potion
                        if 'C' in objects:
                            percept_numbers.add('9')  # Chess of gold
                        
                        # Combine percepts into a string
                        self.grid[x][y] = ''.join(sorted(percept_numbers))
                    else:
                        self.grid[x][y] = ''
    

    def generate_percepts(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        percept_map = {
            '1': '5',  # Wumpus -> Stench
            '2': '6',  # Pits -> Breeze
            '3': '7',  # Poisonous Gas -> Whiff
            '4': '8'   # Healing Potion -> Glitter
        }

        for x in range(self.grid_size):
            for y in range(len(self.grid[x])):
                cell = self.grid[x][y]
                percepts_to_add = set()
                
                for key, value in percept_map.items():
                    if key in cell:
                        percepts_to_add.add(value)
                
                # Update adjacent cells with percepts
                for percept in percepts_to_add:
                    self.update_percepts(x, y, directions, percept)

    def update_percepts(self, x, y, directions, percept):
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < len(self.grid[nx]):
                if self.grid[nx][ny] == '':
                    self.grid[nx][ny] = percept
                elif percept not in self.grid[nx][ny]:
                    self.grid[nx][ny] += percept

    def get_cell_info(self, x, y):
        percept_map = {
            '1': 'W',
            '2': 'P',
            '3': 'P_G',
            '4': 'H_P',
            '5': 'S',
            '6': 'B',
            '7': 'W_H',
            '8': 'G_L',
            '9': 'C'
        }
        percepts = ['W', 'P', 'P_G', 'H_P', 'S', 'B', 'W_H', 'G_L', 'C']
        result = ['~W', '~P', '~P_G', '~H_P', '~S', '~B', '~W_H', '~G_L', '~C']

        if 0 <= x < self.grid_size and 0 <= y < len(self.grid[x]):
            cell = self.grid[x][y]
            for code, percept in percept_map.items():
                if code in cell:
                    result[percepts.index(percept)] = percept
        
        return result

    def display_grid(self):
        for row in self.grid:
            formatted_row = []
            for cell in row:
                if cell:
                    formatted_row.append(''.join(sorted(cell)))
                else:
                    formatted_row.append('-')
            print(' '.join(formatted_row))

    def log_state(self, state):
        state_str = (f"Position: {state[State.POSITION.value]} "
                      f"Action: {state[State.EVENT.value]} "
                      f"Point: {state[State.POINT.value]} "
                      f"HP: {state[State.HP.value]} "
                      f"Heal_Potions: {state[State.HEAL_POTIONS.value]}")
        with open(self.output_file, 'a') as file:
            file.write(state_str + '\n')
        self.states_log.append(state)

    
# Example usage
if __name__ == "__main__":
    program = Program('map1.txt', 'outpu2.txt')
    x, y = 0, 0
    print(program.get_cell_info(x, y))
    program.display_grid()
