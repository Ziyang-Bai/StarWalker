# -*- coding: utf-8 -*-
from tkinter import *
import os
from time import *
import json

def showWelcome():
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.overrideredirect(True)
    x = (sw - 475) / 2
    y = (sh - 158) / 2
    root.geometry("475x158+%d+%d" % (x, y))
    root['bg'] = 'lightgray'
    if os.path.exists(".//config//config.json"):
        with open(".//config//config.json", "r") as f:
            config = json.load(f)
    else:
        print("FATAL ERROR!config.json does not exist!")
    if os.path.exists('.//lib//image//starwalker-welcome.png'):
        bm = PhotoImage(file='.//lib//image//starwalker-welcome.png')
        lb_welcomelogo = Label(root, image=bm, bg='black')
        lb_welcomelogo.bm = bm
        lb_welcomelogo.place(x=0, y=0)
    else:
        print("FATAL ERROR!starwalker-welcome.png starwalker-welcome.png does not exist!")
    lb_welcometext_text = config['name'] + " " + config['version'] + " " + config['snapshout']
    lb_welcometext = Label(root, text=lb_welcometext_text,
                           fg='black', bg='lightgray', font=('Courier', 10))
    lb_welcometext.place(x=0, y=143, width=475, height=15)

    # Schedule the root window to   be destroyed after 5 seconds
    root.after(5000, main)


def main():
    # Start Up the starwalker
    import starwalkerCore
    root.destroy()
    starwalkerCore.main()
if __name__ == '__main__':
    root = Tk()
    showWelcome()
    root.mainloop()