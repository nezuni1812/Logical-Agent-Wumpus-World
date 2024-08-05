from Agent import Agent
from Interface import Interface
from Program import Program

if __name__ == "__main__":
    program = Program('map2.txt', 'result1.txt')
    interface = Interface(program)
    agent = Agent(interface)
    print(agent.current_position)
    print(agent.perceive_current_cell())