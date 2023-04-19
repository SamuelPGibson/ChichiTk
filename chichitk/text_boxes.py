from tkinter import Frame, Text


def consecutive_spaces(text:str, consec_char:str=' ', leading:str=True,
                       trailing:str=True):
    '''checks if consec_char occurs consecutively in text
    
    Parameters
    ----------
        :param text: str - must not contain newline characters - '\n'
        :param consec_char: str - single character to check for text
        :param leading: bool - if True, checks if first character is consec_char
        :param trailing: bool - if True, checks if last character is consec_char

    Returns:
        :return: list[tuple[int]] - indices where consecutive consec_char occurs (upper bound exclusive)
                                  - or None if there are no consecutive instances of consec_char
    '''
    indices = []
    start = 0
    end = None
    for i, char in enumerate(text):
        if char == consec_char: # start new sequence or extend current
            if start == None:
                start = i
            else:
                end = i
        elif start != None and end != None: # end last sequence
            indices.append((start, end + 1))
            start = None
            end = None
        elif start != None: # cancel last sequence - only one instance of consec_char
            if i == 1 and leading: # first character is consec_char
                indices.append((0, 1))
            start = None
    if trailing and start != None and end != None: # trailing white space
        indices.append((start, end + 1))
    if start != None:
        indices.append((start, start + 1))
    if len(indices) == 0:
        return False
    return indices


