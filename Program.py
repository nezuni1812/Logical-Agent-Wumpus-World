class Program:
    def __init__(self, input_file, output_file):
        self.grid_size = 0
        self.grid = []
        self.load_map(input_file)
        self.generate_percepts()

    def load_map(self, input_file):
        with open(input_file, 'r') as file:
            self.grid_size = int(file.readline().strip())
            self.grid = [line.strip().split('.') for line in file.readlines()]

    def generate_percepts(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for x in range(self.grid_size):
            for y in range(len(self.grid[x])):
                cell = self.grid[x][y]
                if 'W' in cell and 'W_H' not in cell:
                    self.update_percepts(x, y, directions, 'S')
                if 'P' in cell and 'P_G' not in cell:
                    self.update_percepts(x, y, directions, 'B')
                if 'P_G' in cell:
                    self.update_percepts(x, y, directions, 'W_H')
                if 'H_P' in cell:
                    self.update_percepts(x, y, directions, 'G_L')

    def update_percepts(self, x, y, directions, percept):
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < len(self.grid[nx]):
                if self.grid[nx][ny] == '-':
                    self.grid[nx][ny] = percept
                elif percept not in self.grid[nx][ny]:
                    self.grid[nx][ny] += percept
    def get_cell_info(self, x, y):
        percepts = ['W', 'P', 'P_G', 'H_P', 'S', 'B', 'W_H', 'G_L']

        res = ['~W', '~P', '~P_G', '~H_P', '~S', '~B', '~W_H', '~G_L']

        if 0 <= x < self.grid_size and 0 <= y < len(self.grid[x]):
            cell = self.grid[x][y]

            if 'P_G' in cell:
                res[percepts.index('P_G')] = 'P_G'
            elif 'P' in cell and 'P_G' not in cell:
                res[percepts.index('P')] = 'P'

            if 'H_P' in cell:
                res[percepts.index('H_P')] = 'H_P'
            elif 'W_H' in cell and 'H_P' not in cell:
                res[percepts.index('W_H')] = 'W_H'
            elif 'W' in cell and 'W_H' not in cell and 'H_P' not in cell:
                res[percepts.index('W')] = 'W'

            if 'S' in cell:
                res[percepts.index('S')] = 'S'
            if 'B' in cell:
                res[percepts.index('B')] = 'B'
            if 'G_L' in cell:
                res[percepts.index('G_L')] = 'G_L'

        return res


    def log_action(self, action, output_file):
        self.actions_log.append(action)
        with open(output_file, 'a') as file:
            file.write(action + '\n')
            
    def display_grid(self):
        for row in self.grid:
            print('.'.join(row))

# Example usage
if __name__ == "__main__":
    program = Program('map2.txt')
    program.display_grid()

    # Test get_cell_info
    x, y = 0, 0  # Example coordinates
    print(f"Cell info at ({x}, {y}): {program.get_cell_info(x, y)}")
    print(program.grid[0][0])
