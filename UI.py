import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
from tkinter import ttk
from ctypes import windll
import pyglet
import copy
import Program
import hupper

root = tk.Tk()
canvas = tk.Canvas(bg='#EBE4FA')
# Make text sharper
windll.shcore.SetProcessDpiAwareness(1)
# Add font file
pyglet.font.add_file('resource/FiraSansExtraCondensed-Bold.ttf')

states_log = []
grid_log = []
grid = []
original_grid = []
visited_grid = []
canvas_object_map = []
ele_img_list = list[list[list]]
ele_content_list: list[list[list]]
img_list = []

state_index = -1

PADDING_TOP = 55
PADDING_LEFT = 75
CELL_SIZE = 88.5 # pixels

def init():
    root.geometry('1464x900+-4+50')
    root.configure(background='#EBE4FA')
    
    canvas.pack(fill='both', expand=True)
    
    img= ImageTk.PhotoImage(Image.open("resource/image.png").resize((1995,1200)))
    canvas.create_image(-50, -64, image=img, anchor='nw')
    
    global ele_content_list
    global ele_img_list
    global visited_grid
    global original_grid
    global grid
    grid = copy.deepcopy(original_grid)
    print('Grid size', len(grid), len(grid[0]))
    visited_grid = [[False for j in range(len(grid[0]))] for i in range(len(grid))]
    ele_img_list = [[[] for j in range(len(grid[0]))] for i in range(len(grid))]
    ele_content_list = [[[] for j in range(len(grid[0]))] for i in range(len(grid))]
    
    # draw_objects()
    draw_layout()
    # draw_path()
    global state_index
    global agent_rotation
    global is_autoplay
    is_autoplay = False
    root.bind("<Right>", lambda *args: next())
    root.bind("<Return>", lambda *args: init())
    root.bind("<space>", lambda *args: autoplay(True))
    state_index = -1
    agent_rotation = 0
    draw_text('Hell world')
    draw_path()
    root.mainloop()
    
def load_map(input_grid):
    global grid
    global original_grid
    original_grid = grid = input_grid
    
    
def next():
    global state_index
    state_index += 1
    draw_path()
    
def prev():
    global state_index
    state_index -= 1
    draw_path()
    
is_autoplay = False
def autoplay(toggle=False):
    global is_autoplay
    global state_index
    global states_log
    if toggle:
        print('Autoplay toggled', not is_autoplay)
        is_autoplay = not is_autoplay
    
    if state_index >= len(states_log):
        return
    
    if not is_autoplay:
        return
    
    state_index += 1
    draw_path()
    root.after(100, lambda: autoplay())
    
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
    
    if state_index >= len(states_log):
        draw_text(heading='Game over!')
        return
    
    global ele_img_list
    for row in ele_img_list:
        canvas.delete(row)
    draw_layout()
    draw_unvisited()
    
    if state_index != -1:
        state = states_log[state_index]
    else:
        agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation))
        canvas.delete(agent)
        agent = canvas.create_image(0*CELL_SIZE + PADDING_LEFT, 9*CELL_SIZE + PADDING_TOP, image=agent_img)
        visited_grid[9][0] = True
        draw_unvisited()
        root.update()
        return
        
    # Print current state to the terminal
    print('Current state:', state)
    before = state[0]
    after = state[1]
    action = state[2]
    
    # Update the texts based on the state
    draw_text(step=f'{state_index}. {action.replace("_", " ")}', more=f'Point: {state[3]}, HP: {state[4]}, Heal Potions left: {state[5]}')
    
    if agent is None:
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
    
    # Draw the agent based on the action
    if 'RIGHT' in action:
        # print('Right')
        degree = 0
        while degree <= 90:
            canvas.delete(agent)
            agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation - degree))
            # print('Right', degree)
            agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
            degree += 10
            root.update()
            root.after(10)
            
        canvas.delete(agent)
        agent_rotation += 90
        # print(agent_rotation)
        agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation))
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        
    elif 'LEFT' in action:
        # print('Left')
        degree = 0
        while degree <= 90:
            canvas.delete(agent)
            agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation + degree))
            agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
            degree += 10
            root.update()
            root.after(10)
        
        canvas.delete(agent)
        agent_rotation -= 90
        agent_img = ImageTk.PhotoImage(agent_img_src.rotate(-agent_rotation))
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        
    elif 'FORWARD' in action:
        # while canvas.coords(agent)[0] != after[0]
        step = 15
        canvas.delete(agent)
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        
        moveY = after[0] * CELL_SIZE / step
        moveX = after[1] * CELL_SIZE / step
        # print('Current:', canvas.coords(agent))
        # print('Next:', after[0]*CELL_SIZE + PADDING_TOP, after[1]*CELL_SIZE + PADDING_LEFT)
        for s in range(step):
            canvas.move(agent, moveX, moveY)
            root.update()
            root.after(5)
            
        visited_grid[before[0] + after[0]][before[1] + after[1]] = True
        draw_unvisited()
        # canvas.delete(agent)
        # canvas.moveto(agent, after[0]*CELL_SIZE + PADDING_TOP, after[1]*CELL_SIZE + PADDING_LEFT)
    elif 'SHOOT' in action:
        canvas.delete(agent)
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        draw_status(before[0], before[1], '🔫')
        destroy_wumpus(before[0], before[1], agent_rotation)
    elif 'GOLD' in action:
        canvas.delete(agent)
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        take_gold(before[0], before[1])
    elif 'GRAB_HEALING_POTION' in action:
        canvas.delete(agent)
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        take_heal(before[0], before[1])
    elif 'USE_HEALING_POTION' in action:
        canvas.delete(agent)
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        draw_status(before[0], before[1], '✨')
    elif 'SCREAM' in action:
        canvas.delete(agent)
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        draw_status(before[0], before[1], '❗')
    elif 'NOTHING' in action:
        canvas.delete(agent)
        agent = canvas.create_image(before[1]*CELL_SIZE + PADDING_LEFT, before[0]*CELL_SIZE + PADDING_TOP, image=agent_img)
        draw_status(before[0], before[1], '✅')
    
        
    root.update()
    # root.after(1000)
    
