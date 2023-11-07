from tkinter import Frame, Label

from PIL import Image, ImageTk
import numpy as np
import cv2, os

from .icons import icons
from .buttons import image_replace_colors

__all__ = ['Icon', 'CheckIcon', 'CheckLabel', 'IconCheckLabel']


class Icon(Label):
    ''' Displays icon from png file with custom background and foreground color
    
        png file MUST have black background with white icon
    '''
    def __init__(self, master:Frame, icon_path:str, bg:str='#000000', fg:str='#ffffff',
                 bg2=None, fg2=None, h:int=24, w:int=24, status=False):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param icon_path: str or np.array - path to .png file or image array
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
            :param bg2: str (hex code) - optional secondary background color
            :param fg2: str (hex code) - optional secondary foreground color
            :param h: int (pixels) - icon height
            :param w: int (pixels) - icon width
            :param status: bool - False is bg and True is bg2
        '''        
        super().__init__(master, bg=bg)

        bg2 = bg2 if bg2 is not None else bg
        fg2 = fg2 if fg2 is not None else fg

        img_ar = self.__get_img_array(icon_path)
        self.img0 = cv2.resize(image_replace_colors(img_ar, [('#ffffff', fg), ('#000000', bg)]), (w, h))
        self.img1 = cv2.resize(image_replace_colors(img_ar, [('#ffffff', fg2), ('#000000', bg2)]), (w, h))

        # TODO: can't get img1 colors to show up when calling set()

        self.set(status)

    def __get_img_array(self, icon_path):
        '''returns image path as numpy array
        :icon_path: str (filepath) or np.array
        '''
        if isinstance(icon_path, str): # path to image
            assert len(icon_path) > 4, f'Icon Error: Invalid path: {icon_path}'
            assert icon_path[-4:] == '.png', f'Icon Error: icon_path is not a .png file: {icon_path}'
            assert os.path.exists(icon_path), f'Icon Error: Path to .png file does not exist: {icon_path}'
            return cv2.imread(icon_path)
        elif isinstance(icon_path, np.ndarray): # 3d numpy array
            return icon_path
        else:
            raise TypeError(f'Invalid icon input to Icon: {icon_path}')
        
    def set(self, status:bool):
        '''sets background color'''
        if status: # bg2
            image = ImageTk.PhotoImage(image=Image.fromarray(self.img1), master=self)
        else:
            image = ImageTk.PhotoImage(image=Image.fromarray(self.img0), master=self)
        self.config(image=image)
        self.image = image

class ToggleIcon(Frame):
    ''' Displays one of two icons depending on status
    
        Status can be set and retrieved with .set() and .get() methods

        Status 0 (False) is the first icon and status 1 (True) is second icon

        Do not use directly - only used for inheritance by CheckIcon and CheckLabel
    '''
    def __init__(self, master:Frame, path1:str, path2:str,
                 inactive_bg:str='#000000', active_bg:str=None,
                 inactive_fg:str='#888888', active_fg:str=None,
                 h:int=24, w:int=24, selected=False):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param Icon0: Icon - first icon (status 0 or False)
            :param Icon1: Icon - second icon (status 1 or True)
            :param status: bool - initial status
            :param bg: str (hex code) - background color
        '''
        super().__init__(master, bg=inactive_bg)
        self.__status = selected

        active_bg = active_bg if active_bg is not None else inactive_bg
        active_fg = active_fg if active_fg is not None else inactive_fg
        self.__icon0 = Icon(self, path1, bg=inactive_bg, bg2=active_bg, fg=inactive_fg, h=h, w=w)
        self.__icon1 = Icon(self, path2, bg=inactive_bg, bg2=active_bg, fg=active_fg, h=h, w=w)

        self.set(self.__status)

    def bindall(self, *args, **kwargs):
        '''binds to all sub widgets'''
        self.bind(*args, **kwargs)
        self.__icon0.bind(*args, **kwargs)
        self.__icon1.bind(*args, **kwargs)

    def set(self, status:bool):
        '''sets checked status - True for checked, False for unchecked'''
        self.__status = status
        if status: # set to checked (icon1)
            self.__icon0.pack_forget()
            self.__icon1.pack(fill='both')
        else: # set to unchecked (icon0)
            self.__icon1.pack_forget()
            self.__icon0.pack(fill='both')

    def set_bg(self, status:bool):
        '''sets main (False) or alternate (True) background'''
        self.__icon0.set(status)
        self.__icon1.set(status)

    def get(self) -> bool:
        '''returns current checked status'''
        return self.__status

