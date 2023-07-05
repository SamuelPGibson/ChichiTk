from tkinter import Frame, Label
from datetime import datetime

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
        self.__text_history: list[dict] = []
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
        self.__text_history.append({'text':text, 'time':datetime.now()})
        self.config(text=text, **kwargs)
        self.__Timer.reset()
        self.__Timer.start() # in case label was on default (Timer not running)

    def get_history(self) -> list:
        '''
        Purpose
        -------
            collects all text updates, with their corresponding timestamps
        
        Returns
        -------
            :return: list[dict] - each dict contains keys:
                text: str - text that was passed to set_text()
                time: datetime object - timestamp when set_text() was called
        '''
        return self.__text_history

