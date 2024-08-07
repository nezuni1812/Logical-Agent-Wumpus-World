from KnowledgeBase import *
from State import State
# W - ma, P: pit, G: gold, P_G: -25%, H_P: +25%, S: thúi, B: lạnh, 
# W_H: tỏa ra từ hơi độc, G_L: tỏa ra từ +25%
directions = {
    "N": (1, 0),
    "E": (0, 1),
    "S": (-1, 0),
    "W": (0, -1)
}

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
            d_x, d_y = directions[direction]
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
                    percept_symbol = Or(*neighbor_literals)  # Create OR clause for all adjacent Wumpus positions

                elif percept == 'B':
                    neighbor_literals = [symbols(f'P{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Pit positions

                elif percept == 'W_H':
                    neighbor_literals = [symbols(f'P_G{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Gas positions

                elif percept == 'G_L':
                    neighbor_literals = [symbols(f'H_P{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Heal positions

                self.KB.add_clause(percept_symbol)  # Add clause as a list

        # self.KB.print_KB()
        return self.current_percept
    
    def do_in_percept(self):
        self.perceive_current_cell()
        # Initialize state array with default values
        state = [self.current_position, '', self.point, self.current_hp, self.heal_potions]

        for percept in self.current_percept:
            # Update state based on percept
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

            elif percept == 'G':
                self.point += 5000
                state[State.EVENT.value] = 'GRAB_GOLD'
                self.interface.log_state(state)

            elif percept == 'H_P':
                self.heal_potions += 1
                self.point -= 10
                state[State.EVENT.value] = 'GRAB_HEALING_POTION'
                self.interface.log_state(state)
                # if self.current_hp < 100:
                #     self.current_hp += 25
                #     self.heal_potions -= 1
                #     self.point -= 10
                #     state[State.EVENT.value] = 'USE_HEALING_POTION'
                #     self.interface.log_state(state)

            elif percept == 'P_G':
                self.current_hp -= 25
                state[State.EVENT.value] = 'GO_TO_POISONOUS_GAS'
                if self.current_hp == 0:
                    self.is_alive = False
                    self.point -= 10000
                    state[State.EVENT.value] = 'DEAD_BY_POISONOUS_GAS'
                else:
                    if self.heal_potions >= 1 and self.current_hp == 25:
                        self.current_hp += 25
                        self.heal_potions -= 1
                        self.point -= 10
                        state[State.EVENT.value] = 'USE_HEALING_POTION'
                        self.interface.log_state(state)
                self.interface.log_state(state)

            # Mark this cell explored and percepts to the KB
            # if not self.agent_cell.is_explored():
            #     self.agent_cell.explore()
            #     self.add_KB(self.agent_cell)

            # Update the state array
            state[State.POINT.value] = self.point
            state[State.HP.value] = self.current_hp
            state[State.HEAL_POTIONS.value] = self.heal_potions

        return state

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

            wumpus_danger = self.KB.infer(wumpus_symbol)
            pit_danger = self.KB.infer(pit_symbol)
            gas_danger = self.KB.infer(gas_symbol)
            
            
            if wumpus_safe and pit_safe and (gas_safe or self.current_hp >= 75):
                safe_adj_cell.append((nx, ny))

        return safe_adj_cell
    
    def backtracking_search(self):
        print(self.do_in_percept())
        print(self.current_percept)
        
        if not self.is_alive:
            return False
        
        self.explored_cells.add(self.current_position)  # Mark the current cell as explored

        safe_adj_cells = self.check_safeadjcell()
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
        return self.direction  # Default to current direction if no change