class CheckIcon(ToggleIcon):
    ''' Displays checked or unchecked icon
    
        Checked status can be set and retrieved with .set() and .get() methods
    '''
    def __init__(self, master:Frame, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param inactive_bg: str (hex code) - background color when unchecked
            :param active_bg: str (hex code) or None - check background color (if different from inactive_bg)
            :param inactive_fg: str (hex code) - foreground color when unchecked
            :param active_fg: str (hex code) - foreground color when checked (if different from inactive_fg)
            :param h: int (pixels) - icon height
            :param w: int (pixels) - icon width
            :param selected: bool - initial selection status
        '''
        super().__init__(master, icons['box'], icons['checkbox'], **kwargs)

class CheckLabel(ToggleIcon):
    ''' Displays checkmark or blank for unchecked

        Sames as CheckIcon but without the box
    
        Checked status can be set and retrieved with .set() and .get() methods
    '''
    def __init__(self, master:Frame, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param inactive_bg: str (hex code) - background color when unchecked
            :param active_bg: str (hex code) or None - check background color (if different from inactive_bg)
            :param inactive_fg: str (hex code) - foreground color when unchecked
            :param active_fg: str (hex code) - foreground color when checked (if different from inactive_fg)
            :param h: int (pixels) - icon height
            :param w: int (pixels) - icon width
            :param selected: bool - initial selection status
        '''
        super().__init__(master, np.zeros((24, 24, 3)).astype(np.uint8), icons['check'], **kwargs)

class IconCheckLabel(Frame):
    ''' Listing for ToolFrame dropdown menu. Has CheckIcon (left), custom icon,
        then label (right)
        
        Background color changes when the cursor hovers
        
        User clicks to select/deselect. Selection status is indicated by the
        CheckIcon (left)
    '''
    def __init__(self, master:Frame, label:str, icon_path:str, callback=None,
                 inactive_bg:str='#000000', active_bg:str=None, fg:str='#dddddd',
                 active_fg:str='#ffffff', icon_h:int=24, icon_w:int=24, icon_padx=0,
                 font_name='Segoe UI', font_size=10, right_pad=0, selected=False):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param label: str - label title (text displayed to user)
            :param icon_path: path to png file or numpy array
            :param callback: function(status:bool) - called when label is clicked by user
            :param inactive_bg: str (hex code) - background color when unchecked
            :param active_bg: str (hex code) or None - check background color (if different from inactive_bg)
            :param fg: str (hex code) - foreground color
            :param icon_h: int - icon height
            :param icon_w: int - icon width
            :param selected: bool - initial selection status
            :param font_name: str - label font name
            :param font_size: int - label font size
            :param right_pad: int - number of extra spaces after label for x padding
            :param selected: bool - initial selection status
        '''
        super().__init__(master, bg=inactive_bg)
        self.__callback = callback
        self.__text = label
        self.__hovering = False

        active_bg if active_bg is not None else inactive_bg
        self.__bg_colors = [inactive_bg, active_bg]
        self.__fg_colors = [fg, active_fg]

        self.Check = CheckLabel(self, inactive_bg=inactive_bg, active_bg=active_bg,
                                inactive_fg=fg, active_fg=active_fg, h=icon_h, w=icon_w,
                                selected=selected)
        self.Check.pack(side='left', padx=icon_padx)

        self.Icon = Icon(self, icon_path, bg=inactive_bg, fg=fg,
                         bg2='#00ff00', fg2=active_fg, h=icon_h, w=icon_w, status=True) # status is False for not hovering
        self.Icon.pack(side='left', padx=icon_padx)

        self.Label = Label(self, text=self.__text + ' ' * right_pad, bg=inactive_bg,
                           fg=fg, font=(font_name, font_size))
        self.Label.pack(side='left')

        # Event Bindings
        self.bind('<Enter>', self.__hover_enter)
        self.bind('<Leave>', self.__hover_leave)
        self.bind('<Button-1>', self.__click)
        self.Icon.bind('<Button-1>', self.__click)
        self.Label.bind('<Button-1>', self.__click)
        self.Check.bindall('<Button-1>', self.__click)

    def bindall(self, *args, **kwargs):
        '''binds to all sub widgets'''
        self.bind(*args, **kwargs)
        self.Label.bind(*args, **kwargs)
        self.Icon.bind(*args, **kwargs)
        self.Check.bindall(*args, **kwargs)

    def __hover_enter(self, event=None):
        '''called when cursor hovers on popup'''
        self.__hovering = True
        self.__set_bg(True)

    def __hover_leave(self, event=None):
        '''called when cursor leaves popup'''
        self.__hovering = False
        self.__set_bg(False)

    def __set_bg(self, hovering:bool):
        '''sets background color based on hover status'''
        self.Check.set_bg(hovering)
        self.Icon.set(hovering)
        self.Label.config(bg=self.__bg_colors[hovering], fg=self.__fg_colors[hovering])
        self.config(bg=self.__bg_colors[hovering])

    def __click(self, event=None):
        '''cursor clicks to toggle selection status'''
        self.set(not self.get())
        if self.__callback is not None:
            self.__callback(self.get())

    def set(self, status:bool):
        '''sets selection status'''
        self.Check.set(status)

    def get(self) -> bool:
        '''returns current selection status'''
        return self.Check.get()
    
    def get_label(self) -> str:
        '''returns label text'''
        return self.__text

    def is_hovering(self) -> bool:
        '''returns True if cursor is hovering, otherwise False'''
        return self.__hovering
