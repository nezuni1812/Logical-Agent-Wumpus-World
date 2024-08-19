from Agent import Agent
from Interface import Interface
from Program import Program
import UI
import copy

if __name__ == "__main__":
    program = Program('map2.txt', 'result1.txt')
    interface = Interface(program)
    agent = Agent(interface)
    
    program.display_grid()
    UI.grid = copy.deepcopy(program.grid)
    agent.backtracking_search()
    
    print('State log size:', len(program.states_log))
    
    UI.states_log = program.states_log
    UI.init()
    program.display_grid()