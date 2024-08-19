from Agent import Agent
from Interface import Interface
from Program import Program
import UI
import copy

if __name__ == "__main__":
    program = Program('map1.txt', 'result1.txt')
    interface = Interface(program)
    agent = Agent(interface)
    
    program.display_grid()
    UI.load_map(copy.deepcopy(program.grid))
    agent.backtracking_search()
    
    print('State log size:', len(program.states_log))
    
    UI.states_log = program.states_log
    UI.init()
    program.display_grid()