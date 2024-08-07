from KnowledgeBase import *
from State import *
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
    
    def get_adj_cell(self):
        x, y = self.current_position
        adj_cell = []
        for direction in priority_order[self.direction]:
            d_x, d_y = directions_vectors[direction]
            row = x + d_x
            col = y + d_y
            if 1 <= row <= 4 and 1 <= col <= 4:
                adj_cell.append((row, col))
        return adj_cell
    

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
                state[State.EVENT.value] = 'GRAB_HEALING_POTION'
                self.interface.log_state(state)

            elif percept == 'P_G':
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

    def check_safeadjcell(self):
        self.perceive_current_cell()
        adj_cell = self.get_adj_cell()
        safe_adj_cell = []

        for nx, ny in adj_cell:
            wumpus_symbol = symbols(f'W{nx}{ny}')
            pit_symbol = symbols(f'P{nx}{ny}')
            gas_symbol = symbols(f'P_G{nx}{ny}')

            wumpus_safe = self.KB.infer(Not(wumpus_symbol))
            pit_safe = self.KB.infer(Not(pit_symbol))
            gas_safe = self.KB.infer(Not(gas_symbol))

            # self.KB.add_clause(wumpus_symbol)

            # wumpus_danger = self.KB.infer(wumpus_symbol)
            # pit_danger = self.KB.infer(pit_symbol)
            # gas_danger = self.KB.infer(gas_symbol)
            
            # if wumpus_danger:
            #     self.point = self.point - 100
            #     state = [self.current_position, self.direction, 'SHOOT_WUMPUS', self.point, self.current_hp, self.heal_potions]
            #     self.interface.log_state(state)

            
            if wumpus_safe and pit_safe and gas_safe or (gas_safe == False and self.current_hp >= 75):
                safe_adj_cell.append((nx, ny))

        return safe_adj_cell
    
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
    
    def check_wumpus_cell(self, adj_cell):
        self.perceive_current_cell()
        if '~S' in self.current_percept:
            return self.get_adj_cell()

        safe_adj_cell = []

        for nx, ny in adj_cell:
            wumpus_symbol = symbols(f'W{nx}{ny}')
            wumpus_safe = self.KB.infer(Not(wumpus_symbol))
            wumpus_danger = self.KB.infer(wumpus_symbol)

            if wumpus_danger == True:
                self.shoot_wumpus((nx, ny))
                safe_adj_cell.append((nx, ny))
                
                neighbors = self.get_adj_cell() 
                neighbor_literals = [symbols(f'W{x}{y}') for x, y in neighbors]
                percept_symbol = Or(*neighbor_literals) 
                self.KB.add_clause(Not(wumpus_symbol))
                self.KB.delete_clause(percept_symbol)

            elif wumpus_safe:
                safe_adj_cell.append((nx, ny))
                self.KB.add_clause(Not(wumpus_symbol))
            
            elif wumpus_danger == False and wumpus_safe == False:
                self.shoot_wumpus((nx, ny))
                safe_adj_cell.append((nx, ny))
                
                neighbors = self.get_adj_cell() 
                neighbor_literals = [symbols(f'W{x}{y}') for x, y in neighbors]
                percept_symbol = Or(*neighbor_literals) 
                self.KB.add_clause(Not(wumpus_symbol))
                self.KB.delete_clause(percept_symbol)

        return safe_adj_cell

    def check_pit_cell(self, adj_cell):
        if '~B' in self.current_percept:
            return self.get_adj_cell()
        self.perceive_current_cell()
        
        safe_adj_cell = []

        for nx, ny in adj_cell:
            pit_symbol = symbols(f'P{nx}{ny}')
            pit_safe = self.KB.infer(Not(pit_symbol))
            pit_danger = self.KB.infer(pit_symbol)

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
            return self.get_adj_cell()
        self.perceive_current_cell()
        
        safe_adj_cell = []

        for nx, ny in adj_cell:
            gas_symbol = symbols(f'P_G{nx}{ny}')
            gas_safe = self.KB.infer(Not(gas_symbol))
            gas_danger = self.KB.infer(gas_symbol)
            
            if gas_danger:
                self.KB.add_clause(gas_symbol)
                if self.current_hp >= 50:
                    safe_adj_cell.append((nx, ny))
            elif gas_safe:
                safe_adj_cell.append((nx, ny))
                self.KB.add_clause(Not(gas_symbol))
            elif self.current_hp >= 50:
                safe_adj_cell.append((nx, ny))
            
        return safe_adj_cell
    
    def backtracking_search(self):
        self.do_in_percept()
        # print(self.current_percept)
        
        if not self.is_alive:
            return False
        
        self.explored_cells.add(self.current_position)  # Mark the current cell as explored
        safe_adj_cells = set()
        adj_cell = self.get_adj_cell()
        safe_adj_cells.update(self.check_pit_cell(adj_cell))
        safe_adj_cells = safe_adj_cells.intersection(self.check_gas_cell(adj_cell))
        safe_adj_cells = safe_adj_cells.intersection(self.check_wumpus_cell(adj_cell))
        print(safe_adj_cells)
        if not safe_adj_cells:
            return False
    
        for cell in safe_adj_cells:
            if cell not in self.explored_cells:  # Check if the cell has not been explored
                self.move_to(cell)
    
                if self.backtracking_search():
                    return True
                else:
                    self.current_position = self.last_position
    
        return False
    
    def move_to(self, new_position):
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