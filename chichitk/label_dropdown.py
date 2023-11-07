from tkinter import Widget, Event

from .buttons import IconButton
from .tool_frame import ToolFrame
from .icons import icons


class LabelDropdown(IconButton):
    ''' Combines IconButton and ToolFrame to show dropdown menu with
        selectable labels when button is clicked
    '''
    def __init__(self, master:Widget, parameters:list, callback=None, icon=None,
                 popup_label=None, bg:str='#000000', inactive_fg:str='#888888',
                 hover_fg:str='#ffffff', label_bg:str=None, label_active_bg:str=None,
                 label_fg:str=None, label_active_fg:str=None):
        '''
        Parameters
        ----------
            :param master: tk.Widget - parent widget (for button)
            :param parameters: list[dict] - each dict has keys: ['label', 'icon']
            :param callback: function(index:int, status:bool) - called when a label is clicked
            :param icon: str (path to png), np.array or None (for default menu icon)
            :param popup_label: str - displayed when cursor hovers on button
        '''
        # Configure label colors
        label_bg = label_bg if label_bg is not None else bg
        label_active_bg = label_active_bg if label_active_bg is not None else label_bg
        label_fg = label_fg if label_fg is not None else inactive_fg
        label_active_fg = label_active_fg if label_active_fg is not None else hover_fg

        icon = icon if icon is not None else icons['menu']
        super().__init__(master, icon, self.__button_click, bar_height=0,
                         selectable=False, inactive_bg=bg, inactive_fg=inactive_fg,
                         inactive_hover_fg=hover_fg, popup_label=popup_label)
        
        self.__ToolFrame = ToolFrame(self, parameters, callback, bg=label_bg,
                                     active_bg=label_active_bg, fg=label_fg,
                                     active_fg=label_active_fg)
        
        self.bind('<Leave>', self.__button_leave, add='+')
        self.__ToolFrame.bindall('<Leave>', self.__popup_leave, add='+')

    # Event Callbacks
    def __button_leave(self, event:Event):
        '''called when cursor leaves button'''
        self.after(200, lambda: self.__leave(event))
    
    def __popup_leave(self, event:Event):
        '''called when cursor leaves button'''
        self.after(200, lambda: self.__leave(event))

    def __leave(self, event:Event):
        '''called a few miliseconds after the cursor leaves the button or popup'''
        if not self.is_hovering() and not self.__ToolFrame.contains_point(event.x_root, event.y_root):
            self.__ToolFrame.hide()

    def __button_click(self, event=None):
        '''user clicks on menu button to display popup'''
        self.__ToolFrame.show()

    # Pass to ToolFrame
    def select_all(self):
        '''selects all labels'''
        self.__ToolFrame.select_all()
    
    def deselect_all(self):
        '''deselects all labels'''
        self.__ToolFrame.deselect_all()

    def set(self, d:dict):
        '''sets selection status of labels
        :param d: dict - label(str):status(bool) for each item
        '''
        self.__ToolFrame.set(d)

    def get(self) -> dict:
        '''returns dictionary with label(str):status(bool) for each item'''
        return self.__ToolFrame.get()
