from tkinter import Menu, Frame, Label
from fractions import Fraction


class OptionMenu(Label):
    ''' Label that displays a tkinter Menu when clicked

        OptionMenu was created because tk.OptionMenu and ttk.OptionMenu are not
        aesthetically pleasing and they lack customizable features
    
        OptionMenu.set() must be called when an option is selected in order to
        update the label
    '''
    def __init__(self, master:Frame, menu:Menu, default='', bg:str='#ffffff',
                 fg='#000000', hover_bg:str='#aaaaaa',
                 font_name='Segoe UI', font_size=10, active=True):
        '''        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param menu: tk.Menu - displayed when label is clicked
            :param default: str - initial text displayed on label
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - text color
            :param hover_bg: str (hex code) - background color when cursor hovers
            :param active: bool - if False, cursor click will not do anything
        '''
        self.menu = menu
        self.text = default
        self.bg = bg
        self.hover_bg = hover_bg
        self.__active = active
        Label.__init__(self, master, text=self.text, font=(font_name, font_size), fg=fg, bg=bg)
        self.bind('<Enter>', self.__hover_enter)
        self.bind('<Leave>', self.__hover_leave)
        self.bind('<Button-1>', self.__popup)

    def set_active(self):
        '''sets state to active so that menu can be viewed and edited by user'''
        self.__active = True

    def set_inactive(self):
        '''sets state to inactive so that hover and click events don't do anything'''
        self.__active = False

    def __hover_enter(self, event=None):
        '''called when cursor enters label'''
        if self.__active:
            self.config(bg=self.hover_bg)

    def __hover_leave(self, event=None):
        '''called when cursor leaves label'''
        if self.__active:
            self.config(bg=self.bg)

    def __popup(self, event=None):
        '''called when cursor clicks on label'''
        if self.__active:
            self.menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())

    def set(self, text:str):
        '''called internally or when a dropdown option is clicked by user'''
        self.text = text
        self.config(text=self.text)

    def get_text(self) -> str:
        '''returns currently selected option'''
        return self.text

class BasicDropDown(OptionMenu):
    ''' Dropdown menu to allow user to selected from a list of options
    
        When an option is selected, calls callback function with the single
        str argument being the option that was selected
    '''
    def __init__(self, master, options:list, default:str, callback=None,
                 bg:str='#ffffff', fg:str='#000000', hover_bg:str='#aaaaaa',
                 active=True):
        '''dropdown menu containing list of str
        
        Parameters
        ----------
            :param master: tk.Frame - frame in which to put dropdown menu
            :param options: list of str - dropdown options available to user
            :param default: str - default selection - should be in options but not mandatory
            :param callback: function (str) - called when an option is selected
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
            :param hover_bg: str (hex code) - background color when cursor hovers
            :param active: bool - if True, dropdown menu is editable by user
        '''
        self._callback = callback
        menu = Menu(master, tearoff=False, bg=bg, fg=fg, activebackground=hover_bg)
        for op in options:
            menu.add_command(label=op, command=lambda x=op: self.update(x, callback=True))

        OptionMenu.__init__(self, master, menu, default=default, bg=bg, fg=fg,
                            hover_bg=hover_bg, active=active)

    def update(self, x:str, callback=False):
        '''called when a dropdown item is selected by user or called internally to set value'''
        self.set(x)
        if callback and self._callback:
            self._callback(self.get())

    def get(self):
        '''returns currently selected option'''
        return self.get_text()

class NumberDropDown(BasicDropDown):
    ''' Special version of BasicDropDown to deal with integers and floats
    
        .get() method returns an integer or float depending on 'return_type'
    '''
    def __init__(self, master, options:list, default:int, return_type='int',
                 **kwargs):
        '''dropdown for selecting number from options
        
        Parameters
        ----------
            :param master : tk.Frame - frame in which to place drowdown menu
            :param options : list[int | float] - dropdown options
            :param default : int - default selection, should be in options but not mandatory
            :param return_type : Literal['int', 'float'] - type to be returned by self.get
            **kwargs includes: ['bg', 'fg', 'hover_bg', 'active']
        '''
        BasicDropDown.__init__(self, master, [str(x) for x in options],
                               str(default), **kwargs)
        self.__return_type = return_type

    def update(self, x:str, callback=False):
        '''called when a dropdown item is selected by user or called internally'''
        self.set(str(x))
        if callback and self._callback:
            self._callback(self.get())
    
    def get(self):
        '''returns currently selected option'''
        if self.__return_type == 'float':
            return float(self.get_text())
        else:
            return int(self.get_text())

