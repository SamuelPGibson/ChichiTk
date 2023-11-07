from tkinter import Toplevel, Widget

from .icon_labels import IconCheckLabel


class ToolFrame(Toplevel):
    ''' Popup to display list of selectable items
    
        Should be connected to a Button to appear when button is clicked
    '''
    def __init__(self, master:Widget, parameters:list, callback=None,
                 bg:str='#000000', active_bg:str='#444444',
                 fg:str='999999', active_fg:str='#ffffff',
                 label_padx=1, label_pady=2, right_pad=2):
        '''
        Parameters
        ----------
            :param master: Widget - parent widget (should be Button)
            :param parameters: list[dict] - each dict has keys: ['label', 'icon']
            :param callback: function(index:int, status:bool) - called when a label is clicked
            :param right_pad: int - number of extra spaces after each label for x padding
        '''
        super().__init__(master, bg=bg)
        self.__callback = callback
        self.__visible = False # True when the popup window is visible

        # make window invisible, on the top, and strip all window decorations/features
        # change alpha to make window visible
        self.attributes('-alpha', 0, '-topmost', True)
        self.overrideredirect(1)

        # add labels
        self.__labels: list[IconCheckLabel] = []
        for i, d in enumerate(parameters):
            selected = d['selected'] if 'selected' in d.keys() else False
            label = IconCheckLabel(self, d['label'], d['icon'],
                                   callback=lambda s, x=i: self.__click_callback(x, s),
                                   inactive_bg=bg, active_bg=active_bg,
                                   fg=fg, active_fg=active_fg, right_pad=right_pad,
                                   selected=selected, icon_padx=0)
            label.pack(side='top', fill='x', padx=label_padx, pady=label_pady)
            self.__labels.append(label)

    def bindall(self, *args, **kwargs):
        '''binds to all sub widgets'''
        self.bind(*args, **kwargs)
        for label in self.__labels:
            label.bindall(*args, **kwargs)

    def __click_callback(self, index:int, status:bool):
        '''called when a label is clicked by user'''
        if self.__callback is not None:
            self.__callback(index, status)

    def show(self, event=None):
        '''called when parent button is clicked
        compute coordinates based on master (button) and set alpha to visible
        '''
        # check parent position (button that calls tool_tip popup)
        widget_width = self.master.winfo_width()
        widget_height = self.master.winfo_height()
        widget_x = self.master.winfo_rootx()
        widget_y = self.master.winfo_rooty()

        # compute popup geometry - may need to use self.frame
        w = self.winfo_width()
        h = self.winfo_height()
        x = widget_x # align to left edge of parent
        y = widget_y + widget_height # directly below widget

        # check root coordinates (main app window)
        root_width = self.master.winfo_toplevel().winfo_width()
        root_height = self.master.winfo_toplevel().winfo_height()
        root_x = self.master.winfo_toplevel().winfo_rootx() # x position of app on computer screen
        root_y = self.master.winfo_toplevel().winfo_rooty() # y position of app on computer screen

        # adjust so that popup is entirely within the root window
        if x + w > root_x + root_width: # enforce right edge
            x = root_x + root_width - w
        if y + h > root_y + root_height: # enforce bottom edge
            y = root_y + root_height - h
        x = max(root_x, x) # enforce left edge
        y = max(root_y, y) # enforce top edge

        # ensure tool_tip is not on top of widget - this makes a button unclickable!
        # this can only happen if tool_tip was moved up by bottom enforcement, so move it to above widget
        if y < widget_y + widget_height:
            y = widget_y - h # position tool_tip above widget

        self.geometry(f'{w}x{h}+{x}+{y}') # apply geometry
        self.attributes('-alpha', 1) # make window visible
        self.__visible = True

    def hide(self, event=None):
        '''should be called when cursor leaves popup window and parent button
        makes popup invisible
        '''
        self.attributes('-alpha', 0)
        self.__visible = False

    def select_all(self):
        '''selects all labels'''
        for label in self.__labels:
            label.set(True)
    
    def deselect_all(self):
        '''deselects all labels'''
        for label in self.__labels:
            label.set(False)

    def set(self, d:dict):
        '''sets selection status of labels
        :param d: dict - label(str):status(bool) for each item
        '''
        for label, value in d.items():
            for l in self.__labels:
                if label == l.get_label():
                    l.set(value)
                    break

    def get(self) -> dict:
        '''returns dictionary with label(str):status(bool) for each item'''
        return {d.get_label():d.get() for d in self.__labels}

    def is_visible(self) -> bool:
        '''returns True if window is visible, otherwise False'''
        return self.__visible

    def contains_point(self, x:int, y:int) -> bool:
        '''returns True if the given (x, y) point is in this Toplevel window, otherwise False'''
        x0 = self.winfo_rootx()
        y0 = self.winfo_rooty()
        x1 = x0 + self.winfo_width()
        y1 = y0 + self.winfo_height()
        # only y0 is >= so that popup does not disappear when moving from button to popup
        return x > x0 and x < x1 and y >= y0 and y < y1
