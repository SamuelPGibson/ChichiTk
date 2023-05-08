from tkinter import Frame

from .timer import Timer
from .buttons import PlayerButtons
from .sliders import TimeSlider, PlotScrollBar, DoubleScrollBar

# TODO: make TimeSlider attribute customizable through Player

class Player(Frame):
    ''' Player executes a callback function with precise timing.

        Combines PlayerButtons and a scrollbar to give user control of playback
    
        Includes a scrollbar for user to control playing.
        
        An example use case could be playing frames from a video
    '''
    def __init__(self, master:Frame, callback, delay:float, bg:str='#000000',
                 slider_type:str='single', frame_num=1000, frame_rate=29.97,
                 step_increment:int=150, end_callback=None, start_callback=None,
                 stop_callback=None, skip_callback=None, buttons_on_top=False,
                 buttons_padx_weight=6, simple_slider_width=None,
                 limit_running_callbacks=False):
        ''' Only keeps track of the current frame using Timer

        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param callback: function (step) - called with each iteration
            :param delay: float - seconds between each iteration
                                - would be based on frame rate for video player
            :param bg: str - background color
            :param slider_type: str - options: ['simple', 'single', 'double']
            :param frame_num: int - number of frames
            :param step_increment: float - number of steps to skip forward or
                                         - back when step buttons are clicked
            :param end_callback: function () - called when final step is reached
                                             - not called if looping is on
            :param start_callback: function (current_step) - called when timer is started
            :param stop_callback: function () - called when timer is stopped
            :param skip_callback: function (current_step) - called when step is incremented
            :param buttons_on_top: bool - True to put buttons on top, or False for bottom
            :param buttons_padx_weight: int - weight of padding for PlayerButtons
            :param limit_running_callbacks: bool - if True, does not call callback function immediately when slider is moved while running
                                                 - to avoid calling the callback function in multiple different threads
        '''
        self.__callback = callback
        self.__end_callback = end_callback
        self.__frame_rate = frame_rate
        self.__step_increment = step_increment
        self.__slider_type = slider_type
        self.__limit_running_callbacks = limit_running_callbacks
        super().__init__(master, bg=bg)

        # compute sides for widget packing
        sides = ['bottom', 'top']
        slider_side = sides[not buttons_on_top]
        buttons_side = sides[buttons_on_top]

        self.__Timer = Timer(delay, self.__timer_update, end_callback=self.__end,
                             start_callback=start_callback, stop_callback=stop_callback,
                             skip_callback=skip_callback, min_step=0, max_step=frame_num)

        if slider_type == 'simple':
            self.__Slider = TimeSlider(self, self.__slider_update, bg=bg,
                                       frame_num=frame_num, active_line_color='#ffffff',
                                       active_line_hover_color='#13ce12', slider_color='#ffffff',
                                       hide_slider=True, steps_per_sec=1/delay,
                                       slider_type='circle', width=simple_slider_width)
        elif slider_type == 'single':
            self.__Slider = PlotScrollBar(self, self.__slider_update, None, frame_num,
                                          min_frame=0, start_frame=0, frame_rate=self.__frame_rate,
                                          height=60, bg=bg)
        elif slider_type == 'double':
            self.__Slider = DoubleScrollBar(self, self.__slider_update, None, frame_num,
                                            min_frame=0, start_frame=0, frame_rate=self.__frame_rate,
                                            bg=bg)
        self.__Slider.pack(side=slider_side, fill='x')

        self.__Buttons = PlayerButtons(self, bg, self.__Timer.start, self.__Timer.stop,
                                       self.step_forward, self.step_back,
                                       self.__Timer.to_end, self.__Timer.reset,
                                       padx_weight=buttons_padx_weight)
        self.__Buttons.pack(side=buttons_side, fill='x')

    def start(self):
        '''starts player - called externally - not from buttons'''
        self.__Timer.start()
        self.__Buttons.to_stop()

    def stop(self):
        '''stops player - called externally - not from buttons'''
        self.__Timer.stop()
        self.__Buttons.to_play()

    def step_forward(self):
        '''same as clicking 'skip forward' button in PlayerButtons'''
        callback = not self.__limit_running_callbacks or not self.__Timer.is_running()
        self.__Timer.increment(self.__step_increment, callback=callback)

    def step_back(self):
        '''same as clicking 'step back' button in PlayerButtons'''
        callback = not self.__limit_running_callbacks or not self.__Timer.is_running()
        self.__Timer.increment(-self.__step_increment, callback=callback)

    def set_frame(self, frame:int):
        '''updates the current frame and calls callback function'''
        self.__Timer.set(frame)
        self.__Slider.set_frame(frame)
        self.__callback(frame)

    def set_frame_num(self, frame_num:int):
        '''updates number of steps - pushes to timer and scrollbar'''
        self.__Timer.set_max_step(frame_num)
        self.__Slider.set_frame_num(frame_num, self.__frame_rate)

    def set_frame_rate(self, frame_rate:float):
        '''updates frame rate - number of frames stays sthe same'''
        self.__frame_rate = frame_rate
        self.__Timer.set_delay(1 / self.__frame_rate)
        self.__Slider.set_frame_num(self.__Timer.get_max_step(), self.__frame_rate)

    def set_delay(self, delay:float):
        '''updates delay of timer
        intended for when Player is not being used to play video frames'''
        self.__Timer.set_delay(delay)
        if self.__slider_type == 'simple':
            self.__Slider.set_steps_per_sec(1 / delay)

    def set_increment(self, inc:int):
        '''sets number of steps to skip when 'skip forward' and 'skip back'
        buttons are clicked'''
        self.__step_increment = inc

    def get_step(self) -> int:
        '''returns the current step'''
        return self.__Timer.get_step()

    def get_delay(self) -> float:
        '''returns delay between callbacks (seconds)'''
        return self.__Timer.get_delay()
    
    def get_max_step(self) -> int:
        '''returns the maximum number of steps'''
        return self.__Timer.get_max_step()

    def get_frame_rate(self) -> float:
        '''returns frame rate'''
        return self.__frame_rate

    def __timer_update(self, step:int):
        '''called by timer when playing'''
        self.__Slider.set_frame(step)
        self.__callback(step)

    def __slider_update(self, step:int):
        '''called when slider is moved by user
        it does not matter whether timer is running or not'''
        self.__Timer.set(step)
        if not self.__limit_running_callbacks or not self.__Timer.is_running():
            self.__callback(step)

    def __end(self):
        '''called when player reaches the end (max step)'''
        if self.__Buttons.is_looped():
            self.__Timer.reset()
            self.__Timer.start()
        else: # no loop - actually stopping
            self.__Buttons.to_play()
            if self.__end_callback is not None:
                self.__end_callback()
    
