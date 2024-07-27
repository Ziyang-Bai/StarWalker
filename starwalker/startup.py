from tkinter import *
import os
from time import *

def showWelcome():
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.overrideredirect(True)
    x = (sw - 475) / 2
    y = (sh - 158) / 2
    root.geometry("475x158+%d+%d" % (x, y))
    root['bg'] = 'lightgray'

    if os.path.exists('.//lib//image//starwalker-welcome.png'):
        bm = PhotoImage(file='.//lib//image//starwalker-welcome.png')
        lb_welcomelogo = Label(root, image=bm, bg='black')
        lb_welcomelogo.bm = bm
        lb_welcomelogo.place(x=0, y=0)

    lb_welcometext = Label(root, text='StarWalker - OpenSource Project - MPL-2.0 licence',
                           fg='black', bg='lightgray', font=('Courier', 10))
    lb_welcometext.place(x=0, y=143, width=475, height=15)

    # Schedule the root window to   be destroyed after 5 seconds
    root.after(5000, perform_other_tasks)


def perform_other_tasks():
    # Start Up the starwalker
    print("Performing other tasks...")
    sleep(1)
    root.destroy()

if __name__ == '__main__':
    root = Tk()
    showWelcome()
    root.mainloop()