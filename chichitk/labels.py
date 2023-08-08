from tkinter import Label, Frame

import time
import numpy as np

from .entry_boxes import CheckEntry
from .buttons import IconButton
from .icons import icons


class EditLabel(Frame):
    ''' Label that changes to an CheckEntry box when user double clicks to
        allow text to be edited
        
        Uses CheckEntry so that text can be checked as it is entered and
        certain characters can be forbidden
    '''
    def __init__(self, master:Frame, text:str, bg:str='#ffffff', fg:str='#000000',
                 hover_bg:str='#cccccc', error_color='#ff0000', callback=None,
                 allowed_chars=None, max_len=None, check_function=None,
                 editable=True, justify='left', focus_out_bind=True,
                 hover_enter_function=None, hover_leave_function=None,
                 entry_on_function=None, entry_off_function=None,
                 font_name='Segoe UI', font_size=10, width=0):
        '''entry box to check text as it is entered
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param text: str - text displayed on label
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
            :param hover_bg: str (hex code) - background color when cursor is hovering
            :param error_color: str (hex code) - background color when there is an error
            :param callback: function (str) - called when label is edited by user
            :param allowed_chars: str or list of str - characters the can be entered
            :param max_len: int - maximum number of characters in box
            :param check_function: function (str) -> bool - called as text is entered
                                                          - if False, changes to error color
            :param hover_enter_function: function () - called when cursor enters label
            :param hover_leave_function: function () - called when cursor leaves label
            :param entry_on_function: function () - called with self.to_entry
            :param entry_off_function: function () - called with self.to_label
            :param width: int - width of Entry box
        '''
        self.text = text
        self.bg = bg
        self.hover_bg = hover_bg
        self.error_color = error_color
        self.callback = callback
        self.editable = editable
        self.dragging = False
        self.check_function = check_function
        self.hover_enter_function = hover_enter_function
        self.hover_leave_function = hover_leave_function
        self.entry_on_function = entry_on_function
        self.entry_off_function = entry_off_function
        self.last_callback = time.time() # to avoid double callbacks

        Frame.__init__(self, master, bg=bg)
        
        self.label = Label(self, text=self.text, bg=bg, fg=fg, font=(font_name, font_size))
        self.label.pack(fill='both')
        self.Entry = CheckEntry(self, default=self.text, allowed_chars=allowed_chars,
                                max_len=max_len, check_function=check_function,
                                font_name=font_name, font_size=font_size,
                                justify=justify, bg=bg, fg=fg,
                                error_color=error_color, width=width)
        self.label.bind("<Enter>", self.hover_enter)
        self.label.bind("<Leave>", self.hover_leave)
        self.label.bind('<Double-Button-1>', self.to_entry)
        self.label.bind("<ButtonRelease-1>", self.button_release)
        self.Entry.bind("<Return>", self.to_label)
        self.Entry.bind("<Tab>", self.to_label)
        if focus_out_bind:
            self.Entry.bind("<FocusOut>", self.to_label)

    def set_active(self):
        self.editable = True

    def set_inactive(self):
        self.editable = False
        self.to_label(callback=False)

    def set_text(self, text, callback=False):
        self.Entry.pack_forget()
        self.label.focus_set() # to take focus away from Entry so that keyboard strokes are no longer read by Entry
        self.label.pack(fill='both')
        self.text = text
        self.label.config(text=self.text)
        self.Entry.activate(text=text, select=False, focus=False) # only to set text in entry box
        if callback and self.callback:
            self.callback(text)

    def set_bg(self, bg:str, hover_bg:str=None):
        '''updates background color and hover_bg, optionally'''
        self.bg = bg
        self.hover_bg = hover_bg if hover_bg is not None else self.hover_bg
        self.label.config(bg=self.bg)
        self.config(bg=self.bg)
        self.Entry.set_bg(self.bg)

    def hover_enter(self, event=None):
        if self.editable:
            self.label.config(bg=self.hover_bg)
            self.config(bg=self.hover_bg)
            if self.hover_enter_function:
                self.hover_enter_function()

    def hover_leave(self, event=None):
        if self.editable and not self.dragging:
            self.label.config(bg=self.bg)
            self.config(bg=self.bg)
            if self.hover_leave_function:
                self.hover_leave_function()

    def button_release(self, event=None):
        if self.dragging:
            self.hover_leave()
            self.dragging = False

    def to_entry(self, event=None):
        if self.editable:
            self.label.pack_forget()
            self.Entry.activate(text=self.text, select=True)
            self.Entry.pack(fill='both')
            if self.entry_on_function:
                self.entry_on_function()

    def to_label(self, event=None, callback=True):
        '''switching from entry box to label'''
        current_time = time.time()
        if current_time - self.last_callback > 0.05: # avoid double callback
            self.last_callback = current_time
            self.Entry.pack_forget()
            self.label.focus_set() # to take focus away from Entry so that keyboard strokes are no longer read by Entry
            self.label.pack(fill='both')
            if self.check_function is None or self.check_function(self.Entry.get()): # only if text in Entry is good
                if self.Entry.get() != self.text: # only callback if text has changed
                    self.text = self.Entry.get()
                    self.label.config(text=self.text)
                    if callback and self.callback:
                        self.callback(self.text)
            if self.entry_off_function:
                self.entry_off_function()

    def get(self) -> str:
        return self.text

