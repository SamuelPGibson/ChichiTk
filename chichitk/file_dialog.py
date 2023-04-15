from tkinter import Frame, Label, filedialog

import os

from .buttons import IconButton


class FileDialog(Frame):
    ''' Widget that allows user to load and store file names

        The currently loaded file can be retrieved using the .get() method
    '''
    def __init__(self, master, label:str, file_types:list, bg:str,
                 fg:str='#ffffff', file_active_fg:str='#ffffff',
                 file_inactive_fg:str='#ffffff', inactive_bg:str='#000000',
                 loaded_bg:str='#00ff00', load_callback=None,
                 label_font_name='Segoe UI bold', file_font_name='Segoe UI',
                 label_font_size=10, file_font_size=10,
                 target_filenames:list=None,
                 row=None, start_col=0, padx=0, pady=0):
        '''frame to load and access filenames
        specify row to grid components directly in master
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param label: str - label to indicate what the file is for
            :param file_types: list[str] - list of filetypes such as 'wav' or 'csv'
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - label foreground color
            :param file_active_fg: str (hex code) - filename foreground when loaded
            :param file_inactive_fg: str (hex code) - filename foreground when not loaded
            :param inactive_bg: str (hex code) - filename background when not loaded
            :param loaded_bg: str (hex code) - filename background when loaded
        file_type : list of str - file types such as 'wav' or 'png'
        load_callback : 1 argument function (filename) - called when a new file is loaded
        '''
        Frame.__init__(self, master, bg=bg)
        self.__start_folder = None
        self.__load_callback = load_callback
        self.__filename = None
        self.__target_filenames = target_filenames if target_filenames else []
        self.inactive_bg, self.loaded_bg = inactive_bg, loaded_bg
        self.file_active_fg, self.file_inactive_fg = file_active_fg, file_inactive_fg
        self.__filetypes = [(f'{t.upper()} Files', f'*.{t}') for t in file_types] + [('All Files', '*.*')]

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")
        icon_path = os.path.join(image_path, "file_upload.png")

        if row != None:
            file_label = Label(master, text=label, bg=bg, fg=fg,
                               font=(label_font_name, label_font_size))
            file_label.grid(row=row, column=start_col, padx=padx, pady=pady, sticky='nsew')
            load_button = IconButton(master, icon_path, self.browse_file,
                                     popup_label='Upload File', selectable=False,
                                     bar_height=0, inactive_bg=bg)
            load_button.grid(row=row, column=start_col + 1, padx=padx, pady=pady, sticky='nsew')
            self.file_label = Label(master, text='No File Loaded', bg=inactive_bg,
                                    fg=self.file_inactive_fg,
                                    font=(file_font_name, file_font_size))
            self.file_label.grid(row=row, column=start_col + 2, padx=padx, pady=pady, sticky='nsew')
        else:
            file_label = Label(self, text=label, bg=bg, fg=fg,
                               font=(label_font_name, label_font_size))
            file_label.pack(side='left', fill='x', expand=True)
            load_button = IconButton(self, icon_path, self.browse_file,
                                     popup_label='Upload File', selectable=False,
                                     bar_height=0, inactive_bg=bg)
            load_button.pack(side='right')
            self.file_label = Label(self, text='No File Loaded', bg=inactive_bg,
                                    fg=self.file_inactive_fg,
                                    font=(file_font_name, file_font_size))
            self.file_label.pack(side='left', fill='x', expand=True)

    def load(self, folder):
        '''sets start folder for browsing files
        
        folder : str - path to song folder such as "C:\\Users\\samue\\Electric Praise Songs\\Tester - Test Song"
        '''
        self.__start_folder = folder
        for filename in self.__target_filenames:
            if os.path.exists(self.__start_folder + '\\' + filename):
                self.load_file(self.__start_folder + '\\' + filename)
                break

    def load_file(self, filename:str):
        '''load file internal command instead of user browsing file'''
        if isinstance(filename, str) and filename != '' and os.path.exists(filename): # didnt click 'cancel' instead of selecting a file
            self.__filename = filename
            if '/' in self.__filename:
                text = self.__filename.split('/')[-1]
            elif '\\' in self.__filename:
                text = self.__filename.split('\\')[-1]
            else:
                text = self.__filename
            self.file_label.config(text=text, bg=self.loaded_bg,
                                   fg=self.file_active_fg)
            if self.__load_callback:
                self.__load_callback(self.__filename)

    def browse_file(self):
        '''user click upload button to browse file from computer'''
        self.load_file(filedialog.askopenfilename(initialdir=self.__start_folder,
                                                  title='Select File', filetypes=self.__filetypes))

    def is_loaded(self):
        '''returns True if a file is loaded, otherwise False'''
        return self.__filename is not None

    def get(self):
        '''returns filename assuming a file has been loaded
        returns None if no file is loaded'''
        return self.__filename

    def remove(self):
        '''removes and discards the file that is currently loaded'''
        self.__filename = None
        self.file_label.config(text='No File Loaded', bg=self.inactive_bg,
                               fg=self.file_inactive_fg)
