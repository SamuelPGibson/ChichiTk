from tkinter import Frame


class AspectFrame(Frame):
    ''' Dynamic Frame that uses flexible border padding to maintain a
        consistent aspect ratio

        All content should be put in AspectFrame.frame NOT in AspectFrame
        directly

        For AspectFrame to work as intended, pack with fill='both' and
        expand=True, and grid with sticky='nsew'

        DO NOT use AspectFrame.place() because then AspectFrame will not work
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

        self.frame = Frame(self, bg=frame_bg)

        self.bind('<Configure>', self.__configure)
        #self.event_generate('<Configure>', when='tail')

    def __configure(self, event):
        '''places self.frame within self with the appropiate aspect ratio'''
        # start by using the width as the controlling dimension
        desired_width = event.width
        desired_height = int(event.width / self.__aspect_ratio)

        # if window is too tall to fit, use the height as controlling dimension
        if desired_height > event.height:
            desired_height = event.height
            desired_width = int(event.height * self.__aspect_ratio)

        self.frame.place(in_=self, relx=0.5, rely=0.5, anchor='center',
                         width=desired_width, height=desired_height)

        if self.__config_callback:
            self.__config_callback(event)
        if self.__size_callback:
            self.__size_callback(desired_width, desired_height)
