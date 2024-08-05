class Program:
    def __init__(self, input_file, output_file):
        self.grid_size = 0
        self.grid = []
        self.output_file = output_file
        self.load_map(input_file)
        self.generate_percepts()
        self.actions_log = []

    def load_map(self, input_file):
        with open(input_file, 'r') as file:
            self.grid_size = int(file.readline().strip())
            self.grid = [line.strip().split('.') for line in file.readlines()]

    def generate_percepts(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if x < len(self.grid) and y < len(self.grid[x]):
                    if self.grid[x][y] == 'W':
                        self.update_percepts(x, y, directions, 'S')
                    elif self.grid[x][y] == 'P':
                        self.update_percepts(x, y, directions, 'B')
                    elif self.grid[x][y] == 'P_G':
                        self.update_percepts(x, y, directions, 'W_H')
                    elif self.grid[x][y] == 'H_P':
                        self.update_percepts(x, y, directions, 'G_L')
                else:
                    print(f"Skipped invalid index {x},{y}")

    def update_percepts(self, x, y, directions, percept):
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.grid[nx][ny] == '-':
                    self.grid[nx][ny] = percept
                elif percept not in self.grid[nx][ny]:
                    self.grid[nx][ny] += percept
            else:
                print(f"Out of bounds: {nx},{ny}")

    def get_cell_info(self, x, y):
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.grid[x][y]
        return None

    def log_action(self, action, output_file):
        self.actions_log.append(action)
        with open(output_file, 'a') as file:
            file.write(action + '\n')

    def display_grid(self):
        for row in self.grid:
            print('.'.join(row))

# Example usage
if __name__ == "__main__":
    program = Program('map1.txt', 'result1.txt')
    program.display_grid()
