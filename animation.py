import tkinter as tk
import time

from math import pi, sin, cos

class Alien(object):
    def __init__(self, canvas, *args, **kwargs):
        self.canvas = canvas
        self.id = canvas.create_oval(*args, **kwargs)
        self.vx = 5
        self.vy = 0
        self.phi = 0
        self.speed = 1
        self.r = 10

    def move(self):
        x1, y1, x2, y2 = self.canvas.bbox(self.id)
        
        new_phi = (self.phi + self.speed) / (2 * pi)
        
        self.vx = self.r * (cos(new_phi) - cos(self.phi))
        self.vy = self.r * (sin(new_phi) - sin(self.phi))
        self.phi = new_phi
        print(self.phi)

                
        self.canvas.move(self.id, self.vx, self.vy)

class App(object):
    def __init__(self, master, **kwargs):
        self.master = master
        self.canvas = tk.Canvas(self.master, width=400, height=400)
        self.canvas.pack()

        
        self.aliens = [
            Alien(self.canvas, 130, 130, 160, 160, outline='white', fill='red'),
        ]
        self.canvas.pack()
        self.master.after(0, self.animation)
        
        self.label = tk.Label(text='Look up for other gamers')
        self.label.pack()

    def animation(self):
        for alien in self.aliens:
            alien.move()
        self.master.after(12,  self.animation)

root = tk.Tk()
app = App(root)
root.mainloop()
