from KnowledgeBase import *
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
        self.current_position = (1, 1)
        self.current_hp = 100
        self.heal_potions = 0
        self.is_alive = True
        self.KB = WumpusKB()
        self.interface.set_agent_cell(self.current_position)
        self.current_percept = []
        self.point = 0

    def perceive_current_cell(self):
        percept_types = self.interface.get_percepts()  # Example: {'P', '~W', '~S',...}
        self.current_percept = percept_types
        x, y = self.current_position

        for percept in percept_types:
            is_not = False
            if percept.startswith('~'):
                is_not = True
                percept = percept[1:]

            percept_symbol = symbols(f'{percept}{x}{y}')

            # Convert percept to its logical representation if it is negative (e.g., '~W' for no Wumpus)
            if is_not:
                percept_symbol = Not(percept_symbol)

            elif percept == 'S':
                neighbors = get_adj_cell(x, y)
                neighbor_literals = [symbols(f'W{nx}{ny}') for nx, ny in neighbors]
                percept_symbol = Or(*neighbor_literals)  # Fix: Create OR clause for all adjacent Wumpus positions
            
            elif percept == 'B':
                neighbors = get_adj_cell(x, y)
                neighbor_literals = [symbols(f'P{nx}{ny}') for nx, ny in neighbors]
                percept_symbol = Or(*neighbor_literals)  # Fix: Create OR clause for all adjacent Pit positions
            
            elif percept == 'W_H':
                neighbors = get_adj_cell(x, y)
                neighbor_literals = [symbols(f'P_G{nx}{ny}') for nx, ny in neighbors]
                percept_symbol = Or(*neighbor_literals)  # Fix: Create OR clause for all adjacent Gas positions

            elif percept == 'G_L':
                neighbors = get_adj_cell(x, y)
                neighbor_literals = [symbols(f'H_P{nx}{ny}') for nx, ny in neighbors]
                percept_symbol = Or(*neighbor_literals)  # Fix: Create OR clause for all adjacent Heal positions

            self.KB.add_clause(percept_symbol)  # Fix: Add clause as a list
        self.KB.print_KB()
        return percept_types
    
    def top_condition(self):
        for percept in self.current_percept:
            # if current step of agent have wumpus => game is finish, agent dies
            if percept == 'W':
                self.is_alive = False
                self.point -= 10000
                self.current_hp = 0
                self.interface.log_action('{self.current_position} BE_EATEN_BY_WUMPUS {self.point} {self.current_hp} {self.heal_potions}')

            # if current step of agent have pit => game is finish, agent dies
            if percept == 'P':
                self.is_alive = False
                self.point -= 10000
                self.current_hp = 0
                self.interface.log_action('{self.current_position} FALL_INTO_PIT {self.point} {self.current_hp} {self.heal_potions}')

            # if current step of agent have gold => agent grab gold
            if percept == 'G':
                self.point += 5000
                self.interface.log_action('{self.current_position} GRAB_GOLD {self.point} {self.current_hp} {self.heal_potions}')

            # # if current step of agent feel Stench => agent perceives Stench
            # if percept == 'S':
            #     self.interface.log_action('{self.current_position} PERCEIVE_STENCH {self.point} {self.current_hp}')
            
            # # if current step of agent feel Breeze => agent perceives Breeze
            # if percept == 'B':
            #     self.interface.log_action('{self.current_position} PERCEIVE_BREEZE {self.point} {self.current_hp}')

            if percept == 'H_P':
                self.heal_potions += 1
                self.point -= 10
                self.interface.log_action('{self.current_position} GRAB_HEALING_POTION {self.point} {self.current_hp} {self.heal_potions}')
                if self.current_hp < 100:
                    self.current_hp += 25
                    self.heal_potions -= 1
                    self.point -= 10
                    self.interface.log_action('{self.current_position} USE_HEALING_POTION {self.point} {self.current_hp} {self.heal_potions}')

            if percept == 'P_G':
                self.current_hp -= 25
                self.interface.log_action('{self.current_position} GO_TO_POISONOUS_GAS {self.point} {self.current_hp} {self.heal_potions}')
                if self.heal_potions >= 1:
                    self.current_hp += 25
                    self.heal_potions -= 1
                    self.point -= 10
                    self.interface.log_action('{self.current_position} USE_HEALING_POTION {self.point} {self.current_hp} {self.heal_potions}')
            
            # mark this cell explored and percepts to the KB
            if not self.agent_cell.is_explored():
                self.agent_cell.explore()
                self.add_KB(self.agent_cell)


    