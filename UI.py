import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
from tkinter import ttk
from ctypes import windll
import pyglet
import Program
import hupper

root = tk.Tk()
canvas = tk.Canvas(bg='#EBE4FA')
# Make text sharper
windll.shcore.SetProcessDpiAwareness(1)
# Add font file
pyglet.font.add_file('resource/FiraSansExtraCondensed-Bold.ttf')

states_log = []
grid = []
canvas_object_map = []
ele_img_list = list[list[list]]
ele_content_list: list[list[list]]
img_list = []

state_index = 0

PADDING_TOP = 55
PADDING_LEFT = 75
CELL_SIZE = 88.5 # pixels

def init():
    root.geometry('1064x900+-4+50')
    root.configure(background='#EBE4FA')
    
    canvas.pack(fill='both', expand=True)
    
    img= ImageTk.PhotoImage(Image.open("resource/image.png").resize((1995,1200)))
    canvas.create_image(-50, -64, image=img, anchor='nw')
    
    global ele_content_list
    global ele_img_list
    ele_img_list = [[[] for j in range(len(grid[0]))] for i in range(len(grid))]
    ele_content_list = [[[] for j in range(len(grid[0]))] for i in range(len(grid))]
    
    # draw_objects()
    draw_layout()
    # draw_path()
    global state_index
    root.bind("<Right>", lambda *args: next())
    # root.bind("<Left>", lambda *args: prev())
    # wum_img = ImageTk.PhotoImage(Image.open("resource/wumpus.png"))
    # wum = canvas.create_image(0, 0, image=wum_img, anchor='center')
    
    # canvas.pack()
    # root.update()
    root.mainloop()
    
def load_map(input_file):
    with open(input_file, 'r') as file:
        grid_size = int(file.readline().strip())
        grid = [line.strip().split('.') for line in file.readlines()]
        for x in range(grid_size):
            for y in range(len(grid[x])):
                cell_content = grid[x][y]
                if cell_content != '-':
                    objects = cell_content.split(',')
                    percept_numbers = []
                    
                    # Check and add percepts for each object occurrence
                    for obj in objects:
                        if obj == 'W':
                            percept_numbers.append('1')  # Wumpus
                        elif obj == 'P_G':
                            percept_numbers.append('3')  # Poisonous Gas
                        elif obj == 'P':
                            percept_numbers.append('2')  # Pit
                        elif obj == 'H_P':
                            percept_numbers.append('4')  # Healing Potion
                        elif obj == 'C':
                            percept_numbers.append('9')  # Chess of gold
                        
                    # Combine percepts into a string
                    grid[x][y] = ''.join(sorted(percept_numbers))
                else:
                    grid[x][y] = ''
        print(grid)
    
    
def next():
    global state_index
    state_index += 1
    draw_path()
    
def prev():
    global state_index
    state_index -= 1
    draw_path()
    
agent_img_src = Image.open("resource/agent.png").resize((76, 76))
agent_img = ImageTk.PhotoImage(agent_img_src)
agent = None
agent_rotation = 0
def draw_path():
    global states_log
    global agent_img
    global state_index
    global agent
    global agent_rotation
    print('Running...', len(states_log))
    
    state = states_log[state_index]
        
    print(state)
    before = state[0]
    after = state[1]
    action = state[2]
    
    if agent is None:
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
    
    if 'RIGHT' in action:
        print('Right')
        degree = 0
        while degree <= 90:
            canvas.delete(agent)
            agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation - degree))
            print('Right', degree)
            agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
            degree += 10
            root.update()
            root.after(40)
            
        canvas.delete(agent)
        agent_rotation += 90
        print(agent_rotation)
        agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation))
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        
    elif 'LEFT' in action:
        print('Left')
        degree = 0
        while degree <= 90:
            canvas.delete(agent)
            agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation + degree))
            agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
            degree += 10
            root.update()
            root.after(40)
        
        canvas.delete(agent)
        agent_rotation -= 90
        agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation))
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        
    elif 'FORWARD' in action:
        # while canvas.coords(agent)[0] != after[0]
        step = 15
        moveY = after[0] * CELL_SIZE / step
        moveX = after[1] * CELL_SIZE / step
        print('Current:', canvas.coords(agent))
        print('Next:', after[0]*CELL_SIZE + PADDING_TOP, after[1]*CELL_SIZE + PADDING_LEFT)
        for s in range(step):
            canvas.move(agent, moveX, moveY)
            root.update()
            root.after(20)
            
        # canvas.delete(agent)
        # canvas.moveto(agent, after[0]*CELL_SIZE + PADDING_TOP, after[1]*CELL_SIZE + PADDING_LEFT)
        
        
    root.update()
    # root.after(1000)
    