class TuningDropDown(OptionMenu):
    ''' Dropdown menu to select tuning or create a custom tuning
    
        Tuning can be retrieved with .get() and .get_labels() either as
        a list of note indices such as [19, 24, 29, 34, 38, 43]
        or a list of labels such as ['E', 'A', 'D', 'G', 'B', 'E']
    '''
    def __init__(self, master, default_tuning:list, callback=None,
                 bg:str='#ffffff', fg='#000000', hover_bg:str='#aaaaaa',
                 active=True):
        '''dropdown to select tuning - default must be in tuning keys'''
        self._callback = callback
        self.tunings = {'E Standard':[19, 24, 29, 34, 38, 43],
                        'E♭ Standard':[18, 23, 28, 33, 37, 42],
                        'D Standard':[17, 22, 27, 32, 36, 41],
                        'Drop D':[17, 24, 29, 34, 38, 43],
                        'Drop D♭':[16, 23, 28, 33, 37, 42],
                        'Drop C':[15, 22, 27, 32, 36, 41]}
        self.labels = {'E Standard':['E', 'A', 'D', 'G', 'B', 'E'],
                        'E♭ Standard':['D♯', 'G♯', 'C♯', 'F♯', 'A♯', 'D♯'],
                        'D Standard':['D', 'G', 'C', 'F', 'A', 'D'],
                        'Drop D':['D', 'A', 'D', 'G', 'B', 'E'],
                        'Drop D♭':['C♯', 'G♯', 'C♯', 'F♯', 'A♯', 'D♯'],
                        'Drop C':['C', 'G', 'C', 'F', 'A', 'D']}
        menu = Menu(master, tearoff=False, bg=bg, fg=fg, activebackground=hover_bg)
        for tuning in self.tunings.keys():
            menu.add_command(label=tuning, command=lambda x=tuning: self.__update(x))
        menu.add_command(label='Custom Tuning', command=self.set_custom_tuning)

        OptionMenu.__init__(self, master, menu, bg=bg, fg=fg,
                            hover_bg=hover_bg, active=active)
        self.set_tuning(default_tuning)

    def set_custom_tuning(self):
        '''open window to create custom tuning'''

    def __update(self, x:str):
        '''called when dropdown is selected by user'''
        self.set(x)
        if self._callback:
            self._callback(self.get())

    def set_tuning(self, tuning:list):
        '''sets tuning based on list of note indices
        intended to be called only when a new project is loaded
        
        Parameters
        ----------
            :param tuning: list[int] - note indices of each string, lowest first
        '''
        new_tuning = 'E Standard' # in case no match is found
        for text, inds in self.tunings.items():
            if tuning == inds:
                new_tuning = text
                break
        self.set(new_tuning)

    def get(self):
        '''returns tuning as list of note indices (ints) such as: [19, 23, 29, 34, 38, 43]'''
        return self.tunings[self.get_text()]

    def get_labels(self):
        '''returns tuning labels such as: ['E', 'A', 'D', 'G', 'B', 'E']'''
        return self.labels[self.get_text()]

