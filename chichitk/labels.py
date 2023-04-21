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
        self.Entry.pack_forget()
        self.label.focus_set() # to take focus away from Entry so that keyboard strokes are no longer read by Entry
        self.label.pack(fill='both')
        if self.check_function == None or self.check_function(self.Entry.get()): # only if text in Entry is good
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

    def __init__(self, master, callback=None, min_value=0, max_value=100,
                 step=1, default_value=None, reference_width=2.0, max_len=None,
                 drag_threshold=0.2, **kwargs):
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
        '''
        if step % 1 == 0: # integer
            self.__decimals = 0
        else:
            self.__decimals = len(str(self.__step).split(".")[1])
        default_value = default_value if default_value is not None else min_value
        allowed_chars = '0123456789' + '.' * (self.__decimals > 0)
        
        super().__init__(master, self.__get_text(default_value),
                         callback=self.__entry_update, allowed_chars=allowed_chars,
                         max_len=max_len, check_function=self.__check_function, **kwargs)
        
        self.__callback_function = callback
        self.__min_value, self.__max_value = min_value, max_value
        self.__step = step
        self.__values = np.arange(self.__min_value, self.__max_value + self.__step * 0.9, self.__step)
        self.__drag_threshold = drag_threshold
        self.__reference_width = reference_width

        self.label.config(cursor='sb_h_double_arrow')

        # Bindings
        self.label.bind("<Button-1>", self.__mouse_click)
        self.label.bind("<ButtonRelease-1>", self.__mouse_release, add='+')
        self.label.bind("<B1-Motion>", self.__mouse_drag)

    def __check_function(self, text:str) -> bool:
        '''
        called when text is edited in entry box - checks if text is good
        input text is guaranteed to contain only numbers and '.' if return_type
        is float
        '''
        if text == '':
            return False
        if text[0] == '.' or text.count('.') >= 1: # improperly formatted number
            return False
        value = float(text)
        if value < self.__min_value or value > self.__max_value: # out of range
            return False
        return True
        
    def __entry_update(self, text:str):
        '''
        called when number is updated by user exiting entry box
        text is guaranteed to have passed self.__check_function
        reformats text if necessary and calls callback function
        '''
        # to reformat if necessary
        self.label.config(text=self.__get_text(self.get()))
        if self.__callback_function is not None:
            self.__callback_function(self.get())

    def __mouse_click(self, event):
        '''
        called when mouse clicks on label
        store current position for dragging
        store time so that release can decide to go to entry box or not
        '''
        self.dragging = True
        self.__click_value = self.get()
        self.__click_position = event.x
        self.__click_time = time.time()

    def __mouse_release(self, event=None):
        '''
        called when mouse releases click
        if a short enough time has passed since click, goes to entry box
        a short time would indicate that the user simply clicked and didn't drag
        '''
        if time.time() - self.__click_time < self.__drag_threshold:
            self.to_entry()

    def __mouse_drag(self, event):
        '''
        called when mouse drags on label
        changes value based on drag distance
        '''
        # compute percentage of reference width that drag has traversed
        p = (event.x - self.__click_position) / (self.label.winfo_width() * self.__reference_width)
        # compute increment based on traversal percentage
        increment = (self.__max_value - self.__min_value) * p
        # add increment to click value and round to nearest allowed value
        value = self.__values[(np.absolute(self.__values - (self.__click_value + increment))).argmin()]

        self.text = self.__get_text(value)
        self.label.config(text=self.text)
        if self.__callback_function is not None:
            self.__callback_function(self.get())

    def set_min_value(self, min_value:int):
        '''sets minimum value - must be less than current maximum value'''
        assert min_value <= self.__max_value, f'Tried to set minimum value, {min_value}, that is greater than current maximum value, {self.__max_value}'
        self.__min_value = min_value
        self.__values = np.arange(self.__min_value, self.__max_value + self.__step * 0.9, self.__step)

    def set_max_value(self, max_value:int):
        '''sets maximum value - must be greater than current minimum value'''
        assert max_value >= self.__min_value, f'Tried to set maximum value, {max_value}, that is greater than current minimum value, {self.__min_value}'
        self.__max_value = max_value
        self.__values = np.arange(self.__min_value, self.__max_value + self.__step * 0.9, self.__step)

    def __get_text(self, value:int) -> str:
        '''converts value to string based on step and return_type'''
        if self.__decimals == 0: # integer
            return str(int(value))
        text = str(round(value, self.__decimals))
        if '.' in text:
            dec = len(text.split(".")[1])
        else:
            text += '.'
            dec = 0
        return text + '0' * (self.__decimals - dec)

    def set(self, value:int):
        '''updates value'''
        super().set_text(self.__get_text(value))

    def get(self) -> int:
        '''
        returns number current in NumberEditLabel as int or float depending
        on preset return_type
        text currently in label is guaranteed to be formatted correctly
        '''
        if self.__decimals == 0: # integer
            return int(super().get())
        else:
            return float(super().get())

class RangeLabel(Frame):
    ''' Pair of NumberEditLabels that allow user to select a range
    '''
    def __init__(self, master, callback=None, bg='#ffffff', sep_text='to',
                 min_val=0, max_val=100, default_min=None, default_max=None,
                 step=1, label_fg='#888888', label_font_size=10, **kwargs):
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
            :param label_fg: str (hex code) - color of sep_text
            :param label_font_size: int - font size of sep text
        '''
        super().__init__(master, bg=bg)
        self.__callback_function = callback
        default_min = default_min if default_min is not None else min_val
        default_max = default_max if default_max is not None else max_val

        self.__MinLabel = NumberEditLabel(self, self.__min_callback, bg=bg,
                                          min_value=min_val, max_value=default_max,
                                          step=step, default_value=default_min,
                                          max_len=len(str(max_val)), **kwargs)
        self.__MaxLabel = NumberEditLabel(self, self.__max_callback, bg=bg,
                                          min_value=default_min, max_value=max_val,
                                          step=step, default_value=default_max,
                                          max_len=len(str(max_val)), **kwargs)
        self.__MinLabel.pack(side='left', fill='x', expand=True)
        Label(self, text=f' {sep_text} ', bg=bg, fg=label_fg,
              font=('Segoe UI', label_font_size)).pack(side='left')
        self.__MaxLabel.pack(side='left', fill='x', expand=True)

    def set_min(self, new_min:int):
        '''updates current min value - does not change range limits'''
        self.__MinLabel.set(new_min)
        self.__MaxLabel.set_min_value(new_min)

    def set_max(self, new_max:int):
        '''updates current max value - does not change range limits'''
        self.__MaxLabel.set(new_max)
        self.__MinLabel.set_max_value(new_max)

    def set_min_limit(self, new_min_limit:int):
        '''updates min limit - does not change current values'''
        self.__MinLabel.set_min_value(new_min_limit)

    def set_max_limit(self, new_max_limit:int):
        '''updates max limit - does not change current values'''
        self.__MaxLabel.set_max_value(new_max_limit)

    def __min_callback(self, min_value:int):
        '''
        called when min label is changed
        updates minimum value of max label and calls callback function
        '''
        self.__MaxLabel.set_min_value(min_value)
        if self.__callback_function is not None:
            self.__callback_function(*self.get())

    def __max_callback(self, max_value:int):
        '''
        called when max label is changed
        updates maximum value of min label and calls callback function
        '''
        self.__MinLabel.set_max_value(max_value)
        if self.__callback_function is not None:
            self.__callback_function(*self.get())

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
        return self.__MinLabel.get(), self.__MaxLabel.get()

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
