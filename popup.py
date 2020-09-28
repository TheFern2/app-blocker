from tkinter import *
import tkinter.messagebox

def show_popup(message):
    root = Tk()
    root.wm_withdraw()
    tkinter.messagebox.showinfo('Message of the day', message)
    root.destroy()

if __name__ == '__main__':
    show_popup('Get back to work!')