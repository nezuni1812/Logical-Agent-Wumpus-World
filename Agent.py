from KnowledgeBase import WumpusKB

class Agent:
    def __init__(self, interface):
        self.interface = interface
        self.current_position = (1, 1)
        self.KB = WumpusKB()
        self.interface.set_agent_cell(self.current_position)

    def perceive_current_cell(self):
        cell_info = self.interface.get_percepts()
        self.KB = self.KB.add_clause(cell_info)
        return cell_info
    
    def perform_action(self, action):
        self.interface.log_action(action)