text_status = None
def draw_status(row, col, content):
    global text_status
    if text_status is not None:
        canvas.delete(text_status)
    text_status = canvas.create_text(col*CELL_SIZE + 1.4*PADDING_LEFT, row*CELL_SIZE + PADDING_TOP - 20, text=content, font=('Fira Sans Extra Condensed Bold', 18, 'bold'))
    ele_img_list.append(text_status)
    root.update()
    
text_list = [None, None, None, None]
def draw_text(heading = None, step = None, more = None, other = None, instruction = '<Arrow ▶> for next move\n<Space ␣> for autoplay\n<Enter ↵> for restarting'):
    if heading is not None:
        if text_list[0] is not None:
            canvas.delete(text_list[0])
        text_list[0] = canvas.create_text(960, 10, text=heading, anchor='nw', font=('Fira Sans Extra Condensed', 28))
    if step is not None:
        if text_list[1] is not None:
            canvas.delete(text_list[1])
        text_list[1] = canvas.create_text(960, 60, text=step, anchor='nw', font=('Fira Sans Extra Condensed', 18))
    if more is not None:
        if text_list[2] is not None:
            canvas.delete(text_list[2])
        text_list[2] = canvas.create_text(960, 90, text=more, anchor='nw', font=('Fira Sans Extra Condensed', 16))
    if other is not None:
        if text_list[3] is not None:
            canvas.delete(text_list[3])
        text_list[3] = canvas.create_text(960, 110, text=other, anchor='nw', font=('Fira Sans Extra Condensed', 16))
    if instruction is not None:
        if text_list[3] is not None:
            canvas.delete(text_list[3])
        text_list[3] = canvas.create_text(960, 140, text=instruction, anchor='nw', font=('Fira Sans Extra Condensed', 16))
    
def is_close_to_target(i, j, target):
    global grid
    for x in range(i-1, i+2):
        for y in range(j-1, j+2):
            if x >= 0 and x < len(grid) and y >= 0 and y < len(grid[0]) and (x == i or y == j):
                if target in grid[x][y]:
                    return True
    return False
    
def take_heal(row, col):
    global grid
    if '4' in grid[row][col]:
        # print('Remove healer at:', row, col)
        grid[row][col] = grid[row][col].replace('4', '', 1)
        for i in range(row-1, row+2):
            for j in range(col-1, col+2):
                if i >= 0 and i < len(grid) and j >= 0 and j < len(grid[0]):
                    if '8' in grid[i][j] and not is_close_to_target(i, j, '4'):
                        grid[i][j] = grid[i][j].replace('8', '', 1)
        return True
    return False
    
