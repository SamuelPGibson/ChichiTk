import os
from tkinter import Label, Frame

from .entry_boxes import CheckEntry
from .buttons import IconButton


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

    def get(self):
        return self.text

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

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")

        minus_button = IconButton(self, os.path.join(image_path, "minus.png"),
                                  self.minus, selectable=False,
                                  bar_height=0, popup_label='-1', inactive_bg=bg,
                                  inactive_hover_fg=fg, inactive_fg=fg,
                                  inactive_hover_bg=hover_bg)
        plus_button = IconButton(self, os.path.join(image_path, "plus.png"),
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