def draw_layout():
    global ele_content_list
    # print(len(ele_content_list), len(ele_content_list[0]))
    # return
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            cell_content = sorted(cell, reverse=True)
            # print('Cell content:', cell_content)
            while (len(cell_content)):
                img = None
                per_size = 96
                if cell_content[0] == '4':
                    print('Heal')
                    ele_content_list[i][j].append('Healer')
                    # print(ele_content_list)
                    # print('-----------')
                    # tet = canvas.create_text(j*CELL_SIZE + PADDING_LEFT, i*CELL_SIZE + PADDING_TOP, text='Healer', fill='#00ff75')
                    # ele_img_list[i][j].append(tet)
                    # img = ImageTk.PhotoImage(Image.open("resource/heal.png").resize((46, 46)))
                elif cell_content[0] == '1':
                    print('Wumpus')
                    ele_content_list[i][j].append('Wumpus')
                    # img = ImageTk.PhotoImage(Image.open("resource/wumpus.png").resize((46, 46)))
                elif cell_content[0] == '2':
                    print('Pit')
                    ele_content_list[i][j].append('Pit')
                    # img = ImageTk.PhotoImage(Image.open("resource/pit.png").resize((46, 46)))
                elif cell_content[0] == '3':
                    print('Poison')
                    ele_content_list[i][j].append('Poison')
                    # img = ImageTk.PhotoImage(Image.open("resource/poison.png").resize((46, 46)))
                elif cell_content[0] == '9':
                    print('Gold')
                    ele_content_list[i][j].append('Gold')
                    # img = ImageTk.PhotoImage(Image.open("resource/gold.png").resize((46, 46)))
                # Percepts
                elif cell_content[0] == '5':
                    print('Stench')
                    img = ImageTk.PhotoImage(Image.open("resource/stench.png").resize((per_size, per_size)))
                elif cell_content[0] == '6':
                    print('Breeze')
                    img = ImageTk.PhotoImage(Image.open("resource/breeze.png").resize((per_size, per_size)))    
                elif cell_content[0] == '7':
                    print('Whiff')
                    img = ImageTk.PhotoImage(Image.open("resource/whiff.png").resize((per_size, per_size)))
                elif cell_content[0] == '8':
                    print('Glitter')
                    img = ImageTk.PhotoImage(Image.open("resource/glitter.png").resize((per_size + 35, per_size + 35)))
                    
                if img is not None:
                    img_list.append(img)
                    canvas.create_image(j*CELL_SIZE + PADDING_LEFT, i*CELL_SIZE + PADDING_TOP, image=img)
                
                
                cell_content = cell_content[1:len(cell_content)]
                
            # print('ele content list:', ele_content_list)
            # if len(ele_content_list[i][j]) <= 0:
            #     continue
            wumpus_count = ele_content_list[i][j].count('Wumpus')
            text_height = 16
            content = set(ele_content_list[i][j])
            for id, item in enumerate(content):
                text_color = 'black'
                if item == 'Wumpus':
                    text_color = '#6B0090'
                elif item == 'Healer':
                    text_color = '#005008'
                elif item == 'Gold':
                    text_color = '#857F00'
                elif item == 'Pit':
                    text_color = 'black'
                elif item == 'Poison':
                    text_color = '#F00000'
                    
                if item == 'Wumpus' and wumpus_count > 1:
                    item = item + ' ' + str(wumpus_count) + 'x'
                
                ele_img_list[i][j].append(canvas.create_text(j*CELL_SIZE + PADDING_LEFT/2.3, i*CELL_SIZE + PADDING_TOP - (text_height * len(content)/2) + id*text_height + 6, text=item, font=('Fira Sans Extra Condensed Bold', 14, 'bold'), anchor='w', fill=text_color))
                # bbox = canvas.bbox(ele_img_list[i][j][-1])
                # rect_item = canvas.create_rectangle(bbox, outline="white", fill="white")
            # print('End of cell')
            # return

    
    
def start(index = 0):
    
    pass


