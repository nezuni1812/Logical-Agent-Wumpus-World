import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
from tkinter import ttk
import Program
import hupper

root = tk.Tk()
canvas = tk.Canvas(bg='#EBE4FA')

states_log = []

def init():
    root.geometry('1064x660+-4+50')
    root.configure(background='#EBE4FA')
    
    canvas.pack(fill='both', expand=True)
    
    img= ImageTk.PhotoImage(Image.open("resource/image.png").resize((1330,800)))
    canvas.create_image(-20, -20, image=img, anchor='nw')
    
    # canvas.pack()
    # root.update()
    root.mainloop()
    
def start(index = 0):
    
    pass


if __name__ == "__main__":
    init()
    root.mainloop()
    