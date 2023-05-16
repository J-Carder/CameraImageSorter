#Import the tkinter library
from tkinter import *
import tkinter.tix

#Create an instance of tkinter frame
win = Tk()
#Set the geometry
#win.geometry("600x450")

#Create a tooltip
tip = tix.Balloon(win)

#Create a Button widget
my_button=Button(win, text= "Hover Me")
my_button.pack(pady=20)

#Bind the tooltip with button
tip.bind_widget(my_button,balloonmsg="www.tutorialspoint.com")

win.mainloop()