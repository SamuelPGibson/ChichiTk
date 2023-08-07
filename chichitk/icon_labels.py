from tkinter import Frame, Label

from PIL import Image, ImageTk
import numpy as np
import cv2, os

from .icons import icons
from .buttons import image_replace_colors


class Icon(Label):
    ''' Displays icon from png file with custom background and foreground color
    
        png file MUST have black background with white icon
    '''
    def __init__(self, master:Frame, icon_path:str, bg:str='#000000', fg:str='#ffffff',
                 h:int=24, w:int=24):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param icon_path: str or np.array - path to .png file or image array
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
            :param h: int (pixels) - icon height
            :param w: int (pixels) - icon width
        '''        
        super().__init__(master, bg=bg)

        if isinstance(icon_path, str): # path to image
            assert len(icon_path) > 4, f'Icon Error: Invalid path: {icon_path}'
            assert icon_path[-4:] == '.png', f'Icon Error: icon_path is not a .png file: {icon_path}'
            assert os.path.exists(icon_path), f'Icon Error: Path to .png file does not exist: {icon_path}'
            img = cv2.imread(icon_path)
        elif isinstance(icon_path, np.ndarray): # 3d numpy array
            img = icon_path
        else:
            raise TypeError(f'Invalid icon input to IconButton: {icon_path}')

        img = image_replace_colors(img, [('#ffffff', fg), ('#000000', bg)])
        image = ImageTk.PhotoImage(image=Image.fromarray(cv2.resize(img, (w, h))), master=self)
        self.config(image=image)
        self.image = image

class CheckIcon(Frame):
    ''' Displays checked or unchecked icon
    
        Checked status can be set and retrieved with .set() and .get() methods
    '''
    def __init__(self, master:Frame, inactive_bg:str='#000000',
                 active_bg:str=None, inactive_fg:str='#888888',
                 active_fg:str='#ffffff', h:int=24, w:int=24, selected=False):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param inactive_bg: str (hex code) - background color when unchecked
            :param active_bg: str (hex code) or None - check background color (if different from inactive_bg)
            :param inactive_fg: str (hex code) - foreground color when unchecked
            :param active_fg: str (hex code) - foreground color when checked
            :param h: int (pixels) - icon height
            :param w: int (pixels) - icon width
            :param selected: bool - initial selection status
        '''
        super().__init__(master, bg=inactive_bg)
        self.__status = selected

        active_bg = active_bg if active_bg is not None else inactive_bg
        self.icon0 = Icon(self, icons['box'], bg=inactive_bg, fg=inactive_fg, h=h, w=w)
        self.icon1 = Icon(self, icons['checkbox'], bg=active_bg, fg=active_fg, h=h, w=w)

        self.set(self.__status)

    def set(self, status:bool):
        '''sets checked status - True for checked, False for unchecked'''
        self.__status = status
        if status: # set to checked (icon1)
            self.icon0.pack_forget()
            self.icon1.pack(fill='both')
        else: # set to unchecked (icon0)
            self.icon1.pack_forget()
            self.icon0.pack(fill='both')

    def get(self) -> bool:
        '''returns current checked status'''
        return self.__status
