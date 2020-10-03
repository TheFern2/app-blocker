from tkinter import Tk
import tkinter.messagebox

def show_popup(message):
    root = tkinter.Tk()
    root.wm_withdraw()
    tkinter.messagebox.showinfo('Message of the day', message)
    root.destroy()

if __name__ == '__main__':
    show_popup('Get back to work!')