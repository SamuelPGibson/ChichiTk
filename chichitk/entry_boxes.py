from tkinter import Entry, StringVar


class CheckEntry(Entry):
    ''' Extension of tk.Entry to check text as it is entered and only allow
        certain characters to be entered
    '''
    def __init__(self, master, default='', allowed_chars=None, max_len=None,
                 check_function=None, exit_function=None, justify='left',
                 bg:str='#ffffff', fg:str='#000000', disabled_bg=None,
                 disabled_fg=None, error_color='#ff0000', width=0,
                 font_name='Segoe UI', font_size=10, editable=True,
                 hide_char=None, select_first=False, focus_first=False, **kwargs):
        '''entry box to check text as it is entered
        
        Parameters
        ----------
            :param master: tk.Frame
            :param default: str - text automatically inserted into entry box
            :param allowed_chars: str or list of str - characters the can be entered
            :param max_len: int - maximum number of characters in box
            :param check_function: function (str) -> bool - text that fails check_function will trigger error_color
            :param exit_function: function (str) - optionally called when focus leaves
            :param justify: Literal['left', 'right', 'center'] - text position
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
            :param disabled_bg: str (hex code) - optionally different from bg
            :param disabled_fg: str (hex code) - optionally different from fg
            :param error_colors: str (hex code) - background color when there is an error
            :param width: int - default width of text box
            :param editable: bool - if False, entry box will be disabled (uninteractable)
            :param hide_char: str or None - character to display in entry box instead of text
                                          - example: '*' for password entry
            :param select_first: bool - if True, will select text upon initiation
            :param focus_first: bool - if True will focus CheckEntry upon initiation
        '''
        self.allowed_chars = allowed_chars
        self.max_len = max_len
        self.__check_function = check_function
        self.__exit_function = exit_function
        self.bg = bg
        self.error_color = error_color
        self.just_started = True
        disabled_bg = disabled_bg if disabled_bg else bg
        disabled_fg = disabled_fg if disabled_fg else fg

        self.sv = StringVar()
        self.sv.trace("w", lambda name, index, mode: self.entry_callback())
        Entry.__init__(self, master, width=width, font=(font_name, font_size),
                       textvariable=self.sv, fg=fg, bg=bg, insertbackground=fg,
                       disabledbackground=disabled_bg, disabledforeground=disabled_fg,
                       justify=justify, highlightthickness=0, borderwidth=0,
                       state='normal' if editable else 'disabled', show=hide_char,
                       **kwargs)
        if self.__exit_function is not None:
            for tag in ['<Return>', '<Tab>', '<FocusOut>']:
                self.bind(tag, self.exit)
        self.activate(text=default, select=select_first, focus=focus_first)

    def activate(self, text=None, select=True, focus=True):
        '''takes focus, replaces current text with text, and selects all text'''
        if text != None:
            self.delete(0, 'end')
            self.insert('end', text)
        if focus:
            self.focus_set()
        if select:
            self.select_range(0, 'end')

    def entry_callback(self):
        '''called whenever text in Entry is modified'''
        if self.just_started: # so that callback will not be called upon initialization
            self.just_started = False
            return None
        text = self.sv.get()
        self.config(bg=self.bg)
        if text == '':
            if self.__check_function is not None: # this is only here because of the misuse of CheckEntry as a search bar
                self.__check_function(text)
            return None
        if (self.allowed_chars is not None and not min([c in self.allowed_chars for c in text])) or (self.max_len and len(text) > self.max_len):
            cursor_index = self.index('insert')
            # remove character that was just entered
            self.delete(str(cursor_index - 1), str(cursor_index))
            text = super().get() # update text to current text in entry box
        if self.__check_function is not None and not self.__check_function(text):
            self.config(bg=self.error_color)

    def set_allowed_chars(self, allowed_chars:str):
        '''updates allowed characters in entry box
        :param allowed_chars: str | list[str] | None
        '''
        self.allowed_chars = allowed_chars

    def set_bg(self, bg:str):
        '''updates background color'''
        self.bg = bg
        self.config(bg=self.bg)

    def get(self):
        '''returns text currently in CheckEntry'''
        return self.sv.get()
    
    def clear(self):
        '''
        Purpose:
            removes all text from entry box
        Pre-conditions:
            (none)
        Post-conditions:
            removes all text from entry box
        Returns:
            (none)
        '''
        self.activate(text='', select=False, focus=False)

    def exit(self, event=None):
        '''calls exit function and destroys widget'''
        if self.__exit_function is not None:
            self.__exit_function(self.get())
        self.destroy()

class ColorEntry(CheckEntry):
    ''' Special version of CheckEntry that allows user to enter a hex code.
        As such, the text must begin with '#', must be 7 characters long, and
        can only contain the characters '0123456789abcdef'
    
        Includes popup that lets user select a color for a color gradient
    '''
    def __init__(self, master, default='#ffffff', callback=None, exit_function=None,
                 justify='left', bg:str='#ffffff', fg:str='#000000',
                 disabled_bg=None, disabled_fg=None, error_color='#ff0000',
                 width=0,  font_name='Segoe UI', font_size=10, editable=True,
                 hide_char=None, select_first=False, focus_first=False, **kwargs):
        '''CheckEntry box to only accept hex codes
        callback function will only be called with valid hex codes
        
        Parameters
        ----------
            :param master: tk.Frame
            :param default: str - text automatically inserted into entry box
            :param callback: function (str) - called when new color is set
            :param exit_function: function (str) - optionally called when focus leaves
            :param justify: Literal['left', 'right', 'center'] - text position
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
            :param disabled_bg: str (hex code) - optionally different from bg
            :param disabled_fg: str (hex code) - optionally different from fg
            :param error_colors: str (hex code) - background color when there is an error
            :param width: int - default width of text box
            :param editable: bool - if False, entry box will be disabled (uninteractable)
            :param hide_char: str or None - character to display in entry box instead of text
                                          - example: '*' for password entry
            :param select_first: bool - if True, will select text upon initiation
            :param focus_first: bool - if True will focus CheckEntry upon initiation
        '''
        self.__callback = callback
        CheckEntry.__init__(self, master, default=default,
                            allowed_chars='#0123456789abcdef', max_len=7,
                            check_function=self.color_check_function, exit_function=exit_function,
                            justify=justify, bg=bg, fg=fg, disabled_bg=disabled_bg,
                            disabled_fg=disabled_fg, error_color=error_color,
                            width=width, font_name=font_name, font_size=font_size,
                            editable=editable, hide_char=hide_char,
                            select_first=select_first, focus_first=focus_first,
                            **kwargs)
        
    def color_check_function(self, text:str):
        '''
        Purpose:
            check function for color entry box
            only calls __update_function if color if formatted correctly
        Pre-conditions:
            :param text: str - text for color entry box
        Post-conditions:
            (none)
        Returns:
            :return: bool - True if color text is formatted properly, otherwise False
        '''
        if len(text) == 7 and text[0] == '#' and text.count('#') == 1:
            self.__callback(text)
            return True
        return False

