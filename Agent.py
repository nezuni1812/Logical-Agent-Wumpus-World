from KnowledgeBase import *
from State import State
# W - ma, P: pit, G: gold, P_G: -25%, H_P: +25%, S: thúi, B: lạnh, 
# W_H: tỏa ra từ hơi độc, G_L: tỏa ra từ +25%
nextidx = [(0, 1), (0, -1), (-1, 0), (1, 0)]

def get_adj_cell(x, y):
    adj_cell = []
    for (d_x, d_y) in nextidx:
        row = x + d_x
        col = y + d_y
        if row >= 1 and row <= 10 and col >= 1 and col <= 10:
            adj_cell.append((row, col))  # Fix: Ensure tuple is appended correctly
    return adj_cell

class Agent:
    def __init__(self, interface):
        self.interface = interface
        self.current_position = (10, 1) # Start position is 1,1
        self.current_percept = []
        self.current_hp = 100
        self.heal_potions = 0
        self.is_alive = True
        self.point = 0
        self.KB = WumpusKB()
        self.interface.set_agent_cell(self.current_position)

    def perceive_current_cell(self):
        self.current_percept = self.interface.get_percepts()  # Example: {'P', '~W', '~S',...}
        x, y = self.current_position

        for percept in self.current_percept:
            if percept.startswith('~'):
                percept_symbol = symbols(f'{percept[1:]}{x}{y}')
                percept_symbol = Not(percept_symbol)
            else:
                percept_symbol = symbols(f'{percept}{x}{y}')
                if percept == 'S':
                    neighbors = get_adj_cell(x, y)
                    neighbor_literals = [symbols(f'W{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Fix: Create OR clause for all adjacent Wumpus positions
                
                elif percept == 'B':
                    neighbors = get_adj_cell(x, y)
                    neighbor_literals = [symbols(f'P{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Fix: Pit positions
                
                elif percept == 'W_H':
                    neighbors = get_adj_cell(x, y)
                    neighbor_literals = [symbols(f'P_G{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Fix: Gas positions

                elif percept == 'G_L':
                    neighbors = get_adj_cell(x, y)
                    neighbor_literals = [symbols(f'H_P{nx}{ny}') for nx, ny in neighbors]
                    percept_symbol = Or(*neighbor_literals)  # Fix: Heal positions

            self.KB.add_clause(percept_symbol)  # Fix: Add clause as a list
        self.KB.print_KB()
        return self.current_percept
    
    def top_condition(self):
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
                if self.current_hp < 100:
                    self.current_hp += 25
                    self.heal_potions -= 1
                    self.point -= 10
                    state[State.EVENT.value] = 'USE_HEALING_POTION'
                    self.interface.log_state(state)

            elif percept == 'P_G':
                self.current_hp -= 25
                if self.current_hp == 0:
                    self.is_alive = False
                else:
                    if self.heal_potions >= 1:
                        self.current_hp += 25
                        self.heal_potions -= 1
                        self.point -= 10
                        state[State.EVENT.value] = 'USE_HEALING_POTION'
                        self.interface.log_state(state)
                state[State.EVENT.value] = 'GO_TO_POISONOUS_GAS'
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