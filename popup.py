from tkinter import *
import tkinter.messagebox
import configparser

def show_popup(message):
    root = Tk()
    tkinter.messagebox.showinfo('Message of the day', message)
    root.mainloop()

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('app-blocker.conf')
    motd = config.get('Settings', 'motd')
    show_popup(motd)