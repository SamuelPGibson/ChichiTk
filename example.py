from tkinter import Tk, Frame, Label

import chichitk
from chichitk.icons import icons


class OptionGroup(Frame):
    ''' Contains two dropdown menus and an EditLabel
    '''
    def __init__(self, master, bg:str, label_padx=10):
        super().__init__(master, bg=bg)

        for i, label in enumerate(['Key', 'Meter', 'Tempo']):
            label = Label(self, text=label, bg=bg, fg='#ffffff', font=('Segoe UI', 10))
            label.grid(row=0, column=i, padx=label_padx, sticky='nsew')
            
        key = chichitk.KeyDropDown(self, 'A', bg=bg, fg='#ffffff')
        meter = chichitk.MeterDropDown(self, bg=bg, fg='#ffffff')
        tempo = chichitk.EditLabel(self, '120', bg=bg, fg='#ffffff',
                                   allowed_chars='0123456789', max_len=3,
                                   check_function=lambda s: len(s) > 0 and int(s) > 20,
                                   justify='center')
        for i, widget in enumerate([key, meter, tempo]):
            widget.grid(row=1, column=i, padx=label_padx, sticky='nsew')

class Header(Frame):
    ''' App header
    '''
    def __init__(self, master, bg:str):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param bg: str (hex code) - background color
        '''
        super().__init__(master, bg=bg)

        OptionGroup(self, bg).pack(side='right')
        OptionGroup(self, bg).pack(side='left')

        player = chichitk.Player(self, lambda x: None, 1/100, bg=bg,
                                 slider_type='simple', frame_num=12001,
                                 frame_rate=1, step_increment=500,
                                 buttons_on_top=True, simple_slider_width=300)
        player.pack(side='top')

class Footer(Frame):
    ''' App footer
    '''
    def __init__(self, master, bg:str):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param bg: str (hex code) - background color
        '''
        super().__init__(master, bg=bg)

        Label(self, text='ChichiTk 0.0.1 Example App', bg=bg, fg='#bbbbbb',
              font=('Segoe UI', 12)).pack(side='left')
        
        pdf_button = chichitk.ToggleIconButton(self, icons['open_in_new'],
                                               self.toggle_pdf, inactive_bg=bg,
                                               active_bg=bg, bar_height=0,
                                               popup_label='Show/Hide PDF',
                                               selected=True)
        pdf_button.pack(side='right')
        Label(self, text=' ' * 24, bg=bg, fg='#bbbbbb',
              font=('Segoe UI', 12)).pack(side='right') # for spacing

        buttons_frame = Frame(self, bg=bg)
        buttons_frame.pack(side='bottom')
        self.buttons: list[chichitk.IconButton] = []
        for i in range(4):
            button = chichitk.IconButton(buttons_frame, icons['edit'],
                                         self.deselect_buttons, label=f'Page {i + 1}',
                                         inactive_bg=bg, active_bg='#000000',
                                         popup_label=f'Go to page {i + 1} (not actually)',
                                         padx=20)
            button.pack(side='left')
            self.buttons.append(button)
        self.buttons[0].select()
            
    def deselect_buttons(self):
        '''deselects all buttons'''
        for button in self.buttons:
            button.deselect()

    def toggle_pdf(self, on:bool):
        '''show/hide PdfDisplay (right side)'''
        if on:
            Pdf.pack(side='right', fill='y')
        else:
            Pdf.pack_forget()

class LeftFrame(Frame):
    def __init__(self, master):
        super().__init__(master, bg=colors[1])

        # Slider Group - Bottom
        collapse_frame = chichitk.CollapseFrame(self, label='Horizontal Sliders', label_side='top',
                                                font_name='Segoe UI bold', font_size=14,
                                                bg=colors[1], active_bg=colors[0], inactive_hover_bg=colors[1],
                                                active_hover_bg=colors[2], inactive_hover_fg='#00ff00',
                                                inactive_fg='#ffffff',
                                                padx=5, pady=5)
        collapse_frame.pack(side='bottom', fill='both')
        params = [{'label':'Slider 1', 'value':10, 'min_value':0, 'max_value':50, 'step':1, 'description':'Slider 1 description here'},
                  {'label':'Slider 2', 'value':20, 'min_value':0, 'max_value':50, 'step':1},
                  {'label':'Slider 3', 'value':30, 'min_value':0, 'max_value':50, 'step':1}]
        group = chichitk.HorizontalSliderGroup(collapse_frame.frame, params,
                                               callback=lambda x, y: None,
                                               bg=colors[1], rows=1, columns=3,
                                               active_line_color='#00ff00', hide_slider=False,
                                               label_draggable=True, text_fg='#ffffff',
                                               slider_type='rectangle', slider_width=25, slider_height=8)
        group.pack(side='bottom', fill='x')

        # Widgets Frame - Bottom
        collapse_frame = chichitk.CollapseFrame(self, label='Select Widgets', label_side='top',
                                                font_name='Segoe UI bold', font_size=14,
                                                bg=colors[1], active_bg=colors[0], inactive_hover_bg=colors[1],
                                                active_hover_bg=colors[2], inactive_hover_fg='#00ff00',
                                                inactive_fg='#ffffff',
                                                padx=5, pady=5)
        collapse_frame.pack(side='bottom', fill='both')
        frame = collapse_frame.frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        for i in range(4):
            frame.grid_rowconfigure(i, weight=1)

        for i, label in enumerate(['Dropdown', 'Check Entry', 'Color Entry', 'Upload File', 'Time Label', 'Range Labels', 'Slider']):
            Label(frame, text=label, bg=colors[1], fg='#ffffff',
                  font=('Segoe UI', 11)).grid(row=i, column=0)
        dropdown = chichitk.BasicDropDown(frame, ['Option 1', 'Option 2', 'Option 3'],
                                          'Select', bg=colors[0], fg='#ffffff')
        entry = chichitk.CheckEntry(frame, bg=colors[0], fg='#ffffff')
        color_entry = chichitk.ColorEntry(frame, bg=colors[0], fg='#ffffff')
        upload = chichitk.FileDialog(frame, '', file_types=['wav', 'mp3'],
                                     bg=colors[0], fg='#ffffff')
        time = chichitk.TimeEditLabel(frame, print, min_value=0, max_value=600,
                                      default_value=100, step=0.001, bg=colors[0],
                                      fg='#ffffff', hover_bg=colors[2])
        number = chichitk.RangeLabel(frame, default_min=20, default_max=30,
                                     bg=colors[0], fg='#ffffff',
                                     hover_bg=colors[2])
        slider = chichitk.HorizontalSlider(frame, bg=colors[0],
                                           min_value=10, max_value=50, default_value=25,
                                           active_line_color='#ffffff',
                                           active_line_hover_color='#00ff00',
                                           hide_slider=True, slider_type='circle',
                                           label_draggable=True, label_fg='#ffffff',
                                           text_fg='#ffffff', label='', step=0.1)
        for i, widget in enumerate([dropdown, entry, color_entry, upload, time, number, slider]):
            widget.grid(row=i, column=1, pady=2, sticky='nsew')

        # Textbox - Top
        Label(self, text='Lined Textbox', bg=colors[0], fg='#ffffff',
              font=('Segoe UI bold', 14)).pack(side='top', fill='x')
        Text = chichitk.TextBox(self, bg=colors[0], fg='#ffffff', width=35,
                                height=20, check_consecutive_spaces=True,
                                check_blank_lines=False, font_size=12)
        Text.pack(side='top', fill='both', expand=True, pady=1)
        Text.clear_insert(placeholder_text)