class TextBox(Frame):
    ''' Text widget that counts the lines just like a code editor and can
        call a callback function whenever the text is edited by the user
        
        TextBox can optionally display an error color when there are blank
        lines or consecutive spaces
    '''
    def __init__(self, master, callback=None, bg:str='#ffffff', fg:str='#000000',
                 cursor_color=None, disabled_bg=None, disabled_fg=None,
                 error_bg:str='#3c2525', error_highlight_bg:str='#ff0000',
                 error_highlight_fg:str='#000000', track_fg:str='#bbbbbb',
                 font_name:str='Consolas', font_size:int=15,  wrap='none',
                 focus_in_function=None, focus_out_function=None,
                 check_blank_lines:bool=True, check_consecutive_spaces:bool=True,
                 line_numbers_labels=True, width=None, height=None,
                 justify='left', inactive_justify='center'):
        '''Text box with number lines and callback when text box is edited
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param callback: function (str) - called whenever text box is modified
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - main text color
            :param cursor_color: str (hex code) - cursor color - if different from fg
            :param disabled_bg: str (hex code) - background color when disabled
            :param disabled_fg: str (hex code) - foreground color when disabled
            :param error_bg: str (hex code) - background color when there is an error
            :param error_highlight_bg: str (hex code) - highlight on text causing error
            :param error_highlight_fg: str (hex code) - color of text cauing error
            :param track_fg: str (hex code) - color of track text - line numbers
            :param font_name: str - font for text box and line numbers
            :param font_size: int - font size for text box and line numbers
            :param wrap: str Literal['none', 'char', 'word'] - wrap setting
            :param focus_in_function: function () - called when text box takes focus
            :param focus_out_function: function () - called when text box loses focus
            :param check_blank_lines: bool - if True, show error when there are blank lines
            :param check_consecutive_spaces: bool - if True, show error when there are consecutive spaces
            :param line_numbers_labels: bool - if True, show line numbers
        '''
        self.callback_function = callback
        self.bg, self.fg = bg, fg
        self.error_bg = error_bg
        self.error_highlight_bg = error_highlight_bg
        self.error_highlight_fg = error_highlight_fg
        self.disabled_bg = disabled_bg if disabled_bg else bg
        self.disabled_fg = disabled_fg if disabled_fg else fg
        self.justify, self.inactive_justify = justify, inactive_justify
        Frame.__init__(self, master, bg=bg)
        self.good_format = True # False if there are errors in the text box
        self.check_blank_lines = check_blank_lines
        self.check_consecutive_spaces = check_consecutive_spaces
        cursor_color = cursor_color if cursor_color else fg

        self.track = Text(self, width=4, height=height, font=(font_name, font_size),
                          bg=bg, fg=track_fg, wrap='none', bd=0,
                          yscrollcommand=lambda a, b: self.box.yview_moveto(a))
        if line_numbers_labels:
            self.track.pack(side='left', fill='y')
        self.track.insert('end', '  1')
        self.track.config(state='disabled')
        # undo must be False because Ctrl+z causes infinite loop (no idea why)
        self.box = Text(self, width=width, height=height, font=(font_name, font_size),
                        bg=bg, fg=fg, insertbackground=cursor_color, undo=False, wrap=wrap,
                        yscrollcommand=lambda a, b: self.track.yview_moveto(a), bd=0)
        self.box.pack(side='right', fill='both', expand=True)
        self.box.tag_add("justify", 1.0, "end")
        self.box.tag_configure('justify', justify=self.justify)
        self.box.bind("<<TextModified>>", self.callback)
        #self.box.bind("<Key>", self.callback)
        if focus_in_function:
            self.box.bind("<FocusIn>", focus_in_function)
        if focus_out_function:
            self.box.bind("<FocusOut>", focus_out_function)

        # create a proxy for the underlying widget
        self.box._orig = self.box._w + "_orig"
        self.box.tk.call("rename", self.box._w, self.box._orig)
        self.box.tk.createcommand(self.box._w, self._proxy)

    def _proxy(self, command, *args):
        '''facilitates callback - called whenever Text box is edited by user'''
        cmd = (self.box._orig, command) + args
        try:
            result = self.box.tk.call(cmd)
        except:
            # As far as I can tell, this error only occurs when pasting
            # pasting involves: 1. deleting selected text 2. pasting copied text
            # tk is trying to delete selected text when no text is selected
            # Pasting worked fine when there was text selected to "overwrite"
            # Because tk is trying to delete "nothing", this error an be skipped without effect
            # Hopefully this doesn't bite me in the ass down the road...
            # Many frustrating hours were spent trying to solve this... :/
            return None
        if command in ("insert", "delete", "replace"):
            self.box.event_generate("<<TextModified>>")
        return result

    def callback(self, event=None):
        '''called whenever text box is modified'''
        text = self.box.get('1.0', 'end-1c')
        y_pos = self.box.yview()[0]
        self.track.config(state='normal')
        self.track.delete(0.0, 'end')
        self.track.insert('end', '\n'.join([f'{x} ' for x in range(1, text.count('\n') + 2)]))
        self.track.config(state='disabled')
        self.track.tag_delete('right')
        self.track.tag_add("right", 1.0, "end")
        self.track.tag_configure("right", justify='right')

        # do basic error checking
        self.good_format = True
        self.box.tag_delete('empty_line')
        self.box.tag_delete('consecutive_space')
        if text != '' and (self.check_blank_lines or self.check_consecutive_spaces):
            for i, line in enumerate(text.split('\n')):
                if self.check_blank_lines and line == '':
                    self.good_format = False
                    self.box.tag_add('empty_line', f'{i + 1}.0', f'{i + 2}.0')
                    continue
                # check for two or more consecutive spaces
                if self.check_consecutive_spaces and consecutive_spaces(line, trailing=False) != False:
                    self.good_format = False
                    for tup in consecutive_spaces(line, trailing=False):
                        self.box.tag_add('consecutive_space',
                                         f'{i + 1}.{tup[0]}',
                                         f'{i + 1}.{tup[1]}')
            self.box.tag_config('empty_line', background=self.error_highlight_bg,
                                foreground=self.error_highlight_fg)
            self.box.tag_config('consecutive_space', background=self.error_highlight_bg,
                                foreground=self.error_highlight_fg)
            if self.good_format:
                self.box.config(bg=self.bg)
                self.track.config(bg=self.bg)
            else:
                self.box.config(bg=self.error_bg)
                self.track.config(bg=self.error_bg)

        self.box.yview_moveto(y_pos)
        self.track.yview_moveto(y_pos)
        if self.callback_function:
            self.callback_function(text)

    def get(self, strip=True) -> str:
        '''returns entire text in text box

        Parameters
        -----------
            :param strip: bool - if True, removes spaces and newline characters for beginning and end
        '''
        if strip:
            return self.box.get(0.0, 'end').strip()
        return self.box.get(0.0, 'end')

    def clear(self):
        '''clears all text from text box'''
        self.box.delete(0.0, 'end')

    def insert(self, text):
        '''inserts text at the end of text box'''
        self.box.insert('end', text)

    def clear_insert(self, text):
        '''clears all text from text box and adds text'''
        self.clear()
        self.insert(text)

    def set_active(self):
        '''
        Purpose:
            sets text box state to 'normal' so that it is interactable
        '''
        self.box.config(state='normal', bg=self.bg, fg=self.fg)
        self.box.tag_add("justify", 1.0, "end")
        self.box.tag_configure('justify', justify=self.justify)
        self.track.config(bg=self.bg)

    def set_inactive(self):
        '''
        Purpose:
            sets text box state to 'disabled' so that it is not interactable
        '''
        self.box.config(state='disabled', bg=self.disabled_bg, fg=self.disabled_fg)
        self.box.tag_add("justify", 1.0, "end")
        self.box.tag_configure('justify', justify=self.inactive_justify)
        self.track.config(bg=self.disabled_bg)

