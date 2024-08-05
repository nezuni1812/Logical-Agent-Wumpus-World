class Program:
    def __init__(self, input_file):
        self.grid_size = 0
        self.grid = []
        self.load_map(input_file)
        self.generate_percepts()

    def load_map(self, input_file):
        with open(input_file, 'r') as file:
            self.grid_size = int(file.readline().strip())
            self.grid = [line.strip().split('.') for line in file.readlines()]
            for x in range(self.grid_size):
                for y in range(len(self.grid[x])):
                    cell_content = self.grid[x][y]
                    if cell_content != '-':
                        percept_numbers = []
                        if 'W' in cell_content:
                            percept_numbers.append('1')
                        if 'P' in cell_content:
                            percept_numbers.append('2')
                        if 'P_G' in cell_content:
                            percept_numbers.append('3')
                        if 'H_P' in cell_content:
                            percept_numbers.append('4')
                        self.grid[x][y] = ''.join(sorted(percept_numbers))
                    else:
                        self.grid[x][y] = ''

    def generate_percepts(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        percept_map = {
            '1': '5',  # Wumpus -> Stench
            '2': '6',  # Pits -> Breeze
            '3': '7',  # Pit with Gold -> Whiff
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
            '8': 'G_L'
        }
        percepts = ['W', 'P', 'P_G', 'H_P', 'S', 'B', 'W_H', 'G_L']
        result = ['~W', '~P', '~P_G', '~H_P', '~S', '~B', '~W_H', '~G_L']

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
            print('.'.join(formatted_row))

# Example usage
if __name__ == "__main__":
    program = Program('map2.txt')
    x, y = 0, 0
    print(program.get_cell_info(x, y))
    program.display_grid()
