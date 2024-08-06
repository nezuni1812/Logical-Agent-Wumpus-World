from Agent import Agent
from Interface import Interface
from Program import Program

if __name__ == "__main__":
    program = Program('map1.txt', 'result1.txt')
    interface = Interface(program)
    agent = Agent(interface)
    # agent.perceive_current_cell()
    # print(agent.check_safeadjcell())
    # print(agent.do_in_percept())
    agent.backtracking_search()