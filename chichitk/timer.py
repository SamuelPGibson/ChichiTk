import time
from threading import Thread


class Timer:
    ''' Performs precisely timed callbacks
    
        The timer is given a set number of steps which could be frames in a
        video, seconds until an alarm, etc. The timer will count up, calling a
        callback function with each iteration, until the set number of steps is
        reached.

        The callback functions must accept a single integer argument, which is
        the current step.

        The timer works by storing the current time when it is started and
        computing the step of each iteration based on the time elasped since
        the timer started. It is not guaranteed that the callback function will
        be called with exactly sequential steps since step(s) will be skipped
        if the callback function takes longer than expected to execute.

        The number of steps, and the delay between steps can be changed at any
        time (even while the timer is running)
        
        The simplest usage is a stopwatch, where delay could be 1 for seconds or
        0.001 for miliseconds. The callback will be called to increment the time
    '''
    
    def __init__(self, delay:float, callback, end_callback=None,
                 start_callback=None, stop_callback=None, skip_callback=None,
                 min_step=0, max_step=None, reset_end_start=True,
                 track_execution_time=False):
        '''sets timer with number of steps and delay, both of which can be changed later
        
        Parameters
        ----------
            :param delay: float - time to elapse between steps
            :param callback: function (current_step) - called with each step
            :param end_callback: function () - called when final step is reached
            :param start_callback: function (current_step) - called when timer is started
            :param stop_callback: function () - called when timer is stopped
            :param skip_callback: function (current_step) - called when step is incremented
            :param min_step: int - lowest allowed step (default=0)
            :param max_step: int - number of steps in timer (default=None - unlimited)
            :param reset_end_start: bool - If True, resets timer when starting from the end
            :param track_execution_time: bool - only use when debugging (more computationally expensive)

        Note
        ----
            * Start, stop, skip, and end callbacks are always called regardless of the
                manner in which the event occurs
            * For example, if you call the Timer.start() method, the start
                callback will be called
            * However, if Timer.start() is called when timer is already running,
                the start callback will not be called
            * Timer.to_end() does not call the skip function since this stops the
                timer
        '''
        self.__delay = delay
        self.__callback = callback
        self.__end_callback, self.__skip_callback = end_callback, skip_callback
        self.__start_callback, self.__stop_callback = start_callback, stop_callback
        self.__min_step, self.__max_step = min_step, max_step
        self.__current_step = min_step
        self.__start_step = min_step # relevant while running
        self.__track_execution_time = track_execution_time
        self.__reset_end_start = reset_end_start
        self.__running = False

    def start(self):
        '''
        Purpose
        -------
            starts timer at current step
            if you need to start at a specific step, call set() first then start()

        Returns
        -------
            :return: bool - False if timer was already running, otherwise True
        '''
        if not self.__running: # cannot start timer if already started
            # if starting from the end, so go back to start
            if self.at_end() and self.__reset_end_start:
                self.__current_step = self.__min_step
            self.__running = True
            self.__start_time = time.time()
            self.__last_time = self.__start_time
            self.__start_step = self.__current_step
            Thread(target=self.__run).start()
            if self.__start_callback is not None:
                self.__start_callback(self.__current_step)
            return True
        return False

    def stop(self):
        '''
        Purpose
        -------
            stops timer immediatly - next callback will be halted
            
        Returns
        -------
            :return: bool - False if timer was already stopped, otherwise True
        '''
        if self.__running:
            self.__running = False
            if self.__stop_callback is not None:
                self.__stop_callback()
            return True
        return False

    def reset(self):
        '''resets step to min_step and calls callback function
        does not stop the timer'''
        self.increment(self.__min_step - self.__current_step, callback=True)

    def to_end(self):
        '''sets step to max_step, stops timer, and calls callback function'''
        assert self.__max_step is not None, 'Skipped timer to end when max_step is not defined'
        self.stop()
        if self.__end_callback is not None:
            self.__end_callback()
        self.__current_step = self.__max_step
        self.__callback(self.__current_step)

    def set(self, step:int):
        '''
        Purpose:
            sets timer to the current step.
            if timer is currently running, it will continue uninterrupted
            the next callback will reflect the updated step
        Pre-conditions:
            :param step: int - replaces current step
        '''
        assert isinstance(step, int), 'Step must be an integer'
        if step < self.__min_step or (self.__max_step is not None and step > self.__max_step):
            raise ValueError(f"Step is out of range: {step}.")
        self.__start_step += step - self.__current_step # for running computation
        self.__current_step = step
        if self.__skip_callback is not None:
            self.__skip_callback(self.__current_step)

    def increment(self, inc:int, callback=False):
        '''changes current step by the given increment (can be positive or negative)
        forces current step to stay between min_step and max_step
        only calls callback function if callback == True and timer is running
        '''
        inc = max(self.__min_step - self.__current_step, inc) # enforce upper limit
        if self.__max_step is not None: # enforce upper limit
            inc = min(self.__max_step - self.__current_step, inc)
        self.__current_step += inc
        self.__start_step += inc # so that running step is computed correctly
        if callback and not self.__running:
            self.__callback(self.__current_step)
        if self.__skip_callback is not None:
            self.__skip_callback(self.__current_step)

    def get_step(self) -> int:
        '''returns the current step'''
        return self.__current_step

    def set_delay(self, delay:float):
        '''
        Purpose:
            updates the delay between callbacks.
            if timer is currently running, the next callback will occur
            at the previously scheduled time, and callbacks after that will
            reflect the updated delay
        Pre-conditions:
            :param delay: float - new delay between callbacks
        '''
        self.__delay = delay

    def get_delay(self) -> float:
        '''returns delay between callbacks (seconds)'''
        return self.__delay

    def set_max_step(self, max_step:int):
        '''updates max step'''
        self.__max_step = max_step

    def get_max_step(self):
        '''returns max_step - must not call this is max_step is undefined'''
        assert self.__max_step is not None, 'Tried to get max_step when it is undefined'
        return self.__max_step
    
    def at_end(self):
        '''returns True if timer is at the end, otherwise False'''
        return self.__max_step is not None and self.__current_step >= self.__max_step
    
    def is_running(self):
        '''returns True if timer is running, otherwise False'''
        return self.__running

    def __run(self):
        '''private method to actually run timer
        private because it must always be called in a Thread
        '''
        while self.__running:
            # compute time to wait before next iteration - approx
            current_time = time.time()
            elapsed_time = current_time - self.__last_time # since last iteration
            sleep_time = max(0, self.__delay - elapsed_time)
            self.__last_time = current_time

            # compute step based on time since start
            step_inc = (self.__last_time - self.__start_time) / self.__delay
            self.__current_step = int(round(self.__start_step + step_inc, 0))

            # check if timer has reached the end
            if self.__max_step is not None and self.__current_step >= self.__max_step:
                self.stop()
                if self.__end_callback is not None:
                    self.__end_callback()
                break

            self.__callback(self.__current_step)

            if self.__track_execution_time:
                execution_time = time.time() - self.__last_time
                if execution_time > self.__delay:
                    print(f'Callback took {execution_time:.4f}s, which is longer than delay: {self.__delay:.4f}s')

            time.sleep(sleep_time) # wait before next iteration

