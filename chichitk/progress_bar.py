from tkinter import Canvas, Frame, Label


class ProgressBar(Frame):
    ''' Progress bar that displays completion percentage and a label
    
        Completion percentage is computed in terms of iterations so that
        the progress bar can be easily increment with each iteration of a
        function using the .increment() method
    '''
    def __init__(self, master:Frame, iterations:int, bg:str, inactive_color=None,
                    active_color:str='#00ff00', text_color:str='#000000',
                    border_color:str='#ffffff', text='Loading...',
                    border_thickness=1, width=400, height=40, start_value:int=0,
                    text_font_name='Segoe UI bold', val_font_name='Segoe UI',
                    text_font_size=14, val_font_size=12, decimals:int=0,
                    text_side='bottom', center=True):
        '''Simple progress bar that displays completion percentage
        
        Parameters
        ----------
            :param master: tk.Frame - widget in which to pack progress bar
            :param iterations: int - number of iterations until completion
            :param bg: str (hex code) -  frame background color
            :param inactive_color: str (hex code) - color of uncompleted part of progress bar
            :param active_color: str (hex code) - color of completed part of progress bar
            :param text_color: str (hex code) - color of percentage label
            :param border_color: str (hex code) - color of canvas border
            :param text: str - text displayed while progress bar is running
            :param border_thickness: int - thickness of progress bar border
            :param width: int (pixels) - width of progress bar
            :param height: int (pixels) - height of progress bar
            :param start_value: int - iterations already complete
            :param decimals: int - number of decimal places to display on percentage
            :param text_side: str - where to pack loading text relative to progress bar
            :param center: bool - if True, progress bar will be placed within self
        '''
        Frame.__init__(self, master, bg=bg)
        self.width, self.height = width, height
        self.iterations = max(1, iterations)
        self.current_value = start_value
        self.decimals = decimals
        self.bd = border_thickness
        inactive_color = inactive_color if inactive_color else bg

        self.frame = Frame(self, bg=bg)
        if center:
            self.frame.place(relx=0.5, rely=0.5, anchor='center')
        else:
            self.frame.pack(side='top')
        self.loading_label = Label(self.frame, text=text, bg=bg, fg=text_color,
                                   font=(text_font_name, text_font_size))
        self.loading_label.pack(side=text_side)
        self.canvas = Canvas(self.frame, bg=inactive_color, width=self.width,
                             height=self.height, highlightthickness=self.bd,
                             highlightbackground=border_color)
        self.canvas.pack(side='left')
        self.label = Label(self.frame, text=self.get_percentage_text(), bg=bg,
                           fg=text_color, font=(val_font_name, val_font_size))
        self.label.pack(side='left')
        self.bar_id = self.canvas.create_rectangle(*self.get_bar_coords(),
                                                   fill=active_color, width=0,
                                                   state='normal')

    def set_text(self, text:str):
        '''updates progress bar loading text'''
        self.loading_label.config(text=text)

    def get_percentage_text(self) -> str:
        '''return completion percentage'''
        perc = self.current_value * 100 / self.iterations
        if self.decimals == 0:
            return str(int(perc)) + '%'
        text = str(round(perc, self.decimals))
        if '.' not in text:
            return text + '.' + '0' * self.decimals
        return  text + '0' * (self.decimals - len(text.split('.')[1])) + '%'

    def get_bar_coords(self):
        '''returns x0, y0, x1, y1 for active bar based on self.current_value'''
        x0, x1 = self.bd, self.width * self.current_value / self.iterations + self.bd
        y0, y1 = self.bd, self.height + self.bd
        return x0, y0, x1, y1

    def reset(self, iterations=None, current_value=None):
        '''reset iterations and/or current value'''
        if iterations != None:
            self.iterations = iterations
        if current_value != None:
            self.current_value = current_value
        else:
            self.current_value = 0
        self.canvas.coords(self.bar_id, *self.get_bar_coords())
        self.label.config(text=self.get_percentage_text())

    def increment(self, inc=1):
        '''called everytime an iteration is completed'''
        self.current_value = max(0, min(self.current_value + inc, self.iterations))
        self.canvas.coords(self.bar_id, *self.get_bar_coords())
        self.label.config(text=self.get_percentage_text())