class NumberEditLabel(EditLabel):
    ''' Extension of EditLabel that only handles numbers and allows the to
        adjust the number by dragging on top of the label.

        Clicking on the label will switch it to an entry box for the user to
        enter an exact value. Dragging across the label will increment its value
        like a slider. To allow both of these functionalities, switching to the
        entry box is actually done upon the mouse button release, if the mouse
        button was released right after it was clicked (duration is defined by
        the 'drag_threshold' argument). Clicks longer than this will be
        considered drags and will not switch to the entry box.

        The sensitivity of dragging depends on the 'reference_width' parameter,
        which is 2 by default. 'reference_width' refers to a fraction of the
        label width and is defined as the the drag distance required to go from
        the minimum value to the maximum value. Dragging is entirely relative
        and does not depend on the position where the drag begun or ended.

        NumberEditLabel can handle floats or integers, depending on the value of
        the 'step' argument. If step evenly divisible by 1 (not necessarily of
        type int), return values from .get() will be integers, otherwise return
        values will be floats.
        
        NumberEditLabel is an excellent compact solution when there is not room
        to display a scrollbar or slider for the user to adjust numeric values.
    '''
    allowed_chars = '0123456789'

    def __init__(self, master, callback=None, min_value=0, max_value=100,
                 step=1, default_value=None, reference_width=2.0, max_len=None,
                 drag_threshold=0.2, draggable=True, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param callback: function (int|float), called when value is changed
            :param min_value: int or float - minimum value
            :param max_value: int or float - maximum value
            :param step: int or float - number increment
            :param default_value: int or float - default value if different from min_value
            :param reference_width: float - fraction of label width
            :param max_len: int - maximum number of characters in entry box
            :param drag_threshold: float (seconds) - click duration to be considered a single click (not drag)
            :param draggable: bool - if True, label value can be changed by dragging (like a slider)
        '''
        self._step = step
        if self._step % 1 == 0: # integer
            self._decimals = 0
        else:
            self._decimals = len(str(self._step).split(".")[1])
        default_value = default_value if default_value is not None else min_value
        allowed_chars = self.allowed_chars + '.' * (self._decimals > 0)
        
        super().__init__(master, self._get_text(default_value),
                         callback=self._entry_update, allowed_chars=allowed_chars,
                         max_len=max_len, check_function=self._check_function, **kwargs)
        
        self._callback_function = callback
        self._min_value, self._max_value = min_value, max_value
        self._values = np.arange(self._min_value, self._max_value + self._step * 0.9, self._step)
        self._drag_threshold = drag_threshold
        self._reference_width = reference_width

        if draggable:
            self.label.config(cursor='sb_h_double_arrow')
            self.label.bind("<Button-1>", self._mouse_click)
            self.label.bind("<ButtonRelease-1>", self._mouse_release, add='+')
            self.label.bind("<B1-Motion>", self._mouse_drag)

    def _check_function(self, text:str) -> bool:
        '''
        called when text is edited in entry box - checks if text is good
        input text is guaranteed to contain only numbers and '.' if return_type
        is float
        '''
        if text == '':
            return False
        if text[0] == '.' or text[-1] == '.' or text.count('.') > 1: # improperly formatted number
            return False
        value = float(text)
        if value < self._min_value or value > self._max_value: # out of range
            return False
        return True
        
    def _entry_update(self, text:str):
        '''
        called when number is updated by user exiting entry box
        text is guaranteed to have passed self._check_function
        reformats text if necessary and calls callback function
        '''
        # to reformat if necessary
        self.text = self._get_text(self.get())
        self.label.config(text=self.text)
        if self._callback_function is not None:
            self._callback_function(self.get())

    def _mouse_click(self, event):
        '''
        called when mouse clicks on label
        store current position for dragging
        store time so that release can decide to go to entry box or not
        '''
        self.dragging = True
        self._click_value = self.get()
        self._click_position = event.x
        self._click_time = time.time()

    def _mouse_release(self, event=None):
        '''
        called when mouse releases click
        if a short enough time has passed since click, goes to entry box
        a short time would indicate that the user simply clicked and didn't drag
        '''
        if time.time() - self._click_time < self._drag_threshold:
            self.to_entry()

    def _mouse_drag(self, event):
        '''
        called when mouse drags on label
        changes value based on drag distance
        '''
        # compute percentage of reference width that drag has traversed
        p = (event.x - self._click_position) / (self.label.winfo_width() * self._reference_width)
        # compute increment based on traversal percentage
        increment = (self._max_value - self._min_value) * p
        # add increment to click value and round to nearest allowed value
        value = self._values[(np.absolute(self._values - (self._click_value + increment))).argmin()]

        self.text = self._get_text(value)
        self.label.config(text=self.text)
        if self._callback_function is not None:
            self._callback_function(self.get())

    def set_min_value(self, min_value:int, force_limits=True):
        '''sets minimum value - must be less than current maximum value
        if force_limits is True, changes value and max value if necessary'''
        if force_limits:
            self._max_value = max(self._max_value, min_value) # adjust max if necessary
            if min_value > self.get():
                self.set(min_value, force_limits=False)
        self._min_value = min_value
        self._values = np.arange(self._min_value, self._max_value + self._step * 0.9, self._step)

    def set_max_value(self, max_value:int, force_limits=True):
        '''sets maximum value - must be greater than current minimum value
        if force_limits is True, changes value and min value if necessary'''
        if force_limits:
            self._min_value = min(self._min_value, max_value) # adjust min if necessary
            if max_value < self.get():
                self.set(max_value, force_limits=False)
        self._max_value = max_value
        self._values = np.arange(self._min_value, self._max_value + self._step * 0.9, self._step)

    def get_min_value(self) -> int:
        '''returns current minimum value'''
        return self._min_value
    
    def get_max_value(self) -> int:
        '''returns current maximum value'''
        return self._max_value

    def _get_text(self, value:int) -> str:
        '''converts value to string based on step and return_type'''
        if self._decimals == 0: # integer
            return str(int(value))
        text = str(round(value, self._decimals))
        if '.' in text:
            dec = len(text.split(".")[1])
        else:
            text += '.'
            dec = 0
        return text + '0' * (self._decimals - dec)

    def set(self, value:int, force_limits=True):
        '''updates value
        if force_limits is True, changes min and max value if necessary
        '''
        if force_limits:
            self._min_value = min(self._min_value, value)
            self._max_value = max(self._max_value, value)
        super().set_text(self._get_text(value))

    def get(self) -> int:
        '''
        returns number current in NumberEditLabel as int or float depending
        on preset return_type
        text currently in label is guaranteed to be formatted correctly
        '''
        if self._decimals == 0: # integer
            return int(super().get())
        else:
            return float(super().get())

    def set_perc(self, perc:float):
        '''sets value based on percentage - float between 0 and 1'''
        self.set(self._min_value + (self._max_value - self._min_value) * perc)

    def get_perc(self) -> float:
        '''returns label value as a percentage - float between 0 and 1'''
        return (self.get() - self._min_value) / (self._max_value - self._min_value)

class TimeEditLabel(NumberEditLabel):
    ''' Extension of NumberEditLabel that displays time in the form
        (h):(m)m:ss.xxx instead of simple number.
        
        set() and get() methods deal in seconds.
        
        Input/output type can be int or float depending on step
        
        See NumberEditLabel for further implementation details.
    '''
    allowed_chars = '0123456789:'

    def _check_function(self, text:str) -> bool:
        '''
        called when text is edited in entry box - checks if text is good
        input text is guaranteed to contain only numbers and ':' and '.' if
        return_type is float
        '''
        if text == '':
            return False
        if text.count(':') > 2 or text[0] == ':' or text[-1] == ':':
            return False
        if text.count('.') > 1 or text[0] == '.' or text[-1] == '.':
            return False
        for t in text.split(':')[1:]: # minute, second components
            if len(t) < 2 or float(t) >= 60:
                return False
        for t in text.split(':')[:-1]: # hour, minute components
            if t == '' or '.' in t or len(t) > 2 or int(t) >= 60:
                return False
        value = self.__get_text_value(text)
        if value < self._min_value or value > self._max_value: # out of range
            return False
        return True
        
    def _get_text(self, sec:float) -> str:
        '''converts value to string based on self._decimals'''
        # compute hours, minutes, and seconds
        s = int(sec)
        if sec >= 3600: # at least one hour
            text = f'{s // 3600}:{(s % 3600) // 60:0>2}:{(s % 60) // 1:0>2}'
        else: # less than one hour
            text = f'{s // 60}:{(s % 60) // 1:0>2}'

        # compute partial seconds
        if self._decimals > 0:
           if sec % 1 == 0: # whole seconds - still add zeros
               text += '.' + '0' * self._decimals
           else:
               dec = str(round(sec % 1, self._decimals))[1:] # in form .xxx
               text += f'{dec:0>{self._decimals + 1}}'
        return text

    def __get_text_value(self, text:str) -> float:
        '''
            returns the value of text in form (h):(m)m:ss.xxx in seconds
            text passed is guaranteed to have passed self._check_function
        '''
        if text.count(':') == 2: # includes hours - in form hh:mm:ss.xxx
            hours, minutes, seconds = text.split(':')
        elif text.count(':') == 1: # includes minutes - in form mm:ss.xx
            hours = 0
            minutes, seconds = text.split(':')
        else: # only minutes - in form mm:ss.xxx
            hours, minutes = 0, 0
            seconds = text

        value = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        if self._decimals == 0: # integer
            return int(round(value, 0))
        else: # float
            return round(value, self._decimals)
        
    def set(self, seconds:float, force_limits=False):
        '''updates value - force_limits is only for consistency with NumberEditLabel'''
        self.set_text(self._get_text(seconds))

    def get(self) -> float:
        '''returns current value as int or float (seconds) depending on step'''
        return self.__get_text_value(EditLabel.get(self))

class RangeLabel(Frame):
    ''' Pair of NumberEditLabels that allow user to select a range
    '''
    def __init__(self, master, callback=None, bg='#ffffff', dropdown_bg=None,
                 sep_text='to', min_val=0, max_val=100, default_min=None,
                 default_max=None, step=1, min_range=0, label_fg='#888888',
                 label_font_size=10, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param callback: function (int, int) - called when ranges is changed
            :param bg: str (hex code) - background color
            :param set_text: str - text between the two NumberEditLabels
            :param min_val: int - minimum value
            :param max_val: int - maximum value
            :param default_min: int - default minimum value if different from min_val
            :param default_max: int - default maximum value if different from max_val
            :param step: int or float - slider increment
            :param min_range: int - minimum allowed distance between min and max
            :param label_fg: str (hex code) - color of sep_text
            :param label_font_size: int - font size of sep text
        '''
        super().__init__(master, bg=bg)
        self._min_range = min_range
        self._callback_function = callback
        default_min = default_min if default_min is not None else min_val
        default_max = default_max if default_max is not None else max_val
        max_len = len(str(max_val)) if step % 1 == 0 else None

        dropdown_bg = dropdown_bg if dropdown_bg is not None else bg
        self._MinLabel = NumberEditLabel(self, self._min_callback, bg=dropdown_bg,
                                          min_value=min_val,
                                          max_value=default_max - self._min_range,
                                          step=step, default_value=default_min,
                                          max_len=max_len, **kwargs)
        self._MaxLabel = NumberEditLabel(self, self._max_callback, bg=dropdown_bg,
                                          min_value=default_min + self._min_range,
                                          max_value=max_val, step=step,
                                          default_value=default_max,
                                          max_len=max_len, **kwargs)
        self._MinLabel.pack(side='left', fill='x', expand=True)
        Label(self, text=f' {sep_text} ', bg=bg, fg=label_fg,
              font=('Segoe UI', label_font_size)).pack(side='left')
        self._MaxLabel.pack(side='left', fill='x', expand=True)

    def set_min(self, new_min:int):
        '''updates current min value - does not change range limits'''
        self._MinLabel.set(new_min)
        self._MaxLabel.set_min_value(new_min + self._min_range)

    def set_max(self, new_max:int):
        '''updates current max value - does not change range limits'''
        self._MaxLabel.set(new_max)
        self._MinLabel.set_max_value(new_max - self._min_range)

    def set_min_limit(self, new_min_limit:int):
        '''updates min limit - does not change current values'''
        self._MinLabel.set_min_value(new_min_limit)

    def set_max_limit(self, new_max_limit:int):
        '''updates max limit - does not change current values'''
        self._MaxLabel.set_max_value(new_max_limit)

    def set_min_range(self, min_range:int):
        '''updates the minimum allowed distance between min and max values'''
        self._min_range = min_range
        self._MaxLabel.set_min_value(self._MinLabel.get() + self._min_range)
        self._MinLabel.set_max_value(self._MaxLabel.get() - self._min_range)

    def _min_callback(self, min_value:int):
        '''
        called when min label is changed
        updates minimum value of max label and calls callback function
        '''
        self._MaxLabel.set_min_value(min_value + self._min_range)
        if self._callback_function is not None:
            self._callback_function(*self.get())

    def _max_callback(self, max_value:int):
        '''
        called when max label is changed
        updates maximum value of min label and calls callback function
        '''
        self._MinLabel.set_max_value(max_value - self._min_range)
        if self._callback_function is not None:
            self._callback_function(*self.get())

    def get(self):
        '''
        Purpose:
            gets minimum and maximum value from EditLabels
        Pre-conditions:
            (none)
        Post-conditions:
            (none)
        Returns:
            :return int - minimum value
            :return int - maximum value
        '''
        return self._MinLabel.get(), self._MaxLabel.get()

class NumberIncrementLabel(Frame):
    ''' Widget that allows user to select a number by typing in CheckEntry
        or by clicking '+' and '-' buttons
        
        EditLabel is used to allow user to enter a number
        
        IconButton is used for '+' and '-' buttons
    '''
    def __init__(self, master, bg:str, fg:str, default_val:int, hover_bg='#cccccc',
                 min_val=None, max_val=None, min_val_function=None, max_val_function=None,
                 callback_function=None, font_name='Segoe UI', font_size=12,
                 max_len=None, width=4):
        '''
        
        Parameters
        ----------
            :param master: tk.Frame - widget in which to grid label
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
            :param default_val: int
            :param hover_bg: str (hex code) - background color when cursor hovers
            :param min_val: None or int - minimum value
            :param max_val: None or int - maximum value
            :param min_function: function () -> int or None - returns min value or None
            :param max_function: function () -> int or None - returns max value or None
            :param callback_function: function (int) - called when value is changed
            :param max_len: int or None - maximum number of characters in number
        '''
        self.value = default_val
        self.min_val, self.max_val = min_val, max_val
        self.min_function, self.max_function = min_val_function, max_val_function
        self.callback_function = callback_function
        Frame.__init__(self, master, bg=bg)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        minus_button = IconButton(self, icons['minus'],
                                  self.minus, selectable=False,
                                  bar_height=0, popup_label='-1', inactive_bg=bg,
                                  inactive_hover_fg=fg, inactive_fg=fg,
                                  inactive_hover_bg=hover_bg)
        plus_button = IconButton(self, icons['plus'],
                                 self.plus, selectable=False,
                                 bar_height=0, popup_label='+1', inactive_bg=bg,
                                 inactive_hover_fg=fg, inactive_fg=fg,
                                 inactive_hover_bg=hover_bg)
        minus_button.grid(row=0, column=0)
        plus_button.grid(row=0, column=2)

        self.Label = EditLabel(self, str(self.value), bg=bg, fg=fg, hover_bg=hover_bg,
                               callback=self.update_from_label, check_function=self.edit_check,
                               allowed_chars='0123456789', max_len=max_len,
                               font_name=font_name, font_size=font_size,
                               justify='center', width=width)
        self.Label.grid(row=0, column=1)

    def edit_check(self, value:str):
        '''returns True if value is acceptable, otherwise False'''
        if value == '':
            return False
        value = int(value)
        if self.min_val != None and value < self.min_val:
            return False
        if self.max_val != None and value > self.max_val:
            return False
        min_exists = self.min_function != None and self.min_function() != None
        if min_exists and value < self.min_function():
            return False
        max_exists = self.max_function != None and self.max_function() != None
        if max_exists and value > self.max_function():
            return False
        return True

    def update_from_label(self, value:str):
        '''called when value is changed with label- value will have already passed edit_check'''
        self.value = int(value)
        if self.callback_function:
            self.callback_function(self.value)

    def set_value(self, value:int, callback=False):
        '''called externally or when plus or minus buttons are clicked'''
        self.value = value
        self.Label.set_text(str(self.value))
        if callback and self.callback_function:
            self.callback_function(self.value)

    def minus(self):
        if self.edit_check(self.value - 1):
            self.set_value(self.value - 1, callback=True)

    def plus(self):
        if self.edit_check(self.value + 1):
            self.set_value(self.value + 1, callback=True)

    def get(self):
        return self.value
