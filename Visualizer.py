from tkinter import *
from tkinter import ttk
import Program
import hupper

def start_reloader():
    reloader = hupper.start_reloader('main.main')

class Visualizer:
    def __init__(self, grid: list = None, init_func = None) -> None:
        if grid is None:
            self.maze = []
        else: 
            self.maze = grid
        
        self.BOX_WIDTH = 50
        self.PAD = 5
        
        self.colors = {
            "-" : "fff", #Nothing
            "1" : "2c6fc3", #Wumpus
            "2" : "000000", #Pit
            "3" : "52a447", #Poisonous Gas
            "4" : "ff2400", #Healing Potion
            "9" : "eedd82"  #Chest of Gold
        }
        
        self.root  = Tk()
        self.root.geometry = ('1040x760')
        self.root.configure(background='#696969')

        self.canvas = Canvas()
        self.canvas.pack(fill='both', expand=False)

        self.draw_screen()
        self.make_boxes()
        self.canvas.pack()
        self.images = []

    #def set_map(self, map: list):
    #    self.maze = map
    def draw_screen(self):
        self.canvas.pack()
        self.root.update()
    
    def make_boxes(self):
        for j, _ in enumerate(self.maze):
            for i, _ in enumerate(self.maze[0]):
                x0 = i*self.BOX_WIDTH + self.PAD
                y0 = j*self.BOX_WIDTH + self.PAD
                x1 = (i + 1)*self.BOX_WIDTH + self.PAD
                y1 = (j + 1)*self.BOX_WIDTH + self.PAD
                if (self.maze[j][i] in self.colors):
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.colors[self.maze[j][i]], width=1)
                elif (isinstance(self.maze[j][i], str) and any(c.isalpha() for c in self.maze[j][i])):
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.colors[self.maze[j][i][0]], width=1)
                    self.canvas.create_text(x0 + self.BOX_WIDTH/2, y0 + self.BOX_WIDTH/2, text=self.maze[j][i])
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='#dae8fc', width=1)
                    self.canvas.create_text(x0 + self.BOX_WIDTH/2, y0 + self.BOX_WIDTH/2, text=self.maze[j][i])
    
def main():
    program = Program.Program('map2.txt', 'result1.txt')
    visuals = Visualizer(program.grid)
    visuals.root.mainloop()
    # visuals.draw()

if __name__ == '__main__':
    # start_reloader()
    main()