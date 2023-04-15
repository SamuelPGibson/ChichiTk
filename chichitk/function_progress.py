import os
from tkinter import Frame, Label

from .progress_bar import ProgressBar
from .buttons import IconButton


class FunctionProgress(Frame):
    ''' Widget to call a specific function and display the progress of that
        function's execution
        
        Uses IconButton to allow user to start the function
        
        Indictes if function has already been executed

        When function is being executed, it should call self.Progress.increment()
        with each iteration to increment progress bar
    '''
    def __init__(self, master, command, label, bg, loading_text='Loading...',
                 height=25, indicator_pady=0, font_name='Segoe UI',
                 font_size=10, text_font_size=12, inactive_bg:str='#ffffff',
                 loaded_bg:str='#00ff00', text_side='bottom', active_color='#00ff00',
                 text_color='#cccccc', inactive_color=None):
        '''
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param command: function () - called when button is clicked
                                        - function should increment progress bar
            :param label: str - label for IconButton - to call command
            :param bg: str (hex code) - widget background color
            :param loading_text: str - text displayed while command is running
            :param height: int - height of progress bar
            :param indicator_pady: int - pady for indicator square
            :param inactive_bg: str (hex code) - color of indicator when incomplete
            :param loaded_bg: str (hex code) - color of indicator when complete
            :param text_side: Literal['bottom', 'top', 'right', 'left'] - for progress bar
            :param active_color: str (hex code) - color of active part of progress bar
            :param text_color: str (hex code) - color of text in progress bar
            :param inactive_color: str (hex code) or None - inactive part of progress bar
        '''
        Frame.__init__(self, master, bg=bg)
        self.inactive_bg, self.loaded_bg = inactive_bg, loaded_bg
        inactive_color = inactive_color if inactive_color else bg
        self.complete = False

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")
        icon_path = os.path.join(image_path, "file_upload.png")

        self.main_frame = Frame(self, bg=bg)
        self.main_frame.pack(side='top', fill='both', expand=True)
        button = IconButton(self.main_frame, icon_path, command, label=label,
                            selectable=False, inactive_bg=bg, bar_height=2)
        button.pack(side='left', fill='both', expand=True)
        self.indicator = Label(self.main_frame, text=' ' * 3, bg=self.inactive_bg,
                               font=(font_name, font_size))
        self.indicator.pack(side='right', fill='y', pady=indicator_pady)

        self.Progress = ProgressBar(self, 100, bg, active_color=active_color,
                                    text_color=text_color, inactive_color=inactive_color,
                                    text=loading_text, width=200, height=height,
                                    center=False, text_font_size=text_font_size,
                                    val_font_size=font_size, text_side=text_side)

    def to_progress_bar(self, iterations:int):
        '''displayes progress bar with the specified number of iterations'''
        self.main_frame.pack_forget()
        self.Progress.pack(side='top', fill='both', expand=True)
        self.Progress.reset(iterations=iterations)

    def to_complete(self):
        '''removes progress bar and indicates that function is complete'''
        self.complete = True
        self.Progress.pack_forget()
        self.main_frame.pack(side='top', fill='both', expand=True)
        self.indicator.config(bg=self.loaded_bg)

    def to_incomplete(self):
        '''removes progress bar and indicates that function is incomplete'''
        self.complete = False
        self.Progress.pack_forget()
        self.main_frame.pack(side='top', fill='both', expand=True)
        self.indicator.config(bg=self.inactive_bg)

    def is_complete(self) -> bool:
        '''returns True if function is complete, otherwise False'''
        return self.complete

