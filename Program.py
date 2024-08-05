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
        percepts = ['~W', '~P', '~P_G', '~H_P', '~S', '~B', '~W_H', '~G_L']
        percept_mapping = {
            'W': 0,
            'P': 1,
            'P_G': 2,
            'H_P': 3,
            'S': 4,
            'B': 5,
            'W_H': 6,
            'G_L': 7
        }

        if 0 <= x < self.grid_size and 0 <= y < len(self.grid[x]):
            cell = self.grid[x][y]
            if cell != '-':
                for key in percept_mapping.keys():
                    if key in cell:
                        percepts[percept_mapping[key]] = key

        return percepts

    def display_grid(self):
        for row in self.grid:
            print('.'.join(row))

# Example usage
if __name__ == "__main__":
    program = Program('map2.txt')
    program.display_grid()

    # Test get_cell_info
    x, y = 1, 1  # Example coordinates
    print(f"Cell info at ({x}, {y}): {program.get_cell_info(x, y)}")
