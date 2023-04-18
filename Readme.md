# ChichiTk

ChichiTk is a python UI library built upon Tkinter, which implements affectedly elegant extensions of existing tkinter widgets. Further description...

![](documentation_images/example_app.jpg)
| _`example.py` on Windows_

https://user-images.githubusercontent.com/74847576/232877538-c069685a-3265-42d0-9961-73ccd59c9738.mp4

| _`example.py` on Windows - sample user interactions_

## Installation
Install the module with pip:
```
pip3 install chichitk
```
Update existing installation:
```
pip3 install chichitk --upgrade
```
Update as often as possible because this library is under active development.

## Documentation
The **official** documentation can be found in the Wiki Tab here:

**--> [ChichiTk Documentation](https://github.com/SamGibson1/ChichiTk/wiki)**

## Example Program
The following is a simple Stopwatch program that uses chichitk.Player to manage callbacks:
```python
from tkinter import Tk, Frame, Label
from chichitk import Player

def time_text(time:int, f:int=100):
    hour = time // (3600 * f)
    minute = (time % (3600 * f)) // (60 * f)
    second = (time % (60 * f)) // f
    return f'{hour:0>2}:{minute:0>2}:{second:0>2}.{time % f:0>2}'

app = Tk()
app.title('Stopwatch')
app.config(bg='#28282e')
app.geometry("650x400")

frame = Frame(app)
frame.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.6, anchor='center')

label = Label(frame, text='00:00:00.00', bg='#232328', fg='#ffffff',
              font=('Segoe UI bold', 30))
label.pack(fill='both', expand=True)

Play = Player(frame, lambda t: label.config(text=time_text(t)), 0.01,
              bg='#1e1e22', frame_num=12001, frame_rate=100, step_increment=500)
Play.pack(side='bottom', fill='x')

app.mainloop()
```
This results in the following window on Windows:
<img src="documentation_images/stopwatch_example.jpg" width="600"/>

## Sample Application - Password Manager
Video here showing password manager and link to git repo for password manager
