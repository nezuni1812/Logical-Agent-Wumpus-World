from KnowledgeBase import *
from State import *
from collections import deque
import heapq

# W - ma, P: pit, G: gold, P_G: -25%, H_P: +25%, S: thúi, B: lạnh, 
# W_H: tỏa ra từ hơi độc, G_L: tỏa ra từ +25%

# Get the current direction
priority_order = {
        "N": ["N", "E", "W", "S"],
        "E": ["E", "S", "N", "W"],
        "S": ["S", "W", "E", "N"],
        "W": ["W", "N", "S", "E"]
    }


class Agent:
    def __init__(self, interface):
        self.interface = interface
        self.current_position = (1, 1) # Start position is 1,1
        self.last_position = None
        self.direction = "N"
        self.current_percept = []
        self.current_hp = 100
        self.heal_potions = 0
        self.is_alive = True
        self.point = 0
        self.KB = WumpusKB()
        self.interface.set_agent_cell(self.current_position)
        self.explored_cells = set()
        self.safe_cells = set()
        self.gas_explored = set()
        self.map_size = self.interface.get_grid_size_for_agent()

    def get_adj_percept_cell(self, x, y):
        adj_cell = []
        for dx, dy in directions_vectors.values():
            row = x + dx
            col = y + dy
            if 1 <= row <= self.map_size and 1 <= col <= self.map_size:
                adj_cell.append((row, col))
        
        return adj_cell

    def get_adj_cell(self):
        x, y = self.current_position
        adj_cell = []
        for direction in priority_order[self.direction]:
            d_x, d_y = directions_vectors[direction]
            row = x + d_x
            col = y + d_y
            if 1 <= row <= self.map_size and 1 <= col <= self.map_size:
                adj_cell.append((row, col))
        return adj_cell
    
    def process_symbol_xy(self, pos_symbol, neg_symbol, x, y):
        negated_pos_xy = symbols(f'{pos_symbol}{x}{y}')
        inferred = self.KB.infer(negated_pos_xy) # Check if ~pos_symbol_xy can be inferred
        # print(negated_pos_xy, inferred)
        if inferred:
            neighbors = self.get_adj_percept_cell(x, y)  # Get the adjacent cells based on the current position and direction
            for nx, ny in neighbors:
                neg_symbol_xy = symbols(f'{neg_symbol}{nx}{ny}')
                if self.KB.infer(neg_symbol_xy):  # Check if neg_symbol is inferred in the neighbor
                    # Get the neighbors of (nx, ny)
                    adj_neighbors = self.get_adj_percept_cell(nx, ny)

                    # Create the Or(pos_symbol...) clause for neg_symbol_xy
                    pos_literals = [symbols(f'{pos_symbol}{adj_x}{adj_y}') for adj_x, adj_y in adj_neighbors]
                    neg_clause = Or(*pos_literals)
                    # Check the other three cells for ~pos_symbol
                    all_others_negated = True
                    for adj_x, adj_y in neighbors:
                        if adj_x == x and adj_y == y:
                            continue  # Skip pos_symbol_xy itself

                        negated_pos = Not(symbols(f'{pos_symbol}{adj_x}{adj_y}'))
                        if not self.KB.infer(negated_pos):
                            all_others_negated = False
                            break
                    
                    # If the negation condition for the other three cells is met, remove clauses
                    if all_others_negated:
                        # print(2, neg_clause, neg_symbol_xy)
                        self.KB.delete_clause(neg_clause)  # Remove the Or(pos_symbol...) clause
                        self.KB.delete_clause(neg_symbol_xy)  # Remove neg_symbol from the KB   
                         
    def perceive_current_cell(self):
        self.current_percept = self.interface.get_percepts()  # Example: {'P', '~W', '~S',...}

        x, y = self.current_position  # Get the current position
        neighbors = self.get_adj_cell()  # Retrieve adjacent cells only once

        for percept in self.current_percept:
            if percept.startswith('~'):
                percept_symbol = symbols(f'{percept[1:]}{x}{y}')
                percept_symbol = Not(percept_symbol)
                self.KB.add_clause(percept_symbol)
                self.KB.delete_clause(symbols(f'{percept[1:]}{x}{y}'))
                if percept == '~S':
                    for nx, ny in neighbors:
                        self.KB.add_clause(Not(symbols(f'W{nx}{ny}')))
                
                elif percept == '~B':
                    for nx, ny in neighbors:
                        self.KB.add_clause(Not(symbols(f'P{nx}{ny}')))
                
                elif percept == '~W_H':
                    for nx, ny in neighbors:
                        self.KB.add_clause(Not(symbols(f'P_G{nx}{ny}')))
                
                elif percept == '~G_L':
                    for nx, ny in neighbors:
                        self.KB.add_clause(Not(symbols(f'H_P{nx}{ny}')))
                
                elif percept == '~H_P':
                    for nx, ny in neighbors:
                        self.process_symbol_xy('H_P', 'G_L', nx, ny)
                    
                elif percept == '~W':
                    for nx, ny in neighbors:
                        self.process_symbol_xy('W', 'S', nx, ny)
            
            else:
                percept_symbol = symbols(f'{percept}{x}{y}')
                if percept == 'S':
                    neighbor_literals = [symbols(f'W{nx}{ny}') for nx, ny in neighbors]
                    percept_infer_symbol = Or(*neighbor_literals)  # Create OR clause for all adjacent Wumpus positions
                    self.KB.add_clause(percept_infer_symbol) 
                    self.KB.delete_clause(Not(percept_symbol))               

                elif percept == 'B':
                    neighbor_literals = [symbols(f'P{nx}{ny}') for nx, ny in neighbors]
                    percept_infer_symbol = Or(*neighbor_literals)  # Pit positions
                    self.KB.add_clause(percept_infer_symbol)
                    self.KB.delete_clause(Not(percept_symbol))                 

                elif percept == 'W_H':
                    neighbor_literals = [symbols(f'P_G{nx}{ny}') for nx, ny in neighbors]
                    percept_infer_symbol = Or(*neighbor_literals)  # Gas positions
                    self.KB.add_clause(percept_infer_symbol)
                    self.KB.delete_clause(Not(percept_symbol))    

                elif percept == 'G_L':
                    neighbor_literals = [symbols(f'H_P{nx}{ny}') for nx, ny in neighbors]
                    percept_infer_symbol = Or(*neighbor_literals)  # Heal positions
                    self.KB.add_clause(percept_infer_symbol)
                    self.KB.delete_clause(Not(percept_symbol))    

                self.KB.add_clause(percept_symbol) 

        # self.KB.print_KB()
        return self.current_percept
    
    def do_in_percept(self):
        self.perceive_current_cell()
        state = [self.current_position, self.direction, '', self.point, self.current_hp, self.heal_potions]

        for percept in self.current_percept:
            if percept == 'W':
                self.is_alive = False
                self.point -= 10000
                self.current_hp = 0
                state[State.EVENT.value] = 'BE_EATEN_BY_WUMPUS'   
                self.interface.log_state(state)

            elif percept == 'P':
                self.is_alive = False
                self.point -= 10000
                self.current_hp = 0
                state[State.EVENT.value] = 'FALL_INTO_PIT'
                self.interface.log_state(state)

            elif percept == 'C':
                self.point += 5000
                state[State.EVENT.value] = 'GRAB_GOLD'
                self.interface.log_state(state)

            elif percept == 'H_P':
                self.heal_potions += 1
                self.point -= 10
                self.process_symbol_xy('H_P', 'G_L', self.current_position[0], self.current_position[1])
                state[State.EVENT.value] = 'GRAB_HEALING_POTION'
                self.interface.log_state(state)
                self.KB.add_clause(Not(symbols(f'H_P{self.current_position[0]}{self.current_position[1]}')))

            elif percept == 'P_G':
                self.gas_explored.add(self.current_position)
                self.current_hp -= 25
                state[State.EVENT.value] = 'POISONED_BY_POISON_GAS'
                self.interface.log_state(state)
                state[State.HP.value] = self.current_hp
                
                if self.current_hp == 0:
                    self.is_alive = False
                    self.point -= 10000
                    state[State.EVENT.value] = 'DEAD_BY_POISONOUS_GAS'
                    self.interface.log_state(state)
                else:
                    if self.heal_potions >= 1 and self.current_hp == 25:
                        self.current_hp += 25
                        self.heal_potions -= 1
                        self.point -= 10
                        state[State.EVENT.value] = 'USE_HEALING_POTION'
                        self.interface.log_state(state)
            else:
                continue
            # Mark this cell explored and percepts to the KB
            # if not self.agent_cell.is_explored():
            #     self.agent_cell.explore()
            #     self.add_KB(self.agent_cell)

            # Update the state array
            state[State.POINT.value] = self.point
            state[State.HP.value] = self.current_hp
            state[State.HEAL_POTIONS.value] = self.heal_potions
    
    def shoot_wumpus(self, target_position):        
        current_vector = directions_vectors[self.direction]
        target_vector = (target_position[0] - self.current_position[0], 
                        target_position[1] - self.current_position[1])
        
        target_direction = None
        for direction, vector in directions_vectors.items():
            if vector == target_vector:
                target_direction = direction
                break

        turn_sequence = turn_actions.get((self.direction, target_direction), [])

        for action in turn_sequence:
            state = [self.current_position, self.direction, action, self.point, self.current_hp, self.heal_potions]
            self.interface.log_state(state)
            self.point -= 10
            if action == 'TURN_RIGHT':
                self.direction = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}[self.direction]
            elif action == 'TURN_LEFT':
                self.direction = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}[self.direction]

        state = [self.current_position, self.direction, 'SHOOT_WUMPUS', self.point, self.current_hp, self.heal_potions]
        self.interface.log_state(state)
        self.point -= 100
        state[State.POINT.value] = self.point
        
        percepts = self.interface.get_percepts_after_shoot()
        self.process_symbol_xy ('W', 'S', self.current_position[0], self.current_position[1])
        # print(percepts)
        if 'SCREAM' in percepts:
            state[State.EVENT.value] = 'HEARD_SCREAM'
            self.interface.log_state(state)
        elif '~SCREAM' in percepts:
            state[State.EVENT.value] = 'HEARD_NOTHING'
            self.interface.log_state(state)
            self.KB.add_clause(Not(symbols(f'W{target_position[0]}{target_position[1]}')))
            self.process_symbol_xy('W', 'S', target_position[0], target_position[1])
            self.KB.delete_clause(symbols(f'W{target_position[0]}{target_position[1]}'))
        
        if 'S' in percepts:
            self.KB.add_clause(symbols(f'S{self.current_position[0]}{self.current_position[1]}'))
            self.KB.delete_clause(Not(symbols(f'S{self.current_position[0]}{self.current_position[1]}')))
        elif '~S' in percepts: 
            self.KB.add_clause(Not(symbols(f'S{self.current_position[0]}{self.current_position[1]}'))) 
            self.KB.delete_clause(symbols(f'S{self.current_position[0]}{self.current_position[1]}'))
            
            neighbors = self.get_adj_cell() 
            neighbor_literals = [symbols(f'W{x}{y}') for x, y in neighbors]
            percept_symbol = And(*neighbor_literals) 
            self.KB.add_clause(Not(symbols(f'W{target_position[0]}{target_position[1]}')))
            self.process_symbol_xy('W', 'S', target_position[0], target_position[1])
            self.KB.delete_clause(symbols(f'W{target_position[0]}{target_position[1]}'))

        return percepts
            
    def check_wumpus_cell(self, adj_cell):
        self.perceive_current_cell()
        if '~S' in self.current_percept:
            return adj_cell

        safe_adj_cell = []

        for nx, ny in adj_cell:
            wumpus_symbol = symbols(f'W{nx}{ny}')
            wumpus_safe = self.KB.infer(Not(wumpus_symbol))
            wumpus_danger = self.KB.infer(wumpus_symbol)
            
            # print(nx, ny, wumpus_safe, wumpus_danger)
            # self.KB.print_KB()

            if wumpus_danger == True:
                percepts = self.shoot_wumpus((nx, ny))
                if '~S' in percepts:
                    safe_adj_cell.append((nx, ny))
                    
            elif wumpus_safe:
                safe_adj_cell.append((nx, ny))
                self.process_symbol_xy('W', 'S', nx, ny)
                self.KB.add_clause(Not(wumpus_symbol))
            
            elif wumpus_danger == False and wumpus_safe == False:
                percepts = self.shoot_wumpus((nx, ny))
                if '~SCREAM' in percepts:
                    safe_adj_cell.append((nx, ny))

        return safe_adj_cell

    def check_pit_cell(self, adj_cell):
        if '~B' in self.current_percept:
            return adj_cell
        self.perceive_current_cell()
        
        safe_adj_cell = []

        for nx, ny in adj_cell:
            pit_symbol = symbols(f'P{nx}{ny}')
            pit_safe = self.KB.infer(Not(pit_symbol))
            pit_danger = self.KB.infer(pit_symbol)
            
            # print(nx, ny, pit_safe, pit_danger)
            # self.KB.print_KB()

            if pit_danger:
                self.KB.add_clause(pit_symbol)
            elif pit_safe:
                safe_adj_cell.append((nx, ny))
                self.KB.add_clause(Not(pit_symbol))
            elif pit_danger == False and pit_safe == False:
                continue
        
        return safe_adj_cell
    
    def check_gas_cell(self, adj_cell):
        if '~W_H' in self.current_percept:
            return adj_cell
        self.perceive_current_cell()
        
        safe_adj_cell = []

        for nx, ny in adj_cell:
            gas_symbol = symbols(f'P_G{nx}{ny}')
            gas_safe = self.KB.infer(Not(gas_symbol))
            gas_danger = self.KB.infer(gas_symbol)
            
            Path, gas_back = self.a_star_minimize_should_not_go((1, 1), self.current_position, self.explored_cells - self.gas_explored, self.gas_explored)
            if gas_danger == True:
                self.KB.add_clause(gas_symbol)
                if self.current_hp - 25 - (gas_back * 25) + self.heal_potions*25 >= 25:
                    safe_adj_cell.append((nx, ny))
            elif gas_safe:
                safe_adj_cell.append((nx, ny))
                self.KB.add_clause(Not(gas_symbol))
            elif gas_danger == False and gas_safe == False and self.current_hp - 25 - (gas_back * 25) + self.heal_potions*25 >= 25:
                safe_adj_cell.append((nx, ny))
            
        return safe_adj_cell

    def backtracking_search(self):
        while self.is_alive:
            self.do_in_percept()  # Handle the percepts at the current cell
            if 'P_G' in self.current_percept:
                Path_tmp, gas_back_tmp = self.a_star_minimize_should_not_go((1, 1), self.current_position, self.explored_cells - self.gas_explored, self.gas_explored)
                if self.current_hp - ((gas_back_tmp + 1) * 25) + self.heal_potions*25 == 0:
                    break
            if not self.is_alive:
                print("Agent is dead. Exploration terminated.")
                break
            
            self.safe_cells.add(self.current_position)
            self.explored_cells.add(self.current_position)
            
            adj_cell = self.get_adj_cell()

            safe_pit_cells = self.check_pit_cell(adj_cell)
            safe_gas_cells = self.check_gas_cell(adj_cell)
            safe_wumpus_cells = self.check_wumpus_cell(adj_cell)
            
            adj_cell = self.get_adj_cell() #Vì có thể sau khi check wumpus, hướng của agent thay đổi 
            #-> agent_cell thay đổi vì agent_cell sẽ chứa cell theo độ ưu tiên dựa trên hướng của agent

            safe_adj_cells = [cell for cell in adj_cell if all([cell in safe_pit_cells, cell in safe_gas_cells, cell in safe_wumpus_cells])]
            # print("Safe cells: ", safe_adj_cells, self.current_position)
            for cell in safe_adj_cells:
                self.safe_cells.add(cell)

                
            if safe_adj_cells:
                moved = False
                for cell in safe_adj_cells:
                    if cell not in self.explored_cells:
                        self.move_to_adj_cell(cell)
                        moved = True
                        break
                if not moved:
                    # If no move was made, backtrack
                    closest_safe_cell = self.find_closest_safe_cell(self.safe_cells - self.explored_cells)
                    if closest_safe_cell:
                        path = self.a_star_path(self.current_position, closest_safe_cell, self.safe_cells)
                        if path:
                            for step in path[1:]:  # Skip the first step as it's the current position
                                self.move_to_adj_cell(step)
                        else:
                            print("No valid path to the closest safe cell. Exploration complete.")
                            break
                    else:
                        self.explored_cells.add(self.current_position)
                        print("No more safe cells to explore or backtrack to. Exploration complete.")
                        break
            else:
                print("No more adjacent safe cells. Backtracking.")
                break
        
        print("Current cell: " + str(self.current_position) + " Total cells pass: " + str(len(self.explored_cells)))
        Path, gas_back = self.a_star_minimize_should_not_go((1, 1), self.current_position, self.explored_cells - self.gas_explored, self.gas_explored)
        Path.reverse()
        Path.pop(0)
        for cell in Path:
            self.move_to_adj_cell(cell)
            
        if self.current_position == (1, 1):
            state = [self.current_position, self.direction, 'CLIMB_OUT_OF_THE_CAVE', self.point, self.current_hp, self.heal_potions]
            self.interface.log_state(state)
            state[State.POINT.value] = self.point + 10
            self.point = self.point + 10
            state[State.EVENT.value] = ''
            self.interface.log_state(state)
        print("Total cells pass: " + str(len(self.explored_cells)))
   

    def find_closest_safe_cell(self, safe_cells):
        """Find the closest safe cell to the current position."""
        min_distance = int(1e9)
        closest_cell = None
        for cell in safe_cells:
            distance = abs(cell[0] - self.current_position[0]) + abs(cell[1] - self.current_position[1])
            if distance < min_distance:
                min_distance = distance
                closest_cell = cell
        return closest_cell
    
    def move_to_adj_cell(self, new_position):
        self.last_position = self.current_position
        self.current_position = new_position

        dx = new_position[0] - self.last_position[0]
        dy = new_position[1] - self.last_position[1]
        
        for direction, vector in directions_vectors.items():
            if vector == (dx, dy):
                new_direction = direction
                break
        action = ''
        if self.direction == new_direction:
            action = 'MOVE_FORWARD'
            state = [self.last_position, self.direction, action, self.point, self.current_hp, self.heal_potions]
            self.interface.log_state(state)
            self.point -= 10
        else:
            for turn in turn_actions[(self.direction, new_direction)]:
                state = [self.last_position, self.direction, turn, self.point, self.current_hp, self.heal_potions]
                self.interface.log_state(state)
                self.point -= 10
                if turn == 'TURN_RIGHT':
                    self.direction = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}[self.direction]
                else: # TURN_LEFT
                    self.direction = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}[self.direction]
            action = 'MOVE_FORWARD'
            state = [self.last_position, self.direction, action, self.point, self.current_hp, self.heal_potions]
            self.interface.log_state(state)
            self.point -= 10
            
        self.interface.set_agent_cell(self.current_position)

    def get_direction(self, current, target):
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        if dx == 1:
            return "S"
        elif dx == -1:
            return "N"
        elif dy == 1:
            return "E"
        elif dy == -1:
            return "W"
        return self.direction
    
    def get_adj_cell_from_position(self, position):
        x, y = position
        adj_cell = []
        for direction in priority_order[self.direction]:
            d_x, d_y = directions_vectors[direction]
            row = x + d_x
            col = y + d_y
            if 1 <= row <= self.map_size and 1 <= col <= self.map_size:
                adj_cell.append((row, col))
        return adj_cell
    
    def a_star_path(self, start, goal, safe_cells):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))  # (priority, cell)
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            for neighbor in self.get_adj_cell_from_position(current):
                if neighbor in safe_cells:
                    tentative_g_score = g_score[current] + 1  # basic move cost

                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # Return None if no path is found
    
    def a_star_minimize_should_not_go(self, start, goal, safe_cells, should_not_go_cells):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))  # (priority, cell)
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        gas_have_to_go_back = 0
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                for cell in path:
                    if cell in should_not_go_cells:
                        gas_have_to_go_back += 1
                if self.current_position in should_not_go_cells:
                    gas_have_to_go_back -= 1
                return path, gas_have_to_go_back

            for neighbor in self.get_adj_cell_from_position(current):
                if neighbor in safe_cells or neighbor in should_not_go_cells:
                    tentative_g_score = g_score[current] + 1  # basic move cost

                    if neighbor in should_not_go_cells:
                        tentative_g_score += 300  # penalty for "should not go" cells
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None, 0