demo_states = [
    [(3, 0), (-1, 0), 'SHOOT_WUMPUS', 0, 100, 0],
    [(3, 0), (-1, 0), 'HEARD_SCREAM', 0, 100, 0],
    [(3, 0), (-1, 0), 'TURN_RIGHT', -100, 100, 0],
    [(3, 0), (0, 1), 'SHOOT_WUMPUS', -110, 100, 0],
    [(3, 0), (0, 1), 'HEARD_NOTHING', -110, 100, 0],
    [(3, 0), (0, 1), 'MOVE_FORWARD', -210, 100, 0],
    [(3, 1), (0, 1), 'SHOOT_WUMPUS', -220, 100, 0],
    [(3, 1), (0, 1), 'HEARD_NOTHING', -220, 100, 0],
    [(3, 1), (0, 1), 'TURN_LEFT', -320, 100, 0],
    [(3, 1), (-1, 0), 'SHOOT_WUMPUS', -330, 100, 0],
    [(3, 1), (-1, 0), 'HEARD_SCREAM', -330, 100, 0],
    [(3, 1), (-1, 0), 'TURN_RIGHT', -430, 100, 0],
    [(3, 1), (0, 1), 'MOVE_FORWARD', -440, 100, 0],
    [(3, 2), (0, 1), 'SHOOT_WUMPUS', -450, 100, 0],
    [(3, 2), (0, 1), 'HEARD_SCREAM', -450, 100, 0],
    [(3, 2), (0, 1), 'TURN_LEFT', -550, 100, 0],
    [(3, 2), (-1, 0), 'SHOOT_WUMPUS', -560, 100, 0],
    [(3, 2), (-1, 0), 'HEARD_NOTHING', -560, 100, 0],
    [(3, 2), (-1, 0), 'MOVE_FORWARD', -660, 100, 0],
    [(2, 2), (-1, 0), 'GRAB_HEALING_POTION', -670, 100, 0],
    [(2, 2), (-1, 0), 'SHOOT_WUMPUS', -680, 100, 1],
    [(2, 2), (-1, 0), 'HEARD_NOTHING', -680, 100, 1],
    [(2, 2), (-1, 0), 'TURN_RIGHT', -780, 100, 1],
    [(2, 2), (0, 1), 'SHOOT_WUMPUS', -790, 100, 1],
    [(2, 2), (0, 1), 'HEARD_SCREAM', -790, 100, 1],
    [(2, 2), (0, 1), 'TURN_RIGHT', -890, 100, 1],
    [(2, 2), (1, 0), 'TURN_RIGHT', -900, 100, 1],
    [(2, 2), (0, -1), 'SHOOT_WUMPUS', -910, 100, 1],
    [(2, 2), (0, -1), 'HEARD_SCREAM', -910, 100, 1],
    [(2, 2), (0, -1), 'TURN_RIGHT', -1010, 100, 1],
    [(2, 2), (-1, 0), 'MOVE_FORWARD', -1020, 100, 1],
    [(1, 2), (-1, 0), 'MOVE_FORWARD', -1030, 100, 1],
    [(0, 2), (-1, 0), 'TURN_RIGHT', -1040, 100, 1],
    [(0, 2), (0, 1), 'TURN_RIGHT', -1050, 100, 1],
    [(0, 2), (1, 0), 'MOVE_FORWARD', -1060, 100, 1],
    [(1, 2), (1, 0), 'TURN_RIGHT', -1070, 100, 1],
    [(1, 2), (0, -1), 'MOVE_FORWARD', -1080, 100, 1],
    [(1, 1), (0, -1), 'TURN_LEFT', -1090, 100, 1],
    [(1, 1), (1, 0), 'MOVE_FORWARD', -1100, 100, 1],
    [(2, 1), (1, 0), 'TURN_RIGHT', -1110, 100, 1],
    [(2, 1), (0, -1), 'SHOOT_WUMPUS', -1120, 100, 1],
    [(2, 1), (0, -1), 'HEARD_SCREAM', -1120, 100, 1],
    [(2, 1), (0, -1), 'MOVE_FORWARD', -1220, 100, 1],
    [(2, 0), (0, -1), 'TURN_RIGHT', -1230, 100, 1],
    [(2, 0), (-1, 0), 'MOVE_FORWARD', -1240, 100, 1],
    [(1, 0), (-1, 0), 'MOVE_FORWARD', -1250, 100, 1],
    [(0, 0), (-1, 0), 'GRAB_HEALING_POTION', -1260, 100, 1],
    [(0, 0), (-1, 0), 'TURN_RIGHT', -1270, 100, 2],
    [(0, 0), (0, 1), 'TURN_RIGHT', -1280, 100, 2],
    [(0, 0), (1, 0), 'MOVE_FORWARD', -1290, 100, 2],
    [(1, 0), (1, 0), 'TURN_LEFT', -1300, 100, 2],
    [(1, 0), (0, 1), 'MOVE_FORWARD', -1310, 100, 2],
    [(1, 1), (0, 1), 'MOVE_FORWARD', -1320, 100, 2],
    [(1, 2), (0, 1), 'MOVE_FORWARD', -1330, 100, 2],
    [(1, 3), (0, 1), 'TURN_RIGHT', -1340, 100, 2],
    [(1, 3), (1, 0), 'MOVE_FORWARD', -1350, 100, 2],
    [(2, 3), (1, 0), 'SHOOT_WUMPUS', -1360, 100, 2],
    [(2, 3), (1, 0), 'HEARD_SCREAM', -1360, 100, 2],
    [(2, 3), (1, 0), 'MOVE_FORWARD', -1460, 100, 2]
]

demo_map = [
    ['123496', '123495678', '6', '2', '', '', '', '', '', ''],
    ['58', '56', '8', '56'],
    ['115', '1158', '45', '158'],
    ['5', '5', '58', '115'],
    ['5', '5', '58', '115'],
    ['5', '5', '58', '115'],
    ['5', '5', '58', '115'],
    ['5', '5', '58', '115'],
    ['5', '5', '58', '115', '8765'],
    ['5', '5', '58', '115', '115', '115', '5', '6', '7', '8'],
]

if __name__ == "__main__":
    # load_map(demo_states)
    grid = demo_map
    init()
    # root.mainloop()
    

