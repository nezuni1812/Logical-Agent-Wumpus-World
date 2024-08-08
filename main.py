from Agent import Agent
from Interface import Interface
from Program import Program

if __name__ == "__main__":
    program = Program('map1.txt', 'result1.txt')
    interface = Interface(program)
    agent = Agent(interface)
    # print(agent.perceive_current_cell())
    # print(agent.check_safeadjcell())
    # print(agent.do_in_percept())
    program.display_grid()
    # state = [(1,1), "N", "SHOOT_WUMPUS", 0, 100, 0]
    # agent.interface.log_state(state)
    agent.backtracking_search()
    # program.display_grid()
    # state = [(1,1), "N", "SHOOT_WUMPUS", 0, 100, 0]
    # agent.interface.log_state(state)
    program.display_grid()