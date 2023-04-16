from tkinter import Tk, Frame, Label

from chichitk import Player


class Stopwatch(Frame):
    ''' Stopwatch that utilizes chichitk Player to control start/stop
    '''
    def __init__(self, master, seconds=120, seconds_degree=0, step_seconds=5,
                 show_hours=False, **kwargs):
        '''
        Parameters
        ----------
            :param seconds: int - number of seconds on stopwatch
            :param seconds_degree: int - order of magnitude for second divisions
                                       - 0 is whole seconds, 3 is miliseconds
            :param step_seconds: int - seconds to skip forward and back with buttons
            :param show_hours: bool - if True, displays time in form hh:mm:ss...
        '''
        assert seconds_degree in range(4), f'seconds_degree is out of range: {seconds_degree}'
        self.total_seconds = seconds
        self.seconds_degree = seconds_degree
        self.show_hours = show_hours
        super().__init__(master, **kwargs)

        # Time Label
        self.__time_label = Label(self, text='', font=('Segoe UI bold', 30))
        self.__time_label.pack(side='top', pady=20)

        self.__Player = Player(self, self.__update_time, 1 / 10 ** self.seconds_degree,
                               bg='#222222', slider_type='single',
                               frame_num=self.total_seconds * 10**self.seconds_degree + 1,
                               frame_rate=10**self.seconds_degree,
                               step_increment=step_seconds * 10**self.seconds_degree,
                               start_callback=self.__start_callback,
                               stop_callback=self.__stop_callback,
                               end_callback=self.__stop_callback)
        self.__Player.pack(side='bottom', fill='x', padx=5, pady=5)

        self.__update_time(0)

    def __start_callback(self, step=None):
        '''called when stopwatch is started'''
        return
        self.configure(border_color='#00ff00')

    def __stop_callback(self):
        '''called when stopwatch is stopped'''
        return
        self.configure(border_color='#000000')

    def __update_time(self, time:int):
        '''updates label based on time'''
        f = 10 ** self.seconds_degree
        second = (time % (60 * f)) // f
        if self.show_hours:
            hour = time // (3600 * f)
            minute = (time % (3600 * f)) // (60 * f)
            text = f'{hour:0>2}:{minute:0>2}:{second:0>2}'
        else:
            minute = time // (60 * f)
            text = f'{minute}:{second:0>2}'
        if self.seconds_degree > 0: # partial seconds
            text += f'.{time % f:0>{self.seconds_degree}}'
        self.__time_label.configure(text=text)


app = Tk()  # create CTk window like you do with the Tk window
app.title('Stopwatch')
app.geometry("700x480")

W = Stopwatch(app, seconds_degree=2, show_hours=True)
W.place(relx=0.5, rely=0.5, anchor='center')

app.mainloop()

