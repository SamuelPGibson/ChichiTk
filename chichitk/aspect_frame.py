from tkinter import Frame


class AspectFrame(Frame):
    ''' Dynamic Frame that uses flexible border padding to maintain a
        consistent aspect ratio

        All content should be put in AspectFrame.frame NOT in AspectFrame
        directly

        For AspectFrame to work as intended, pack with fill='both' and
        expand=True, and grid with sticky='nsew'

        DO NOT use AspectFrame.place() because then AspectFrame will not work

        AspectFrame should ALWAYS be packed with expand=True and grid with
        sticky='nsew' and parent widget gridrowconfigure and gridcolumnconfigure
    '''
    def __init__(self, master, aspect_ratio:float, pad_bg:str='#ffffff',
                 frame_bg:str='#ffffff', config_callback:callable=None,
                 size_callback:callable=None):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param pad_bg: str (hex code) - color of padding
            :param frame_bg: str (hex code) - frame background color
            :param config_callback: function (event) - called whenever frame is resized
            :param size_callback: function (width, height) - called whenever frame is resized
        '''
        Frame.__init__(self, master, bg=pad_bg)
        self.__aspect_ratio = aspect_ratio
        self.__config_callback = config_callback
        self.__size_callback = size_callback

        self.__max_width, self.__max_height = 1, 1 # based on entire frame size
        self.__width, self.__height = 1, 1 # based on aspect ratio within frame

        self.frame = Frame(self, bg=frame_bg)

        self.bind('<Configure>', self.__configure)
        #self.event_generate('<Configure>', when='tail')

    def __configure(self, event):
        '''places self.frame within self with the appropiate aspect ratio'''
        self.__max_width, self.__max_height = event.width, event.height
        self.__width, self.__height = self.__compute_dims()
        
        self.frame.place(in_=self, relx=0.5, rely=0.5, anchor='center',
                         width=self.__width, height=self.__height)

        if self.__config_callback:
            self.__config_callback(event)
        if self.__size_callback:
            self.__size_callback(*self.get_dims())

    def __compute_dims(self):
        '''returns width, height based on max_width, max_height, and aspect_ratio'''
        # start by using the width as the controlling dimension
        width = self.__max_width
        height = int(self.__max_width / self.__aspect_ratio)

        # if window is too tall to fit, use the height as controlling dimension
        if height > self.__max_height:
            height = self.__max_height
            width = int(self.__max_height * self.__aspect_ratio)

        return width, height

    def set_aspect_ratio(self, aspect_ratio:float):
        ''':param aspect_ratio: float - ratio of width / height'''
        self.__aspect_ratio = aspect_ratio
        self.__width, self.__height = self.__compute_dims()
        self.frame.place(in_=self, relx=0.5, rely=0.5, anchor='center',
                         width=self.__width, height=self.__height)

    def get_aspect_ratio(self) -> float:
        '''returns aspect ratio: ratio of width / height'''
        return self.__aspect_ratio
    
    def get_dims(self):
        '''returns inner frame width, height as tuple'''
        return self.__width, self.__height
