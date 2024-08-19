from Agent import Agent
from Interface import Interface
from Program import Program
import UI
import copy

if __name__ == "__main__":
    program = Program('map2.txt', 'result1.txt')
    interface = Interface(program)
    agent = Agent(interface)
    # print(agent.perceive_current_cell())
    # print(agent.check_safeadjcell())
    # print(agent.do_in_percept())
    
    # program.display_grid()
    print(program.grid)
    
    # state = [(2,1), "N", "GRAB_HEALING_POTION", 0, 100, 0]
    # agent.interface.log_state(state)
    
    UI.grid = copy.deepcopy(program.grid)
    agent.backtracking_search()
    print(program.states_log)
    print('State size:', len(program.states_log))
    
    UI.states_log = program.states_log
    UI.init()
    # UI.load_map('map1.txt')
    
    # program.display_grid()
    # state = [(2,3), "N", "GRAB_HEALING_POTION", 0, 100, 0]
    # agent.interface.log_state(state)
    program.display_grid()
    print(program.grid)