class Stopwatch(Frame):
    ''' Stopwatch that utilizes chichitk Player to control start/stop
    '''
    def __init__(self, master, seconds=240, seconds_degree=0, step_seconds=5,
                 show_hours=False, **kwargs):
        '''
        Parameters
        ----------
            :param seconds: int - number of seconds on stopwatch
            :param seconds_degree: int - order of magnitude for second divisions
                                       - 0 is whole seconds, 3 is miliseconds
            :param step_seconds: int - seconds to skip forward and back with buttons
            :param show_hours: bool - if True, displays time in form hh:mm:ss...
        '''
        assert seconds_degree in range(4), f'seconds_degree is out of range: {seconds_degree}'
        self.total_seconds = seconds
        self.seconds_degree = seconds_degree
        self.show_hours = show_hours
        super().__init__(master, bg=colors[0], **kwargs)

        # Time Label
        frame = chichitk.AspectFrame(self, 16/9, pad_bg=colors[2], frame_bg=colors[1])
        frame.pack(side='top', fill='both', expand=True)
        self.__time_label = Label(frame.frame, text='', bg=colors[1], fg='#ffffff',
                                  font=('Segoe UI bold', 30))
        self.__time_label.place(relx=0.5, rely=0.5, anchor='center')

        self.__Player = chichitk.Player(self, self.__update_time,
                                        1 / 10 ** self.seconds_degree,
                                        bg=colors[0], slider_type='double',
                                        frame_num=self.total_seconds * 10**self.seconds_degree + 1,
                                        frame_rate=10**self.seconds_degree,
                                        step_increment=step_seconds * 10**self.seconds_degree)
        self.__Player.pack(fill='x')

        self.__update_time(0)

    def __update_time(self, time:int):
        '''updates label based on time'''
        f = 10 ** self.seconds_degree
        second = (time % (60 * f)) // f
        if self.show_hours:
            hour = time // (3600 * f)
            minute = (time % (3600 * f)) // (60 * f)
            text = f'{hour:0>2}:{minute:0>2}:{second:0>2}'
        else:
            minute = time // (60 * f)
            text = f'{minute}:{second:0>2}'
        if self.seconds_degree > 0: # partial seconds
            text += f'.{time % f:0>{self.seconds_degree}}'
        self.__time_label.configure(text=text)


placeholder_text = '''ChichiTk Textbox can execute a
callback function whenever the
text is edited by the user.
Checks such as blank lines and
consecutive spaces can be
performed automatically by
Textbox when the text is edited.
ChichiTk Textbox could serve as
a basis for any syntax-checking
application.'''


colors = {0:'#1e1e22', 1:'#232328', 2:'#28282e'}

app = Tk()
app.title('ChichiTk Example App')
app.config(bg=colors[0])
sw, sh = app.winfo_screenwidth(), app.winfo_screenheight()
w, h = int(sw * 0.9), int(sh * 0.7)
app.geometry(f'{w}x{h}+{sw // 2 - w // 2}+{sh // 2 - h // 2}')

Footer(app, '#121215').pack(side='bottom', fill='x')
Header(app, '#121215').pack(side='top', fill='x')

Pdf = chichitk.PdfDisplay(app, bg=colors[1], fg='#999999', buttons_side='right')
Pdf.pack(side='right', fill='y')
Pdf.show_pdf('example.pdf')
Pdf.zoom_out()
Pdf.zoom_out()
Pdf.zoom_out()

Left = LeftFrame(app)
Left.pack(side='left', fill='y')

W = Stopwatch(app, seconds_degree=2, show_hours=True)
W.pack(side='left', fill='both', expand=True)

app.mainloop()