def destroy_wumpus(row, col, degree):
    global grid
    if degree % 360 == 0:
        for i in range(row, -1, -1):
            if '1' in grid[i][col]:
                row = i
                break
    elif degree % 360 == 90:
        for i in range(col, len(grid[0])):
            if '1' in grid[row][i]:
                col = i
                break
    elif degree % 360 == 180:
        for i in range(row, len(grid)):
            if '1' in grid[i][col]:
                row = i
                break
    elif degree % 360 == 270:
        for i in range(col, -1, -1):
            if '1' in grid[row][i]:
                col = i
                break
        
    if '1' in grid[row][col]:
        # print('Remove wumpus at:', row, col)
        grid[row][col] = grid[row][col].replace('1', '', 1)
        for i in range(row-1, row+2):
            for j in range(col-1, col+2):
                if i >= 0 and i < len(grid) and j >= 0 and j < len(grid[0]):
                    if '5' in grid[i][j] and not is_close_to_target(i, j, '1'):
                        grid[i][j] = grid[i][j].replace('5', '', 1)
        return True
    return False

def take_gold(row, col):
    global grid
    if '9' in grid[row][col]:
        # print('Remove gold at:', row, col)
        grid[row][col] = grid[row][col].replace('9', '', 1)
    
unvisited_img = img = ImageTk.PhotoImage(Image.open("resource/blur.png").resize((79, 79)))
unvisited_block = []

def draw_unvisited():
    global visited_grid
    for i in unvisited_block:
        canvas.delete(i)
        
    for i in range(len(visited_grid)):
        for j in range(len(visited_grid[0])):
            if not visited_grid[i][j]:
                unvisited_block.append(canvas.create_image(j*CELL_SIZE + PADDING_LEFT - 2, i*CELL_SIZE + PADDING_TOP - 2, image=unvisited_img, anchor='center'))
    
    
def draw_layout():
    global ele_content_list
    global state_index
    global ele_img_list
    
    ele_content_list = [[[] for j in range(len(grid[0]))] for i in range(len(grid))]
    current_grid = []
    current_grid = grid
        
    for i, row in enumerate(current_grid):
        for j, cell in enumerate(row):
            cell_content = sorted(cell, reverse=True)
            # print('Cell content:', cell_content)
            while (len(cell_content)):
                img = None
                per_size = 96
                if cell_content[0] == '4':
                    ele_content_list[i][j].append('Healer')
                elif cell_content[0] == '1':
                    ele_content_list[i][j].append('Wumpus')
                elif cell_content[0] == '2':
                    ele_content_list[i][j].append('Pit')
                elif cell_content[0] == '3':
                    ele_content_list[i][j].append('Poison')
                elif cell_content[0] == '9':
                    ele_content_list[i][j].append('Gold')
                # Percepts
                elif cell_content[0] == '5':
                    img = ImageTk.PhotoImage(Image.open("resource/stench.png").resize((per_size, per_size)))
                elif cell_content[0] == '6':
                    img = ImageTk.PhotoImage(Image.open("resource/breeze.png").resize((per_size, per_size)))    
                elif cell_content[0] == '7':
                    img = ImageTk.PhotoImage(Image.open("resource/whiff.png").resize((per_size, per_size)))
                elif cell_content[0] == '8':
                    img = ImageTk.PhotoImage(Image.open("resource/glitter.png").resize((per_size + 35, per_size + 35)))
                    
                if img is not None:
                    img_list.append(img)
                    ele_img_list.append(canvas.create_image(j*CELL_SIZE + PADDING_LEFT, i*CELL_SIZE + PADDING_TOP, image=img))
                
                
                cell_content = cell_content[1:len(cell_content)]
                
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
                
                ele_img_list.append(canvas.create_text(j*CELL_SIZE + PADDING_LEFT/2.3, i*CELL_SIZE + PADDING_TOP - (text_height * len(content)/2) + id*text_height + 6, text=item, font=('Fira Sans Extra Condensed Bold', 14, 'bold'), anchor='w', fill=text_color))

    
    
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
    

