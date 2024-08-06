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
    
    def get_adj_cell(self):
        x, y = self.current_position
        adj_cell = []
        for direction in priority_order[self.direction]:
            d_x, d_y = directions[direction]
            row = x + d_x
            col = y + d_y
            if 1 <= row <= 10 and 1 <= col <= 10:
                adj_cell.append((row, col))
        return adj_cell
    
    def perceive_current_cell(self):
        self.current_percept = self.interface.get_percepts()  # Example: {'P', '~W', '~S',...}
        
        x, y = self.current_position  # Get the current position
        for percept in self.current_percept:
            if percept.startswith('~'):
                percept_symbol = symbols(f'{percept[1:]}{x}{y}')
                percept_symbol = Not(percept_symbol)
            else:
                percept_symbol = symbols(f'{percept}{x}{y}')
                if percept == 'S':
                    neighbors = self.get_adj_cell()
                    neighbor_literals = [symbols(f'W{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Create OR clause for all adjacent Wumpus positions
                
                elif percept == 'B':
                    neighbors = self.get_adj_cell()
                    neighbor_literals = [symbols(f'P{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Create OR clause for all adjacent Pit positions
                
                elif percept == 'W_H':
                    neighbors = self.get_adj_cell()
                    neighbor_literals = [symbols(f'P_G{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Create OR clause for all adjacent Gas positions

                elif percept == 'G_L':
                    neighbors = self.get_adj_cell()
                    neighbor_literals = [symbols(f'H_P{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Create OR clause for all adjacent Heal positions

            self.KB.add_clause([percept_symbol])  # Add clause as a list
        self.KB.print_KB()
        return self.current_percept
    
    def check_percept(self):
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
            if not self.agent_cell.is_explored():
                self.agent_cell.explore()
                self.add_KB(self.agent_cell)

            # Update the state array
            state[State.POINT.value] = self.point
            state[State.HP.value] = self.current_hp
            state[State.HEAL_POTIONS.value] = self.heal_potions

        return state

    def check_safeadjcell(self):
        most_priority = []
        less_priority = []
        adj_cell = self.get_adj_cell() 
        safe_adj_cell = []

        for nx, ny in adj_cell:
            wumpus_symbol = symbols(f'W{nx}{ny}')
            pit_symbol = symbols(f'P{nx}{ny}')
            gas_symbol = symbols(f'P_G{nx}{ny}')

            wumpus_safe = not self.KB.infer(Not(wumpus_symbol))
            pit_safe = not self.KB.infer(Not(pit_symbol))
            gas_safe = not self.KB.infer(Not(gas_symbol))

            # KB chỉ được cập nhật nếu chắc chắn là không có wumpus, pit, gas
            if self.KB.infer(wumpus_symbol):
                self.KB.add_clause(Not(wumpus_symbol))
            if self.KB.infer(pit_symbol):
                self.KB.add_clause(Not(pit_symbol))
            if self.KB.infer(gas_symbol):
                self.KB.add_clause(Not(gas_symbol))

            if wumpus_safe and pit_safe and gas_safe:
                most_priority.append((nx, ny))
            elif gas_safe:
                less_priority.append((nx, ny))

        if most_priority:
            safe_adj_cell = most_priority
        elif less_priority:
            safe_adj_cell = less_priority

        if safe_adj_cell == [self.last_position]:
            return safe_adj_cell

        if self.last_position in safe_adj_cell:
            safe_adj_cell.remove(self.last_position)

        return safe_adj_cell