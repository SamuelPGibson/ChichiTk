from tkinter import Menu


class TempMenu:
    ''' Special Menu object for NoteItems

        TempMenu was created for an application in which thousands of object
        instances were using tk.Menu popups bound to right clicked. This caused
        a problem where too many menus were being allocated. TempMenu solves
        this by only creating the tk.Menu when the popup is called and
        discarding it immediatly after.
        
        TempMenu will accept and store the same parameters of a tkinter menu
        but it will only create a tkinter menu when the popup is called.
        
        The functionality on the user side will remain unchanged.
    '''
    def __init__(self, master, bg:str, fg:str, active_bg:str,
                 font_name:str='Segoe UI', font_size:int=11):
        '''
        Purpose:
            custom version of tkinter Menu that does not create a tkinter Menu until popup is called
            destroys tkinter Menu after popup
        Pre-conditions:
            :param master: tk.Frame - parent widget - does not matter if self is a descendant of another TempMenu
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
            :param active_bg: str (hex code) - background color of labels when cursor is hovering
            :param font_name: str - font name such as "Segoe UI"
            :param font_size: int - font size of all labels in menu and nested menus
        Post-conditions:
            (none)
        Returns:
            :return:

        Details about self.__options:
            all commands and cascades (nested TempMenus) are stored in self.__options: list[dict]
            for commands, the dict contains keys: ['type', 'label', 'command'] where type is 'command'
            for cascades, the dict contains keys: ['type', 'label', 'menu'] where type is 'cascade'
        '''
        self.__master = master
        self.__bg = bg
        self.__fg = fg
        self.__active_bg = active_bg
        self.__font = (font_name, font_size)
        self.__options: list[dict] = [] # list of command and cascades

    def add_command(self, label:str, command):
        '''
        Purpose:
            adds a command to menu
        Pre-conditions:
            :param label: str - text displayed in menu dropdown
            :param command: 0 argument function - called when label is clicked
        Post-conditions:
            adds a command to menu
        Returns:
            (none)
        '''
        self.__options.append({'type':'command', 'label':label, 'command':command})

    def add_cascade(self, label:str, menu):
        '''
        Purpose:
            adds a nested menu
        Pre-conditions:
            :param label: str - text displayed in menu dropdown
            :param menu: TempMenu - another TempMenu to nest within this TempMenu
        Post-conditions:
            adds a nested menu to the menu
        Returns:
            (none)
        '''
        self.__options.append({'type':'cascade', 'label':label, 'menu':menu})

    def get_menu(self, parent_menu=None) -> Menu:
        '''
        Purpose:
            creates tkinter Menu with predefined commands and cascades
            should only be called from within tk_popup of this or another TempMenu
            self can be parent TempMenu or a descendant of another TempMenu
            parent_menu parameter will be None only when self is the parent TempMenu
        Pre-conditions:
            :param parent_menu: TempMenu or None - parent TempMenu in which to create tkinter Menu
        Post-conditions:
            (none)
        Returns:
            :return: tk.Menu - Menu containing predefined commands and cascades
        '''
        master = parent_menu if parent_menu != None else self.__master
        menu = Menu(master, tearoff=False, bg=self.__bg, fg=self.__fg, activebackground=self.__active_bg, font=self.__font)
        for option in self.__options:
            if option['type'] == 'command':
                menu.add_command(label=option['label'], command=option['command'])
            elif option['type'] == 'cascade':
                menu.add_cascade(label=option['label'], menu=option['menu'].get_menu(parent_menu=menu))
        return menu
    
    def tk_popup(self, x:int, y:int):
        '''
        Purpose:
            creates tkinter menu and calls popup
        Pre-conditions:
            :param x: int - x coordinate of popup position
            :param y: int - y coordinate of popup position
        Post-conditions:
            displays tkinter menu popup
        Returns:
            (none)
        '''
        # menu is stored only in local frame so it will be discarded by
        # python garbage collector after popup
        self.get_menu().tk_popup(x, y)