class KeyDropDown(OptionMenu):
    ''' Dropdown menu to edit the key of a song
    
        Key is displayed to user in the common form 'A' or 'C#'
        but the .get() method returns the key in lilypond format such as
        'a' or 'cis' or 'bes'
    '''
    def __init__(self, master, default:str, callback=None, bg:str='#ffffff',
                 fg:str='#000000', hover_bg:str='#aaaaaa', active:bool=True):
        '''
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param default: str - default key in lilypond format
            :param bg: str - background color
            :param fg: str - foreground color
            :param hover_bg: str - background color when cursor is hovering
            :param active: bool - if True, dropdown is editable by user
        '''
        self._callback = callback
        sharp_sign_unicode, flat_sign_unicode, natural_sign_unicode = '\u266F', '\u266D', '\u266E'
        self.keys_dict = {'A':'a',
                          f'A{sharp_sign_unicode}':'ais',
                          f'A{flat_sign_unicode}':'aes',
                          'B':'b',
                          f'B{flat_sign_unicode}':'bes',
                          'C':'c',
                          f'C{sharp_sign_unicode}':'cis',
                          'D':'d',
                          f'D{sharp_sign_unicode}':'dis',
                          f'D{flat_sign_unicode}':'des',
                          'E':'e',
                          f'E{flat_sign_unicode}':'ees',
                          'F':'f',
                          f'F{sharp_sign_unicode}':'fis',
                          'G':'g',
                          f'G{flat_sign_unicode}':'ges',
                          f'G{sharp_sign_unicode}':'gis'}

        keys = list(self.keys_dict.keys())
        default_key = 'A'
        for key in keys:
            if self.keys_dict[key] == default:
                default_key = key
                break
        
        menu = Menu(master, tearoff=False, bg=bg, fg=fg, activebackground=hover_bg)
        for root_key in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            inds = [i for i in range(len(keys)) if root_key in keys[i]]
            sub_menu = Menu(menu, tearoff=False, bg=bg, fg=fg, activebackground=hover_bg)
            menu.add_cascade(label=root_key, menu=sub_menu)
            for i in inds:
                sub_menu.add_command(label=keys[i], command=lambda x=keys[i]: self.__update(x))

        OptionMenu.__init__(self, master, menu, default=default_key, bg=bg,
                            fg=fg, hover_bg=hover_bg, active=active)

    def __update(self, x:str):
        '''called when key is changed by user by clicking dropdown menu'''
        self.set(x)
        if self._callback:
            self._callback(self.get_text())

    def set_key(self, new_key:str, callback=False):
        '''set the key - called externally to KeyDropDown class
        
        Parameters
        ----------
            :param new_key:str - key in lilypond format such as 'a' or 'cis' or 'bes'
            :param callback: bool - if True, calls callback function
        '''
        key_name = 'A'
        for key in list(self.keys_dict.keys()):
            if self.keys_dict[key] == new_key:
                key_name = key
                break
        self.set(key_name)
        if callback and self._callback:
            self._callback(self.get_text())

    def get(self) -> str:
        '''returns key in lilypond format such as "ais" or "des" or "b"'''
        return self.keys_dict[self.get_text()]

class MeterDropDown(Frame):
    ''' Dropdown menu to edit the time signature of a song
    
        Numerator of time signature must be > 0 and denominator must be a
        power of 2 such as 4, 8, or 16
    '''
    def __init__(self, master, callback=None, default=(4, 4),
                 bg:str='#ffffff', fg:str='#000000', **kwargs):
        '''dropdown for selecting meter
        
        Parameters
        ----------
            :param master: tk.Frame - frame in which to place drowdown menu
            :param callback: function (str) - called when meter is changed
            :param default: tuple[int, int] - default meter such as (4, 4)
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - foreground color
        '''
        self._callback = callback
        Frame.__init__(self, master, bg=bg)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        Label(self, text='/', bg=bg, fg=fg).grid(row=0, column=1, padx=2)
        self.__numerator = NumberDropDown(self, list(range(1, 17)), default[0],
                                          callback=self.__update, bg=bg,
                                          fg=fg, **kwargs)
        self.__numerator.grid(row=0, column=0, sticky='nsew')
        self.__denominator = NumberDropDown(self, [1, 2, 4, 8, 16, 32],
                                            default[1], callback=self.__update,
                                            bg=bg, fg=fg, **kwargs)
        self.__denominator.grid(row=0, column=2, sticky='nsew')

    def set_active(self):
        self.__numerator.set_active()
        self.__denominator.set_active()

    def set_inactive(self):
        self.__numerator.set_inactive()
        self.__denominator.set_inactive()

    def __update(self, x=None):
        '''called when the numerator or denominator is changed'''
        if self._callback:
            self._callback(self.get_str())

    def set_meter(self, numerator:int, denominator:int, callback:bool=False):
        '''called externally to change meter
        
        Parameters
        ----------
            :param numerator: int - top of time signature - must be >= 0
            :param denominator: int - bottom of time signature - must be power of 2
            :param callback: int - if True, calls callback function
        '''
        assert isinstance(numerator, int), f'Meter numerator must be an int, not {type(numerator)}'
        assert isinstance(denominator, int), f'Meter denominator must be an integer, not {type(denominator)}'
        assert numerator > 0, f'Meter numerator must be greater than 0, not {numerator}'
        assert denominator in [1, 2, 4, 8, 16, 32], f'Meter denominator must be a power of 2, not {denominator}'
        self.__numerator.update(numerator, callback=False)
        self.__denominator.update(denominator, callback=False)
        if callback:
            self.__update()

    def get_str(self) -> str:
        '''returns meter in form 4/4 or 6/8'''
        return f'{self.__numerator.get()}/{self.__denominator.get()}'
    
    def get_fraction(self) -> Fraction:
        '''returns meter as an un-reduced Fraction'''
        return Fraction(self.__numerator.get(), self.__denominator.get(),
                        _normalize=False)
