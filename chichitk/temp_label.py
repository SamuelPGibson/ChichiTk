from tkinter import Frame, Label

from .timer import Timer


class TempLabel(Label):
    ''' Simple Tkinter Label that clears after a certain length of time
    '''
    def __init__(self, master:Frame, duration=5.0, default_text='', **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param duration: float (seconds) - time to wait before clearing
            :param default_text: str - text displayed when clearing
        '''
        self.__default_text = default_text
        super().__init__(master, text=self.__default_text, **kwargs)

        self.__delay = 0.1 # arbitrary time between steps
        self.__Timer = Timer(self.__delay, callback=lambda s: None,
                             end_callback=self.__to_default,
                             max_step=int(duration / self.__delay))
        
    def __to_default(self):
        '''called when timer reaches the end - reset label'''
        self.config(text=self.__default_text)

    def set_duration(self, duration:float):
        '''updates label clear duration (seconds)'''
        self.__Timer.set_max_step(int(duration / self.__delay))

    def set_text(self, text:str, **kwargs):
        '''
        Purpose
        -------
            Updates label text and any other parameters such as foregroud color
            Resets the timer
        '''
        self.config(text=text, **kwargs)
        self.__Timer.reset()
        self.__Timer.start() # in case label was on default (Timer not running)

