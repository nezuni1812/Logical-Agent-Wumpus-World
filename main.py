from Agent import Agent
from Interface import Interface
from Program import Program
import UI
import copy

if __name__ == "__main__":
    # program = Program('map9.txt', 'result9.txt')
    # program = Program('map8.txt', 'result8.txt')
    # program = Program('map7.txt', 'result7.txt')
    # program = Program('map6.txt', 'result6.txt')
    # program = Program('map5.txt', 'result5.txt')
    # program = Program('map4.txt', 'result4.txt')
    # program = Program('map3.txt', 'result3.txt')
    # program = Program('map2.txt', 'result2.txt')
    # program = Program('map1.txt', 'result1.txt')
    interface = Interface(program)
    agent = Agent(interface)
    
    program.display_grid()
    UI.load_map(copy.deepcopy(program.grid))
    agent.backtracking_search()
    
    print('State log size:', len(program.states_log))
    
    UI.states_log = program.states_log
    UI.init()
    program.display_grid()