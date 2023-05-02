from tkinter import Toplevel, Label, Widget, Event


def add_line_breaks(text:str, max_line_len:int, split_char=' ', replace_char='\n'):
    '''splits text into multiple lines - only splits at split_char
    the only way a line can be longer than max_line_len
    is if a single word is longer than max_line_len
    
    :return: str - text with some split chars replaced with '\n'
    '''
    output_text = ''
    line_len = 0
    for i, char in enumerate(text):
        if char == split_char:
            next_split = text[i + 1:].find(split_char) # chars until next split
            if next_split == -1: # no more split chars
                next_split = len(text[i + 1:])
            if next_split + line_len + 1 > max_line_len: # split here
                output_text += replace_char
                line_len = 0
                continue
        output_text += char
        line_len += 1
    return output_text


class ToolTip(Toplevel):
    ''' Popup to display information when the cursor hovers on a widget
    
        Info can be displayed on multiple lines by setting chars_per_line
        
        Popup will be displayed directly above the parent widget by default
        but it will check where the edge of the root frame is and adjust its
        position so that it does not extend beyond the root frame
    '''
    def __init__(self, master, chars_per_line=50, fade_inc:float=0.07,
                 fade_ms:int=20, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param chars_per_line: int - maximum characters before line break
            :param fade_inc: float - amount to adjust fade on every frame
            :param fade_ms: int (milliseconds) - time to wait before next frame
        '''
        self.__chars_per_line = chars_per_line
        self.__fade_inc, self.__fade_ms = fade_inc, fade_ms
        super().__init__(master)
        #make window invisible, on the top, and strip all window decorations/features
        self.attributes('-alpha', 0, '-topmost', True)
        self.overrideredirect(1)
        #style and create label. you can override style with kwargs
        style = dict(bd=2, relief='raised', font='courier 10 bold', bg='#FFFF99', anchor='w')
        self.label = Label(self, **{**style, **kwargs})
        self.label.grid(row=0, column=0, sticky='w')
        #used to determine if an opposing fade is already in progress
        self.fout:bool = False
        
    def bind(self, target:Widget, text:str, **kwargs):
        #bind Enter(mouseOver) and Leave(mouseOut) events to the target of this tooltip
        target.bind('<Enter>', lambda e: self.fadein(0, text, e))
        target.bind('<Leave>', lambda e: self.fadeout(1 - self.__fade_inc, e))

    def fadein(self, alpha:float, text:str=None, event:Event=None):
        #if event and text then this call came from target
        #~ we can consider this a "fresh/new" call
        if event is not None and text is not None:
            if self.fout: # if we are in the middle of fading out jump to end of fade
                self.attributes('-alpha', 0)
                self.fout = False # indicate that we are fading in
            text = add_line_breaks(text, self.__chars_per_line, replace_char=' \n ') # to pad each line with space
            self.label.configure(text=f'{text:^{len(text)+2}}') # pad with a space on either side
            self.update() # update so the proceeding geometry will be correct

            # check widget position (widget that calls tool_tip popup such as button or label)
            widget_width = event.widget.winfo_width()
            widget_height = event.widget.winfo_height()
            widget_x = event.widget.winfo_rootx()
            widget_y = event.widget.winfo_rooty()

            # compute popup geometry
            w = self.label.winfo_width()
            h = self.label.winfo_height()
            x = widget_x + int((widget_width - w) / 2) # to center horizontally
            y = widget_y - h # directly above widget

            # check root coordinates
            root_width = event.widget.winfo_toplevel().winfo_width()
            root_height = event.widget.winfo_toplevel().winfo_height()
            root_x = event.widget.winfo_toplevel().winfo_rootx() # x position of app on computer screen
            root_y = event.widget.winfo_toplevel().winfo_rooty() # y position of app on computer screen

            # adjust so that popup is entirely within the root window
            if x + w > root_x + root_width: # enforce right edge
                x = root_x + root_width - w
            if y + h > root_y + root_height: # enforce bottom edge
                y = root_y + root_height - h
            x = max(root_x, x) # enforce left edge
            y = max(root_y, y) # enforce top edge

            # ensure tool_tip is not on top of widget - this makes a button unclickable!
            # this can only happen if tool_tip was moved down by top enforcement, so move it to below widget
            if y + h > widget_y:
                y = widget_y + widget_height # position tool_tip below widget

            #apply geometry
            self.geometry(f'{w}x{h}+{x}+{y}')
               
        #if we aren't fading out, fade in
        if not self.fout:
            self.attributes('-alpha', alpha)
        
            if alpha < 1:
                self.after(self.__fade_ms, lambda: self.fadein(min(alpha + self.__fade_inc, 1)))

    def fadeout(self, alpha:float, event:Event=None):
        #if event then this call came from target 
        #~ we can consider this a "fresh/new" call
        if event is not None:
            #indicate that we are fading out
            self.fout = True
        
        #if we aren't fading in, fade out        
        if self.fout:
            self.attributes('-alpha', alpha)
        
            if alpha > 0:
                self.after(self.__fade_ms, lambda: self.fadeout(max(alpha - self.__fade_inc, 0)))

    def set_text(self, text:str):
        '''sets popup text - to be called while popup is visible
        for example, when a button is clicked'''
        text = add_line_breaks(text, self.__chars_per_line, replace_char=' \n ') # to pad each line with space
        self.label.configure(text=f'{text:^{len(text)+2}}') # pad with a space on either side
        #update so the proceeding geometry will be correct
        self.update()
        w = self.label.winfo_width()
        h = self.label.winfo_height()
        #apply geometry - the position (x, y) is already set - only need to update height/width
        self.geometry(f'{w}x{h}')
