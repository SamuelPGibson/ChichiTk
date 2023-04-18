from tkinter import Toplevel, Frame, Label, Text, Scrollbar, PhotoImage
from threading import Thread
import fitz # fitz is PyMuPDF

from .buttons import IconButton
from .icons import icons


class PdfDisplay(Frame):
    ''' Widget that displays pdf or 'No File Loaded' label when no pdf is loaded
    
        Contains a button that allows the user to open the pdf in a new window
    '''
    def __init__(self, master, bg, fg, font_name:str='Segoe UI', font_size:int=20,
                 button_pad:int=2, view_width=75, zoom_fact=1, height:int=600,
                 buttons_side='left', buttons_bg='#ffffff',
                 new_window_option=True, zoom_options=True):
        '''
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param bg: str (hex code) - background color
            :param fg: str (hex code) - color of 'No File Loaded' label
            :param font_name: str - font name such as 'Segoe UI'
            :param font_size: int - font size
            :param button_pad: int - padding between button and top left corner
            :param view_width: int - width of view in pixels
            :param zoom_fact: float - factor by which to zoom pdf
            :param buttons_side: str - Literal['left', 'right']
            :param buttons_bg: str (hex code) - background color of buttons
            :param new_window_option: bool - if True, include button to open in new window
        '''
        assert buttons_side in ['left', 'right'], f"Invalid buttons side: '{buttons_side}', must be 'left' or 'right'"
        Frame.__init__(self, master, bg=bg)
        self.button_pad = button_pad
        self.bg = bg # store for new window
        self.width, self.height = view_width, height
        self.zoom_fact = zoom_fact # never changes
        self.scale_fact = 1 # changes when zooming in and out
        self.img_object_list = []
        self.buttons_side = buttons_side
        self.pdf_frame = None # tk.Frame once a pdf is loaded
        self.active = False # True when a pdf is loaded

        # Buttons Frame
        self.buttons_frame = Frame(self, bg='#ffffff')

        if new_window_option:
            new_button = IconButton(self.buttons_frame, icons['open_in_new'],
                                    command=self.open_in_window, bar_height=0,
                                    selectable=False, inactive_bg=buttons_bg,
                                    inactive_hover_fg=None, popup_bg=self.bg,
                                    popup_label='Open In New Window')
            new_button.pack(side=buttons_side)

        if zoom_options:
            out_button = IconButton(self.buttons_frame, icons['minus'],
                                    command=self.zoom_out, bar_height=0,
                                    selectable=False, inactive_bg=buttons_bg,
                                    inactive_hover_fg=None, popup_bg=self.bg,
                                    popup_label='Zoom Out')
            in_button = IconButton(self.buttons_frame, icons['plus'],
                                   command=self.zoom_in, bar_height=0,
                                   selectable=False, inactive_bg=buttons_bg,
                                   inactive_hover_fg=None, popup_bg=self.bg,
                                   popup_label='Zoom In')
            out_button.pack(side='left')
            in_button.pack(side='left')
        
        # Inactive Label
        self.label = Label(self, text='No File Loaded', bg=bg, fg=fg,
                           font=(font_name, font_size))
        self.label.pack(fill='both', expand=True)

    def position_buttons(self, event=None):
        '''repositions buttons - called when window is resized'''
        if self.active:
            if self.buttons_side == 'left':
                x = self.pdf_frame.winfo_x() + self.button_pad
                anchor = 'nw'
            elif self.buttons_side == 'right':
                right_edge = self.pdf_frame.winfo_x() + self.pdf_frame.winfo_width()
                x = right_edge - self.scroll_y.winfo_width() - self.button_pad
                anchor = 'ne'
            else: # this should never happen
                raise ValueError(f'PdfDisplay button side is invalid: {self.buttons_side}')
            self.buttons_frame.place(x=x, y=self.pdf_frame.winfo_y() + self.button_pad,
                                     anchor=anchor)
            self.buttons_frame.lift() # raise above pdf

    def remove_all(self):
        '''removes pdf, buttons, and label'''
        self.active = False
        self.label.pack_forget()
        self.buttons_frame.place_forget()
        if self.pdf_frame != None:
            self.pdf_frame.destroy()

    def show_pdf(self, filename:str):
        '''loads pdf from the fiven filepath'''
        self.scale_fact = 1 # reset zoom
        self.filename = filename
        self.remove_all()
        self.active = True
        Thread(target=self.render_pdf()).start()

    def render_pdf(self):
        '''loads pdf from self.filename - MUST be called in Thread'''
        # Create image objects from pdf pages
        self.img_object_list = []
        for page in fitz.open(self.filename):
            pix = page.get_pixmap(dpi=int(72 * self.zoom_fact * self.scale_fact))
            pix1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
            image = pix1.tobytes("ppm")
            self.img_object_list.append(PhotoImage(data=image))

        # Create new pdf frame
        width = int(self.width * self.scale_fact)
        height = int(self.height * self.scale_fact)
        self.pdf_frame = Frame(self, height=height, width=width, bg=self.bg)
        self.scroll_y = Scrollbar(self.pdf_frame, orient="vertical")
        self.scroll_x = Scrollbar(self.pdf_frame, orient="horizontal")
        self.scroll_x.pack(side='bottom', fill='x')
        self.scroll_y.pack(side='right', fill='y')
        # Font size is used to control the space between pages
        self.pdf_text = Text(self.pdf_frame, bg=self.bg, yscrollcommand=self.scroll_y.set,
                             xscrollcommand=self.scroll_x.set, #font=('Segoe UI', 2),
                             height=height, width=width)
        self.pdf_text.pack(side="left")
        self.scroll_x.config(command=self.pdf_text.xview)
        self.scroll_y.config(command=self.pdf_text.yview)
        self.pdf_frame.pack()
        self.pdf_frame.bind('<Configure>', self.position_buttons)
        self.update() # render so that buttons are positioned properly
        self.position_buttons() # place buttons and raise above pdf

        # Add pages to text box
        for i, img in enumerate(self.img_object_list):
            if i > 0: # add space before next page
                self.pdf_text.insert('end', '\n\n')
            self.pdf_text.image_create('end', image=img)
        self.pdf_text.configure(state='disabled')

    def remove_pdf(self):
        '''removes pdf and goes back to 'No File Loaded' label'''
        self.remove_all()
        self.label.config(text='No File Loaded')
        self.label.pack(fill='both', expand=True)

    def zoom_in(self):
        '''update zoom_fact and re-render pdf'''
        self.scale_fact *= 1.1
        self.remove_all()
        self.active = True
        Thread(target=self.render_pdf()).start()

    def zoom_out(self):
        '''update zoom_fact and re-render pdf'''
        self.scale_fact /= 1.1
        self.remove_all()
        self.active = True
        Thread(target=self.render_pdf()).start()

    def to_loading(self, text='Loading...'):
        '''removes current pdf and displays loading text'''
        self.remove_all()
        self.label.config(text=text)
        self.label.pack(fill='both', expand=True)

    def open_in_window(self):
        '''opens PDF in new window - can only ever be called when a PDF is being viewed'''
        PdfWindow(self.filename, self.bg)

class PdfWindow(Toplevel):
    ''' Window to view a single PDF File
    
        PDFs being view in PdfWindow cannot be opened in another new window,
        obviously
    '''
    def __init__(self, filepath:str, bg:str, window_title='PDF Viewer',
                 width_fact:float=0.9, height_fact:float=0.99):
        '''creates window to view pdf
        
        Parameters
        ----------
            :param filepath: str - absolute path to a .pdf file
            :param bg: str (hex code) - window background color
            :param window_title: str - window name displayed in top left corner
            :param width_fact: float between 0 and 1 - percentage of screen width covered by window
            :param height_fact: float between 0 and 1 - percentage of screen height covered by window
        '''
        Toplevel.__init__(self)

        self.config(bg=bg)
        self.title(window_title)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = int(sw * width_fact), int(sh * height_fact)
        self.geometry(f'{w}x{h}+{sw // 2 - w // 2}+{sh // 2 - h // 2}')

        pdf = PdfDisplay(self, bg, '#ffffff', view_width=150, zoom_fact=2,
                         new_window_option=False)
        pdf.pack(fill='both', expand=True)
        pdf.show_pdf(filepath)

