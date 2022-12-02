import tkinter as tk
from tkinter import filedialog, Text, Label
from PIL import Image, ImageTk
from tkmacosx import Button
import os
import parse

root = tk.Tk()

def addApp():
    print('test')
    filename = filedialog.askopenfilename(initialdir='./', title='Select File',
                                          filetypes=[("Excel files", ".xlsx .xls .csv")])
    parse.parse(filename)
    img = Image.open('fig.png')
    img = img.resize((560, 560),Image.ANTIALIAS)
    tkimage = ImageTk.PhotoImage(img)
    lbl = Label(frame, image = tkimage)
    lbl.image = tkimage
    lbl.place(x=0, y=0)


canvas = tk.Canvas(root, height=700, width=700, bg='#263D42')
canvas.pack()

frame = tk.Frame(root, bg='white')
frame.place(relwidth=0.8, relheight=0.8, relx = 0.1, rely = 0.1)

openFile = Button(root, text='Open File', padx=10, pady=5, fg='white',
                  bg='#263D42', command=addApp)
openFile.pack()

runApps = Button(root, text='Run Apps', padx=10, pady=5, fg='white', bg='#263D42')
runApps.pack()

root.mainloop()
