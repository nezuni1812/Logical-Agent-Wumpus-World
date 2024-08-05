from KnowledgeBase import *

class Agent:
    def __init__(self, interface):
        self.interface = interface
        self.current_position = (1, 1)
        self.KB = WumpusKB()
        self.interface.set_agent_cell(self.current_position)

    def perceive_current_cell(self):
        percept_types = self.interface.get_percepts()  # Example: {'P', '~W', '~S',...}
        x, y = self.current_position

        for percept in percept_types:
            percept_symbol = symbols(f'{percept}{x}{y}')
            
            # Convert percept to its logical representation if it is negative (e.g., '~W' for no Wumpus)
            if percept.startswith('~'):
                percept_symbol = Not(percept_symbol)
            
            self.KB.add_clause(percept_symbol)
        
        return percept_types
    
    def perform_action(self, action):
        self.interface.log_action(action)