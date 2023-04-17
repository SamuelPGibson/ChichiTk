from tkinter import Canvas, Frame, Label

import numpy as np

from .tool_tip import ToolTip
from .labels import EditLabel
from .canvas_items import CanvasEditLine, CanvasEditFill, brighten


# helper functions
def seconds_text(sec:float):
    '''converts seconds to text in form (hh):(m)m:ss'''
    sec = int(sec)
    if sec >= 3600: # at least one hour
        return f'{sec // 3600}:{(sec % 3600) // 60:0>2}:{(sec % 60) // 1:0>2}'
    else: # less than one hour
        return f'{sec // 60}:{(sec % 60) // 1:0>2}'
    

class BasicSlider(Frame):
    ''' Parent class of HorizontalSlider and VerticalSlider - contains common
        methods
        
        DO NOT use this class directly because it will not work
    '''
    def __init__(self, master:Frame, command, bg:str, min_value:float,
                 max_value:float, step:float, start_value=0, padx=0, pady=0,
                 slider_ac='#13ce12', slider_ic='#ffffff', line_ac='#999999',
                 line_ic='#888888', slider_height=20, slider_width=35, active=True):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param command: function (value) - called when slider is moved
            :param bg: str (hex code) - background color
            :param min_value: float - slider minimum value
            :param max_value: float - slider maximum value
            :param step: float - slider increment
            :param start_value: float - default value
            :param padx: int - internal x pad
            :param pady: int - internal y pad
            :param slider_ac: str (hex code) - slider color while being dragged
            :param slider_ic: str (hex code) - slider color when not dragging
            :param line_ac: str (hex code) - line color when cursor is hovering
            :param line_ic: str (hex code) - line color when not hovering
            :param slider_height: int - height of slider in pixels
            :param slider_width: int - width of slider in pixels
            :param active: bool - if True, slider is interactable by user
        '''
        self.active = active
        self.command = command
        if step % 1 == 0: # integer
            self.decimals = 0
        else:
            self.decimals = len(str(step).split(".")[1])
        self.slider_colors = [slider_ic, slider_ac]
        self.line_colors = [line_ic, line_ac]
        self.hovering, self.slider_hovering, self.dragging = False, False, False
        self.min, self.max, self.current_value, self.step = min_value, max_value, start_value, step
        self.values = np.arange(self.min, self.max + self.step * 0.9, self.step)
        self.slider_height, self.slider_width = slider_height, slider_width
        Frame.__init__(self, master, bg=bg, padx=padx, pady=pady)

    def color_config(self):
        '''updates color of line and slider based on hover and drag status'''
        self.canvas.itemconfig(self.line_id, fill=self.line_colors[self.hovering or self.dragging])
        self.canvas.itemconfig(self.slider_id, fill=self.slider_colors[self.slider_hovering or self.dragging])

    def get_value_text(self) -> str:
        '''returns value text formatted as string'''
        if self.decimals == 0:
            return str(int(self.current_value))
        text = str(round(self.current_value, self.decimals))
        if '.' in text:
            dec = len(text.split(".")[1])
        else:
            text += '.'
            dec = 0
        return text + '0' * (self.decimals - dec)
    
    def get_value(self):
        '''returns slider value'''
        return self.current_value

    def set_value(self, value:float, callback=False):
        '''
        Purpose:
            sets the value of slider
            called when slider is moved (with drag) or EditLabel is updated
        Pre-conditions:
            :param value: float - new value of slider
            :param callback: bool - if True calls self.command(value)
        Post-conditions:
            changes the value of slider
        Returns:
            (none)
        '''
        self.current_value = value
        self.canvas.coords(self.slider_id, *self.get_slider_coords())
        self.label.set_text(text=self.get_value_text(), callback=False)
        if callback:
            self.command(self.current_value)

    def round_value(self, value:float):
        '''
        Purpose:
            rounds value to the closest acceptable value based on self.values
            intended to be called when value is set manually with EditLabel
        Pre-conditions:
            :param value: float - new value
        Post-conditions:
            (none)
        Returns:
            :return: float or int - new rounded value
        '''
        return self.values[np.absolute(self.values - value).argmin()]

    def slider_hover_enter(self, event=None):
        '''called when cursor hovers on the slider'''
        if self.active:
            self.slider_hovering = True
            self.color_config()

    def slider_hover_leave(self, event=None):
        '''called when cursor leaves the slider'''
        if self.active:
            self.slider_hovering = False
            self.color_config()

    def label_hover_enter(self, event=None):
        '''called when cursor enters the label'''
        if self.popup_label:
            self.tool_tip.fadein(0, self.popup_label, event)

    def label_hover_leave(self, event=None):
        '''called when cursor enters the label'''
        if self.popup_label:
            self.tool_tip.fadeout(1, event) # first argument is initial alpha

    def hover_enter(self, event=None):
        '''called when cursor enters the widget'''
        if self.active:
            self.hovering = True
            self.color_config()

    def hover_leave(self, event=None):
        '''called when cursor leaves the widget'''
        if self.active:
            self.hovering = False
            self.color_config()

    def click(self, event):
        '''cursor clicks on canvas - move slider to click location'''
        if self.active:
            self.dragging = True
            self.color_config()
            value = self.get_cursor_value(event.x, event.y)
            if value != self.current_value:
                self.set_value(value, callback=True)

    def release(self, event=None):
        '''cursor releases click on the canvas'''
        if self.active:
            self.dragging = False
            self.color_config()

    def motion(self, event):
        '''called when cursor drags slider'''
        if self.active:
            value = self.get_cursor_value(event.x, event.y)
            if value != self.current_value:
                self.set_value(value, callback=True)

    def turn_on(self):
        '''called externally to make slider interactable by user'''
        self.active = True
        self.label.set_active()

    def turn_off(self):
        '''called externally to make slider uninteractable by user'''
        self.active = False
        self.label.set_inactive()

class HorizontalSlider(BasicSlider):
    ''' Horizontally oriented slider - user slides from left to right

        User can double slick on the value label to enter an exact value
    
        Calls callback command whenever slider is moved by user
    '''
    def __init__(self, master:Frame, label:str, command, bg:str,
                 min_value:float, max_value:float, step:float, start_value=0,
                 popup_label=None, padx:int=0, pady:int=0, width:int=250,
                 slider_ac='#13ce12', slider_ic='#ffffff', line_ac='#999999',
                 line_ic='#888888', text_color='#888888', popup_bg='#000000',
                 font_name='Segoe UI', label_font_size=14, val_font_size=11,
                 slider_height=35, slider_width=20, line_width=10,
                 justify='right', title_label=False, active=True):
        '''Horizontal Slider
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param label: str - label displayed to the left of slider
            :param command: function (value) - called when slider is moved
            :param bg: str (hex code) - background color
            :param min_value: float - slider minimum value
            :param max_value: float - slider maximum value
            :param step: float - slider increment
            :param start_value: float - default value
            :param popup_label: str - text displayed in info popup upon mouse hover
            :param padx: int (pixels) - internal x pad
            :param pady: int (pixels) - internal y pad
            :param width: int (pixels) - widget width
            :param slider_ac: str (hex code) - slider color while being dragged
            :param slider_ic: str (hex code) - slider color when not dragging
            :param line_ac: str (hex code) - line color when cursor is hovering
            :param line_ic: str (hex code) - line color when not hovering
            :param slider_height: int - height of slider in pixels
            :param slider_width: int - width of slider in pixels
            :param text_color: String (hex code) - color of text
            :param popup_bg: str (hex code) - background color of info popup
            :param justify: str - slider placement in frame - options: ['left', 'right', 'center']
            :param title_label: bool - if True, display 'fade_in' as 'Fade In' - convert snake_case to Title Case
            :param active: bool - if True, slider is interactable by user
        '''
        self.width = width
        BasicSlider.__init__(self, master, command, bg, min_value, max_value,
                             step, start_value=start_value, padx=padx, pady=pady,
                             slider_ac=slider_ac, slider_ic=slider_ic,
                             line_ac=line_ac, line_ic=line_ic,
                             slider_height=slider_height, slider_width=slider_width,
                             active=active)

        frame = Frame(self, bg=bg, height=slider_height)
        if justify == 'center':
            frame.place(relx=0.5, rely=0.5, anchor='center')
        else:
            frame.pack(side=justify)
        check_function = lambda s: len(s) > 0 and s.count('.') <= 1 and s != '.' and float(s) >= self.min and float(s) <= self.max
        self.label = EditLabel(frame, self.get_value_text(), fg=text_color, bg=bg, hover_bg=brighten(bg, 0.02),
                               callback=lambda s: self.set_value(self.round_value(float(s)), callback=True),
                               check_function=check_function, allowed_chars='0123456789.', editable=self.active,
                               justify='left', font_name=font_name, font_size=val_font_size)
        self.label.pack(side='right')
        self.canvas = Canvas(frame, bg=bg, height=self.slider_height, width=self.width, highlightthickness=0)
        self.canvas.pack(side='right')
        label_text = label.replace('_', ' ').title() if title_label else label # convert from snake_case to Title Case
        self.popup_label = label_text + ': ' + popup_label if popup_label else popup_label
        slider_label = Label(frame, text=label_text, bg=bg, fg=text_color, font=(font_name, label_font_size))
        slider_label.pack(side='right')
        self.tool_tip = ToolTip(self, bg=popup_bg, fg='#ffffff', font=(font_name, val_font_size))
        slider_label.bind('<Enter>', self.label_hover_enter)
        slider_label.bind('<Leave>', self.label_hover_leave)

        self.canvas.bind('<Enter>', self.hover_enter)
        self.canvas.bind('<Leave>', self.hover_leave)
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<ButtonRelease-1>', self.release)

        self.line_id = self.canvas.create_line(self.slider_width / 2, self.slider_height / 2, self.width - self.slider_width / 2,
                                                self.slider_height / 2, fill=self.line_colors[0],
                                                width=line_width, state='disabled')
        self.slider_id = self.canvas.create_rectangle(*self.get_slider_coords(), fill=self.slider_colors[0], width=0, state='normal')
        self.canvas.tag_bind(self.slider_id, '<Enter>', self.slider_hover_enter)
        self.canvas.tag_bind(self.slider_id, '<Leave>', self.slider_hover_leave)

    def get_value_text(self) -> str:
        '''returns value text formatted as string - overrides same function in BasicSlider'''
        if self.decimals == 0:
            return str(int(self.current_value)) + '  ' * (len(str(int(self.max))) - len(str(int(self.current_value))))
        text = str(round(self.current_value, self.decimals))
        if '.' in text:
            dec = len(text.split(".")[1])
        else:
            text += '.'
            dec = 0
        return text + '0' * (self.decimals - dec) + '  ' * (len(str(int(self.max))) - len(str(int(self.current_value))))

    def get_slider_coords(self):
        '''returns x0, y0, x1, and y1 for slider based on self.current_value'''
        perc = (self.current_value - self.min) / (self.max - self.min)
        x_center = self.slider_width / 2 + (self.width - self.slider_width) * perc
        return x_center - self.slider_width / 2, 0, x_center + self.slider_width / 2, self.slider_height

    def get_cursor_value(self, x, y):
        '''returns current_value based on x, y'''
        perc = (x - self.slider_width / 2) / (self.width - self.slider_width)
        value = self.min + (self.max - self.min) * perc
        return self.values[np.absolute(self.values - value).argmin()]

class VerticalSlider(BasicSlider):
    ''' Vertically oriented slider - user slides from bottom to top
    
        User can double click on the value label to enter an exact value
        
        Calls callback command whenever slider is moved by user
    '''
    def __init__(self, master:Frame, label:str, command, bg:str,
                 min_value:float, max_value:float, step:float, start_value=0,
                 popup_label=None, padx=0, pady=0, height=250, slider_ac='#13ce12',
                 slider_ic='#ffffff', line_ac='#999999', line_ic='#888888',
                 text_color='#888888', popup_bg='#000000', font_name='Segoe UI',
                 label_font_size=14, val_font_size=11, title_label=False,
                 slider_height=20, slider_width=35, line_width=10, active=True):
        '''Vertical Slider - inherits from tk.Frame - does not pack or grid
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param label: str - label displayed to the left of slider
            :param command: function (value) - called when slider is moved
            :param bg: str (hex code) - background color
            :param min_value: float - slider minimum value
            :param max_value: float - slider maximum value
            :param step: float - slider increment
            :param start_value: float - default value
            :param popup_label: str - text displayed in info popup upon mouse hover
            :param padx: int (pixels) - internal x pad
            :param pady: int (pixels) - internal y pad
            :param height: int (pixels) - widget height
            :param slider_ac: str (hex code) - slider color while being dragged
            :param slider_ic: str (hex code) - slider color when not dragging
            :param line_ac: str (hex code) - line color when cursor is hovering
            :param line_ic: str (hex code) - line color when not hovering
            :param slider_height: int - height of slider in pixels
            :param slider_width: int - width of slider in pixels
            :param text_color: String (hex code) - color of text
            :param popup_bg: str (hex code) - background color of info popup
            :param justify: str - slider placement in frame - options: ['left', 'right', 'center']
            :param title_label: bool - if True, display 'fade_in' as 'Fade In' - convert snake_case to Title Case
            :param active: bool - if True, slider is interactable by user
        '''
        self.height = height
        BasicSlider.__init__(self, master, command, bg, min_value, max_value, step, start_value=start_value, padx=padx, pady=pady,
                                slider_ac=slider_ac, slider_ic=slider_ic, line_ac=line_ac, line_ic=line_ic, slider_height=slider_height,
                                slider_width=slider_width, active=active)

        label_text = label.replace('_', ' ').title() if title_label else label
        self.popup_label = label_text + ': ' + popup_label if popup_label else popup_label
        slider_label = Label(self, text=label_text, bg=bg, fg=text_color, font=(font_name, label_font_size))
        slider_label.pack(side='top', fill='x')
        self.tool_tip = ToolTip(self, bg=popup_bg, fg='#ffffff', font=(font_name, val_font_size))
        slider_label.bind('<Enter>', self.label_hover_enter)
        slider_label.bind('<Leave>', self.label_hover_leave)
        check_function = lambda s: len(s) > 0 and s.count('.') <= 1 and s != '.' and float(s) >= self.min and float(s) <= self.max
        self.label = EditLabel(self, self.get_value_text(), fg=text_color, bg=bg, hover_bg=brighten(bg, 0.02),
                               callback=lambda s: self.set_value(self.round_value(float(s)), callback=True),
                               check_function=check_function, allowed_chars='0123456789.', editable=self.active,
                               justify='center', font_name=font_name, font_size=val_font_size)
        self.label.pack(side='bottom', fill='x')
        self.canvas = Canvas(self, bg=bg, height=self.height, width=self.slider_width, highlightthickness=0)
        self.canvas.pack(side='top')
        self.canvas.bind('<Enter>', self.hover_enter)
        self.canvas.bind('<Leave>', self.hover_leave)
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<ButtonRelease-1>', self.release)
    
        self.line_id = self.canvas.create_line(self.slider_width / 2, self.slider_height / 2, self.slider_width / 2,
                                                self.height - self.slider_height / 2, fill=self.line_colors[0],
                                                width=line_width, state='disabled')
        self.slider_id = self.canvas.create_rectangle(*self.get_slider_coords(), fill=self.slider_colors[0], width=0, state='normal')
        self.canvas.tag_bind(self.slider_id, '<Enter>', self.slider_hover_enter)
        self.canvas.tag_bind(self.slider_id, '<Leave>', self.slider_hover_leave)

    def get_slider_coords(self):
        '''returns x0, y0, x1, and y1 for slider based on self.current_value'''
        perc = (self.current_value - self.min) / (self.max - self.min)
        y_center = self.slider_height / 2 + (self.height - self.slider_height) * (1 - perc)
        return 0, y_center - self.slider_height / 2, self.slider_width, y_center + self.slider_height / 2

    def get_cursor_value(self, x, y):
        '''returns current_value based on x, y'''
        perc = (self.height - y - self.slider_height / 2) / (self.height - self.slider_height)
        value = self.min + (self.max - self.min) * perc
        return self.values[np.absolute(self.values - value).argmin()]

class SimpleScrollBar(Canvas):
    ''' Slider that handles integer values between a specified minimum and
        maximum value
        
        Callback command is called whenever slider value is changed by user
    '''
    def __init__(self, frame, command, min_value=0, max_value=100, start_value=0,
                 padx=0.04, pady=5, radius=10, error_margin=0.015, font_size=8,
                 val_label=False, limit_labels=False, bg='#000000', pack_side='top',
                 active_color='#13ce12', inactive_color='#888888', dot_color='#ffffff',
                 text_color='#888888', drag_color='#ffffff', time_mode=False, mouse_wheel=False,
                 val_label_font_name='Segoe UI bold', val_label_font_size=14,
                 limit_label_font_name='Segoe UI', limit_label_font_size=12,
                 value_display_fact=1):
        '''basic scroll bar to play videos, set parameters, etc
        
        Parameters
        ----------
            :param frame: tk.Frame - parent widget
            :param command: function (value) - functions called whenever scrollbar value is changed
            :param min_value: int - minimum value for slider
            :param max_value: int - maximum value for slider
            :param padx: float - x pad as a percentage of widget width
            :param pady: int - y pad in pixels
            :param radius: int - radius of draggable circle in pixels
            :param font_size: int - size of min/max value labels, if there are any
            :param bg: str (hex code) - slider background color
            :param active_color: str (hex code) - color for active portion of slider on hover
            :param inactive_color: str (hex code) - color for inactive portion of slider when cursor is not hovering
            :param dot_color: str (hex code) - color for inactive portion when not hovering and dot when hovering
            :param text_color: str (hex code) - color of text
            :param error_margin: float - cursor will be considered on the slider if it is within (error_margin * plot width) of slider position
            :param mouse_wheel: bool - make scrollbar scrollable using mouse wheel
            :param value_display_fact: float - values are multiplied by this fact only when being displayed
                                             - this does not affect the callback function
        '''
        self.command = command
        self.min, self.max = min_value, max_value
        self.padx, self.pady = padx, pady
        self.r = radius
        self.error_margin = error_margin
        self.font_size = font_size
        self.val_label, self.limit_labels = val_label, limit_labels
        self.val_label_font_name, self.val_label_font_size = val_label_font_name, val_label_font_size
        self.limit_label_font_name, self.limit_label_font_size = limit_label_font_name, limit_label_font_size
        self.inactive_color = inactive_color
        self.line_colors = [dot_color, active_color]
        self.circle_colors = [dot_color, drag_color]
        self.text_color = text_color
        self.line_id, self.active_line_id, self.circle_id, self.label_id, self.min_label_id, self.max_label_id, self.width = [None] * 7
        self.dragging, self.hovering = [False] * 2
        self.time_mode = time_mode
        self.active = True
        self.circle_states = ['hidden', 'normal']
        self.current_value = start_value
        self.line_height = self.pady + self.r
        self.value_display_fact = value_display_fact

        super().__init__(frame, height=(self.pady + self.r) * 2 + 22 * self.val_label,
                         bg=bg, highlightthickness=0)
        self.pack(side=pack_side, fill='x')
        self.bind("<Button-1>", lambda e: self.toggle_circle(e, True))
        self.bind("<ButtonRelease-1>", lambda e: self.toggle_circle(e, False))
        self.bind("<B1-Motion>", self.drag_move)
        self.bind("<Enter>", lambda e: self.update_hover(True))
        self.bind("<Leave>", lambda e: self.update_hover(False))
        self.bind('<Configure>', self.frame_width)
        if mouse_wheel:
            self.bind('<MouseWheel>', self.mouse_wheel_scroll)
        self.event_generate('<Configure>', when='tail')

    def frame_width(self, event):
        '''called whenever window is resized'''
        self.width = event.width
        self.update_width()
        self.draw()

    def format_text(self, val:int) -> str:
        '''takes as input either self.max or self.current_value
        returns str according to self.time_mode'''
        val = int(round(val * self.value_display_fact, 0))
        if self.time_mode:
           return seconds_text(val)
        else:
            return str(val)
    
    def update_width(self):
        '''called after self.width is updated'''
        self.xmin = self.width * self.padx + 10 * len(self.format_text(self.max)) * self.limit_labels
        self.xmax = self.width * (1 - self.padx) - 10 * len(self.format_text(self.max)) * self.limit_labels

    def set_limits(self, min_value:int, max_value:int):
        if min_value != self.min or max_value != self.max:
            self.min, self.max = min_value, max_value
            self.current_value = min(self.max, max(self.min, self.current_value))
            self.draw()

    def set_value(self, value:int, call_command=False):
        '''moves circle and calls command if value if different from self.current_value'''
        if self.current_value != value:
            self.current_value = value
            x_pos = self.xmin + (self.xmax - self.xmin) * (self.current_value - self.min) / (self.max - self.min)
            self.coords(self.active_line_id, self.xmin, self.line_height, x_pos, self.line_height)
            self.coords(self.circle_id, x_pos - self.r, self.line_height - self.r, x_pos + self.r, self.line_height + self.r)
            if self.val_label:
                self.itemconfig(self.label_id, text=self.format_text(self.current_value))
            if self.limit_labels:
                self.itemconfig(self.min_label_id, text=self.format_text(self.current_value))
            if call_command:
                self.command(self.current_value)

    def set_frame(self, value:int):
        '''
        doubles self.set_value - necessary because this was designed stupidly
        does not call callback command
        '''
        self.set_value(value, call_command=False)

    def set_frame_num(self, max_value:int, frame_rate):
        '''for consistency with PlotScrollbar'''
        self.set_limits(0, max_value)

    def turn_on(self, override=True):
        '''
        makes slider interactable by user
        if override is True, will turn on even if already on
        '''
        if override or not self.active:
            self.active = True
            self.itemconfig(self.circle_id, fill=self.inactive_color)
            if self.val_label:
                self.itemconfig(self.label_id, fill='#ffffff')

    def turn_off(self, override=True):
        '''
        makes slider uninteractable by user
        if override is True, will turn off even if already off
        '''
        if override or self.active:
            self.active = False
            self.itemconfig(self.circle_id, fill=brighten(self.inactive_color, -0.4))
            if self.val_label:
                self.itemconfig(self.label_id, fill=brighten(self.inactive_color, -0.4))

    def remove(self):
        '''removes everything from the canvas'''
        if self.line_id is not None:
            self.delete(self.line_id)
            self.line_id = None
        if self.active_line_id is not None:
            self.delete(self.active_line_id)
            self.active_line_id = None
        if self.circle_id is not None:
            self.delete(self.circle_id)
            self.circle_id = None
        if self.label_id is not None:
            self.delete(self.label_id)
            self.label_id = None
        if self.min_label_id is not None:
            self.delete(self.min_label_id)
            self.min_label_id = None
        if self.max_label_id is not None:
            self.delete(self.max_label_id)
            self.max_label_id = None

    def draw(self):
        '''called when window is resized - redraws canvas according to new size'''
        if not self.width:
            return None
        self.remove()
        self.line_id = self.create_line(self.xmin, self.line_height, self.xmax, self.line_height,
                                                fill=brighten(self.inactive_color, -0.4), width=2)
        x_pos = self.xmin + (self.xmax - self.xmin) * (self.current_value - self.min) / (self.max - self.min)
        self.active_line_id = self.create_line(self.xmin, self.line_height, x_pos, self.line_height, fill=self.line_colors[0], width=2)
        self.circle_id = self.create_oval(x_pos - self.r, self.line_height - self.r, x_pos + self.r, self.line_height + self.r,
                                                    fill=self.circle_colors[0], state='hidden')
        if self.val_label:
            self.label_id = self.create_text(self.width / 2, self.pady + self.r * 2 - 1, text=str(self.current_value), fill='#ffffff',
                                                        font=(self.val_label_font_name, self.val_label_font_size), anchor='n')
        if self.limit_labels:
            self.min_label_id = self.create_text(self.xmin - self.r - 2, self.line_height, text=self.format_text(self.current_value),
                                                        fill=self.inactive_color, font=(self.limit_label_font_name, self.limit_label_font_size),
                                                        anchor='e')
            self.max_label_id = self.create_text(self.xmax + self.r + 2, self.line_height, text=self.format_text(self.max),
                                                        fill=self.inactive_color, font=(self.limit_label_font_name, self.limit_label_font_size),
                                                        anchor='w')
        if not self.active:
            self.turn_off()

    def update_hover(self, hover:bool):
        '''called when cursor enters or leaves line'''
        if self.active:
            self.hovering = hover
            self.itemconfig(self.active_line_id, fill=self.line_colors[self.hovering or self.dragging])
            self.itemconfig(self.circle_id, state=self.circle_states[self.hovering or self.dragging])

    def toggle_circle(self, event, onclick:bool):
        '''mouse clicks or releases click anywhere on canvas'''
        if self.active:
            self.dragging = onclick
            self.itemconfig(self.circle_id, fill=self.circle_colors[self.dragging])
            self.drag_move(event)
            if not self.dragging and not self.hovering:
                self.update_hover(False)

    def drag_move(self, event):
        '''called when mouse drags slider'''
        if self.active:
            x_perc = (event.x - self.xmin) / (self.xmax - self.xmin)
            value = self.min + (self.max- self.min) * x_perc
            self.set_value(int(round(min(self.max, max(self.min, value)), 0)), call_command=True)

    def mouse_wheel_scroll(self, event, fact=1):
        '''called when mouse wheel is scrolled while mouse hovers on slider'''
        # event.delta / 120 is float - number of scroll steps - positive for up, negative for down
        if self.active:
            value = self.current_value + event.delta / 120 * fact
            self.set_value(int(min(self.max, max(self.min, value))), call_command=True)

class VerticalSliderGroup(Frame):
    ''' Group of vertically oriented sliders connected by a single callback
        function
        
        The callback function is called whenever any of the slider values is
        changed by the user and is given 2 arguments: (slider_label, new_value)
    '''
    def __init__(self, master, parameters:list, callback, bg:str, rows:int,
                 columns:int, height=250, slider_pady=5, slider_padx=5,
                 slider_ac='#13ce12', slider_ic='#ffffff', line_ac='#999999',
                 line_ic='#888888', text_color='#888888', font_name='Segoe UI',
                 label_font_size=14, val_font_size=11, slider_height=20,
                 slider_width=35, line_width=10, title_label=True):
        '''Group of vertical sliders aranged in rows and columns
        
        Parameters
        ----------
            :param master: tk.Frame - frame in which to put slider group
            :param parameters: list of dicts - each dict contains the keys:
                        label: str - slider name (given to callback function)
                        value: float - default value
                        min_value: float - minimum value
                        max_value: float - maximum value
                        step: float - slider increment
                        description: str - info displayed when mouse hovers on slider
            :param callback: function (parameter_name, value) - called whenever a slider is adjusted
            :param bg: str (hex code) - background color
            :param rows: int - rows of sliders - filling begins rowwise at top left
            :param columns: int - columns of sliders - filling begins rowwise at top left
            :param height: int - height of each slider in pixels
            :param pady: int - y pad inside each slider
            :param slider_ac: str (hex code) - color of slider when mouse button is depressed
            :param slider_ic: str (hex code) - color of slider when mouse button is not depressed
            :param line_ac: str (hex code) - color of line when mouse is on Canvas
            :param line_ic: str (hex code) - color of line when mouse is not on Canvas
            :param text_color: str (hex code) - color of text
            :param title_label: bool - if True display 'fade_in' as 'Fade In'
        '''
        Frame.__init__(self, master, bg=bg)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        for i in range(columns):
            self.grid_columnconfigure(i, weight=1)
        self.sliders = []
        for i, param in enumerate(parameters):
            S = VerticalSlider(self, param['label'], lambda x, l=param['label']: callback(l, x),
                               bg, param['min_value'], param['max_value'],
                               param['step'], start_value=param['value'],
                               popup_label=param['description'], padx=slider_padx,
                               pady=slider_pady, height=height, slider_ac=slider_ac,
                               slider_ic=slider_ic, line_ac=line_ac, line_ic=line_ic,
                               text_color=text_color, font_name=font_name,
                               label_font_size=label_font_size, val_font_size=val_font_size,
                               slider_height=slider_height, slider_width=slider_width,
                               line_width=line_width, title_label=title_label)
            S.grid(row=i // columns, column=i % columns, sticky='nsew')
            self.sliders.append(S)

class HorizontalSliderGroup(Frame):
    ''' Group of horizontally oriented sliders connected by a single callback
        function
        
        The callback function is called whenever any of the slider values is
        changed by the user and is given 2 arguments: (slider_label, new_value)
    '''
    def __init__(self, master, parameters:list, callback, bg:str,
                 width=250, slider_pady=5, slider_padx=5,
                 slider_ac='#13ce12', slider_ic='#ffffff', line_ac='#999999',
                 line_ic='#888888', text_color='#888888', font_name='Segoe UI',
                 label_font_size=14, val_font_size=11,
                 slider_height=35, slider_width=18, line_width=10, title_label=True):
        '''Group of horizontal sliders aranged in a single column
        
        Parameters
        ----------
            :param master: tk.Frame - frame in which to put slider group
            :param parameters: list of dicts - each dict contains the keys:
                        label: str - slider name (given to callback function)
                        value: float - default value
                        min_value: float - minimum value
                        max_value: float - maximum value
                        step: float - slider increment
                        description: str - info displayed when mouse hovers on slider
            :param callback: function (parameter_name, value) - called whenever a slider is adjusted
            :param bg: str (hex code) - background color
            :param width: int - width of each slider in pixels
            :param pady: int - y pad inside each slider
            :param slider_ac: str (hex code) - color of slider when mouse button is depressed
            :param slider_ic: str (hex code) - color of slider when mouse button is not depressed
            :param line_ac: str (hex code) - color of line when mouse is on Canvas
            :param line_ic: str (hex code) - color of line when mouse is not on Canvas
            :param text_color: str (hex code) - color of text
            :param title_label: bool - if True display 'fade_in' as 'Fade In'
        '''
        Frame.__init__(self, master, bg=bg)
        self.sliders = []
        for param in parameters:
            S = HorizontalSlider(self, param['label'], lambda x, l=param['label']: callback(l, x),
                                 bg, param['min_value'], param['max_value'],
                                 param['step'], start_value=param['value'],
                                 popup_label=param['description'], padx=slider_padx,
                                 pady=slider_pady, width=width, slider_ac=slider_ac,
                                 slider_ic=slider_ic, line_ac=line_ac, line_ic=line_ic,
                                 text_color=text_color, font_name=font_name,
                                 label_font_size=label_font_size, val_font_size=val_font_size,
                                 justify='right', slider_height=slider_height,
                                 slider_width=slider_width, line_width=line_width,
                                 title_label=title_label)
            S.pack(side='top')
            self.sliders.append(S)
    
class PlotScrollBar(Canvas):
    ''' Horizontally oriented plot slider that handles integer values between
        a specified minimum and maximum value
        
        Callback command is called whenever the slider is moved by the user

        Values are displayed to the user in seconds (formatted m:ss), but on the
        backend, values are given in frames. This is ideal if you are using the
        slider to control video playback
    '''
    def __init__(self, master, command, label, frames=100, min_frame=0, start_frame=1,
                 frame_rate=29.97, height=72, padx=0.04, active_color='#e8ff00',
                 inactive_color='#888888', hover_color='#ffffff',
                 active_fill_color=brighten('#00ff00', -0.75), bg='#000000',
                 show_fill=False, active_fill=False, confine_to_active_region=False,
                 fill_text='', active_x0=0, active_x1=0, mouse_wheel_steps=1,
                 active_fill_callback=None, font_name='Segoe UI', label_font_size=10,
                 tick_font_size=9, active=True):
        '''        
        Parameters
        ----------
            :param command: function (int) - called whenever slider value is changed
            :param label: str or None - x axis label display beneath slider
            :param frames: int - total number of steps in slider
            :param start_frame: int - default slider position
            :param height: int - window height in pixels
            :param mouse_wheel_steps: int - increment for each mousewheel scroll event
            :param show_fill: bool - if True, display fill of active range underneath slider - must be True to use confine_to_active_region
            :param active_fill: bool - if True and show_fill is True, fill of active range can be dragged
            :param confine_to_active_region: bool - if True, user will not be allowed to move scrollbar outside of active region
            :param fill_text: str - text displayed in fill of active range
            :param (active_x0 active_x1) : (int, int) - start and end of active range
            :param active_fill_callback: 2 argument function (active_x0, active_x1) - called whenever active region is changed
            :param active: bool - if False, scrollbar will be unresponsive to user interactions - for toggling
        '''
        Canvas.__init__(self, master, bg=bg, height=height, highlightthickness=0)
        self.command = command # function acception 1 numeric argument
        self.active_fill_callback = active_fill_callback
        self.label = label # can be none to display no label
        self.mouse_wheel_steps = mouse_wheel_steps
        self.height, self.padx = height, padx
        self.active_color, self.inactive_color, self.hover_color = active_color, inactive_color, hover_color
        self.font_name, self.label_font_size, self.tick_font_size = font_name, label_font_size, tick_font_size
        self.show_fill, self.active_fill = show_fill, active_fill
        self.confine_to_active_region = confine_to_active_region
        self.hovering, self.dragging = False, False
        self.frame_rate = frame_rate
        self.active_x0, self.active_x1 = active_x0, active_x1 # frames
        self.current_frame, self.min_frame, self.max_frame = start_frame, min_frame, frames
        self.min_seconds, self.max_seconds = self.min_frame / frame_rate, self.max_frame / frame_rate
        self.width = None
        if self.label:
            self.label_line_height, self.tick_height = height * 0.5, height * 0.59
        else:
            self.label_line_height, self.tick_height = height * 0.65, height * 0.76
        self.divisions = np.array([1/2**i for i in range(4, 0, -1)] + [1, 2, 5, 10, 25, 50, 100]) # smallest is 0.0625 (1/16)

        if self.show_fill:
            self.Fill = CanvasEditFill(self, 'sb_fill', 0, 0, 0, self.label_line_height, line_width=2, bg=active_fill_color,
                                       main_text_hover_justify='center', main_text=fill_text, selectable=False, hoverable=True,
                                       box_draggable='horizontal', left_draggable=active_fill, right_draggable=active_fill,
                                       left_drag_function=self.active_drag0, right_drag_function=self.active_drag1,
                                       box_drag_function=self.active_drag, brighten_fact=0, raise_on_click=False,
                                       active=active and self.active_fill)
        self.Line = CanvasEditLine(self, 0, 0, self.label_line_height, width=6,
                                   bg=self.inactive_color, drag_color=self.active_color,
                                   hover_color=self.hover_color, selectable=False,
                                   hoverable=True, draggable=True, deletable=False,
                                   show_drag_color=True, drag_function=self.main_drag,
                                   active=active)

        self.bind('<Configure>', self.frame_width)
        self.bind('<MouseWheel>', self.mouse_wheel_scroll)
        self.event_generate('<Configure>', when='tail')

    def frame_width(self, event):
        '''called whenever window is resized'''
        self.width = event.width
        self.xmin = self.width * self.padx
        self.xmax = self.width * (1 - self.padx)
        self.draw()

    def get_status(self):
        '''returns current_frame, min_frame, and max_frame'''
        return self.current_frame, self.min_frame, self.max_frame
    
    def get_current_frame(self):
        '''returns current frame of ScrollBar'''
        return self.current_frame

    def set_frame_num(self, max_frame:int, frame_rate:float, min_frame:int=0):
        '''update the frame bounds and frame rate'''
        self.frame_rate = frame_rate
        self.min_frame, self.max_frame = min_frame, max_frame
        self.min_seconds, self.max_seconds = self.min_frame / self.frame_rate, self.max_frame / self.frame_rate
        self.update_active_region()
        self.draw()

    def set_frame(self, frame:int):
        '''set the slider position'''
        self.current_frame = frame
        self.update_line_x()

    def set_active(self):
        '''sets state to active so that scrollbar will be responsive to user interactions'''
        self.Line.set_active()
        if self.show_fill and self.active_fill: # if fill is set to be uninteractable, Fill will remain inactive
            self.Fill.set_active()

    def set_inactive(self):
        '''sets state to inactive so that scrollbar will be unresponsive to user interactions'''
        self.Line.set_inactive()
        if self.show_fill:
            self.Fill.set_inactive()

    def update_active_fill(self, start_frame:int, end_frame:int):
        '''configure active region'''
        # could throw error if new active region extends beyond scrollbar limits (self.min_frame to self.max_frame)
        if not self.show_fill:
            # raise error
            return
        self.active_x0, self.active_x1 = start_frame, end_frame
        self.update_fill_x()
            
    def get_frame_x(self, frame:int) -> float:
        '''returns the x coordinate corresponding to the given frame'''
        if self.max_frame - self.min_frame == 0:
            return self.xmin
        return self.xmin + (self.xmax - self.xmin) * (frame - self.min_frame) / (self.max_frame - self.min_frame)
    
    def x_coord_to_frame(self, x:float) -> int:
        '''converts x coordinate to frame - returns int'''
        x_perc = (x - self.xmin) / (self.xmax - self.xmin)
        frame = int(self.min_frame + (self.max_frame - self.min_frame) * x_perc)
        return min(self.max_frame, max(self.min_frame + 1, frame))
            
    def update_line_x(self):
        '''updates line based on self.current_frame and moves active region if necessary'''
        self.Line.set_x(self.get_frame_x(self.current_frame))
        self.update_active_region()

    def update_fill_x(self, callback=True):
        '''updates fill position based on self.active_x0 and self.active_x1'''
        if self.show_fill and self.width: # dont actually do changes if scrollbar has not been drawn yet
            self.Fill.set_x_coords(self.get_frame_x(self.active_x0), self.get_frame_x(self.active_x1))
        if callback and self.active_fill_callback:
            self.active_fill_callback(self.active_x0, self.active_x1)

    def squeeze_active_bounds(self, active_x0:int, active_x1:int):
        '''
        Purpose
        -------
            adjusts active_x0 and active_x1 if necessary based on the following conditions
                active_x0 must be >= self.min_frame
                active_x0 must be < self.current_frame
                active_x1 must be <= self.max_frame
                active_x1 must be > self.current_frame
            distance between active_x0 and active_x1 will remain the same
                
        Parameters
        ----------
            active_x0 : int - left edge of active region before adjustment
            active_x1 : int - right edge of active region before adjustment
            
        Returns
        -------
            active_x0 : int - left edge of active region after adjustment
            active_x1 : int - right edge of active region after adjustment
        '''
        width = max(2, min(self.max_frame - self.min_frame, active_x1 - active_x0))
        x0, x1 = active_x0, active_x0 + width
        if x0 < self.min_frame:
            add = self.min_frame - x0
            x0 += add
            x1 += add
        elif x0 > self.current_frame - 1:
            sub = x0 - (self.current_frame - 1)
            x0 -= sub
            x1 -= sub
        elif x1 < self.current_frame + 1:
            add = self.current_frame + 1 - x1
            x0 += add
            x1 += add
        elif x1 > self.max_frame:
            sub = x1 - self.max_frame
            x0 -= sub
            x1 -= sub
        return x0, x1

    def update_active_region(self):
        '''updates active region if it does not include self.current_frame
        to be called when main line is moved
        other rules may be set to stop the main line from being at the very edge of active region
        '''
        if self.show_fill:
            if self.active_x0 in range(self.min_frame, self.current_frame) and self.active_x1 in range(self.current_frame + 1, self.max_frame + 1):
                return # active bounds are both within allowed range
            self.active_x0, self.active_x1 = self.squeeze_active_bounds(self.active_x0, self.active_x1)
            self.update_fill_x()

    def main_drag(self, current_x:float, cursor_x:float):
        '''called whenever main line is dragged
        move main line and squeeze inside bounds if necessary
        
        Parameters
        ----------
            current_x : float - position of line before drag
            cursor_x : float - cursor position - potential new line position
        
        Returns
        -------
            new_x : float - new position for line
        '''
        frame = self.x_coord_to_frame(cursor_x)
        if self.confine_to_active_region: # do not allow user to move scrollbar outside of active region
            frame = min(self.active_x1 - 1, max(self.active_x0 + 1, frame))
        if frame != self.current_frame:
            self.current_frame = frame
            self.command(self.current_frame - 1)
            self.update_active_region()
        return self.get_frame_x(self.current_frame) # to update line position
    
    def active_drag(self, x0:float, x1:float, cursor_x:float, new_x0:float, new_x1:float):
        '''called whenever the active fill is dragged
        moves active region - cannot exclude main line (current frame)
        
        Parameters
        ----------
            x0 : float - position of left edge of fill before drag
            x1 : float - position of right edge of fill before drag
            cursor_x : float - cursor position
            new_x0 : float - potential new left edge based on cursor movement
            new_x1 : float - potential new right edge based on cursor movement
        
        Returns
        -------
            new_x0 : float - new position of left edge of fill
            new_x1 : float - new position of right edge of fill
        '''
        active_x0, active_x1 = self.x_coord_to_frame(new_x0), self.x_coord_to_frame(new_x1)
        active_x0, active_x1 = self.squeeze_active_bounds(active_x0, active_x1)
        if active_x0 != self.active_x0 and active_x1 != self.active_x1: # width of active region must not change
            self.active_x0, self.active_x1 = active_x0, active_x1
            if self.active_fill_callback:
                self.active_fill_callback(self.active_x0, self.active_x1)
        return self.get_frame_x(self.active_x0), self.get_frame_x(self.active_x1)

    def active_drag0(self, current_x0:float, current_x1:float, cursor_x:float):
        '''called whenever the left active line is dragged
        moves active region - cannot exclude main line (current frame)
        
        Parameters
        ----------
            current_x0 : float - position of left edge before drag
            current_x1 : float - position of right edge before drag
            cursor_x : float - cursor position - potential new left edge position
        
        Returns
        -------
            new_x : float - new position for line
        '''
        frame = min(self.current_frame - 1, max(self.min_frame, self.x_coord_to_frame(cursor_x))) # cannot be >= than current frame
        if frame != self.active_x0:
            self.active_x0 = frame
            if self.active_fill_callback:
                self.active_fill_callback(self.active_x0, self.active_x1)
        return self.get_frame_x(self.active_x0) # to update fill position
    
    def active_drag1(self, current_x0:float, current_x1:float, cursor_x:float):
        '''called whenever the right active line is dragged
        moves active region - cannot exclude main line (current frame)
        
        Parameters
        ----------
            current_x0 : float - position of left edge before drag
            current_x1 : float - position of right edge before drag
            cursor_x : float - cursor position - potential new right edge position
        
        Returns
        -------
            new_x : float - new position for line
        '''
        frame = min(self.max_frame, max(self.current_frame + 1, self.x_coord_to_frame(cursor_x))) # cannot be <= than current frame
        if frame != self.active_x1:
            self.active_x1 = frame
            if self.active_fill_callback:
                self.active_fill_callback(self.active_x0, self.active_x1)
        return self.get_frame_x(self.active_x1) # to update fill position

    def increment_frame(self, increment, loop=False, callback=True):
        '''returns False if the end has been reached or no effect is loaded, otherwise True
        calls callback with new frame'''
        if loop and self.current_frame == self.min_frame + 1 and increment == -1: # reached the beginning when going backward with loop
            self.current_frame = self.max_frame - 1
        if self.current_frame == self.max_frame and increment >= 0: # reached end
            if loop: # loop back to start
                self.current_frame = self.min_frame + 1
                self.update_line_x() # based on self.current_frame
                if callback:
                    self.command(self.current_frame - 1)
                return True
            else: # end
                return False
        self.current_frame = int(min(self.max_frame, max(self.min_frame + 1, self.current_frame + increment)))
        self.update_line_x()
        if callback:
            self.command(self.current_frame - 1)
        return True

    def mouse_wheel_scroll(self, event):
        '''event.delta / 120 is float - number of scroll steps - positive for up, negative for down'''
        frame = min(self.max_frame, max(self.min_frame + 1, int(self.current_frame + event.delta / 120 * self.mouse_wheel_steps)))
        if self.confine_to_active_region: # do not allow user to move scrollbar outside of active region
            frame = min(self.active_x1 - 1, max(self.active_x0 + 1, frame))
        self.set_frame(frame)
        self.command(self.current_frame - 1)

    def remove(self):
        '''removes all labels and ticks from the x axis'''
        # deletes everything except line and active fill
        for i in self.find_all():
            if i != self.Line.id and (not self.show_fill or i != self.Fill.box_id):
                self.delete(i)

    def draw(self, max_ticks=15, tick_x_buffer=0.01):
        '''draws label line and ticks/labels on canvas
        updates position of main scroll line and active region fill'''
        if not self.width:
            # width will not be set for sliders on subsequent pages that have not be loaded yet
            return None
        self.remove()
        self.update_line_x()
        self.update_fill_x(callback=False)
        self.create_line(self.xmin, self.label_line_height, self.xmax,
                         self.label_line_height, fill='#ffffff', width=1)
        if self.label != None:
            self.create_text(self.width / 2, self.height, text=self.label,
                             fill='#ffffff', font=(self.font_name, self.label_font_size),
                             anchor='s')
        
        # draw ticks and labels
        increment = self.divisions[self.divisions > (self.max_seconds - self.min_seconds) / max_ticks].min()
        ticks = np.arange(int(self.min_seconds / increment), int(self.max_seconds / increment) + 1) * increment # in seconds
        for sec, label in zip(ticks, [seconds_text(t) for t in ticks]):
            x = self.xmin + (self.xmax - self.xmin) * (sec - self.min_seconds) / (self.max_seconds - self.min_seconds)
            if x + (self.xmax - self.xmin) * tick_x_buffer >= self.xmin and x - (self.xmax - self.xmin) * tick_x_buffer <= self.xmax:
                self.create_line(x, self.label_line_height, x, self.tick_height,
                                 fill='#ffffff', width=1)
                self.create_text(x, self.tick_height, text=label, fill='#ffffff',
                                 font=(self.font_name, self.tick_font_size), anchor='n')

class DoubleScrollBar(Frame):
    ''' Extension of PlotScrollBar that combines to PlotScrollBars to give user
        more precise control
        
        The top scrollbar displays an adjustable active region, which defines
        the bounds of the bottom scrollbar. User can use the bottom scrollbar
        to seek within the active region.

        Just like PlotScrollBar, there is a single callback command that is
        called whenever the slider value is changed, either by the top or bottom
        PlotScrollBar
    '''
    def __init__(self, master, command, label, frames=100, min_frame=0, start_frame=1,
                 frame_rate=29.97, main_height=60, secondary_height=60, padx=0.04,
                 active_color='#e8ff00', inactive_color='#888888',
                 hover_color='#ffffff', bg='#000000', active_fill_color='#005500',
                 fill_text='', mouse_wheel_steps=1, secondary_width_perc=0.2,
                 font_name='Segoe UI', label_font_size=10, tick_font_size=9,
                 confine_to_active_region=False, active_fill=True, active=True):
        '''Double version of PlotScrollBar - main scrollbar on top and secondary scrollbar beneath for precise seeking
        top scrollbar has interactable fill to control the bounds of bottom scrollbar
        
        Parameters
        ----------
            :param command: 1 argument function (int) - called whenever slider value is changed
            :param label: str or None - x axis label display beneath bottom slider
            :param frames: int - total number of steps in slider
            :param start_frame: int - default slider position
            :param height: int - window height in pixels
            :param mouse_wheel_steps: int - increment for each mousewheel scroll event
            :param fill_text: str - text displayed in fill of active range
            :param secondary_width_perc: float between 0 and 1 - range of secondary scrollbar as a fraction of main scrollbar range
            :param confine_to_active_region: bool - if True, user will not be allowed to move scrollbar outside of active region
            :param active_fill: bool - if True, active region of MainScrollBar can be adjusted by user
            :param active: bool - if False, scrollbar will be unresponsive to user interactions - for toggling
        '''
        Frame.__init__(self, master, bg=bg)
        self.command = command
        self.secondary_width_perc = secondary_width_perc
        self.frame_rate = frame_rate

        active_x0, active_x1 = self.get_active_bounds(start_frame, min_frame, frames, self.secondary_width_perc)   
        fill_callback = lambda f0, f1: self.SecondaryScrollBar.set_frame_num(f1, self.frame_rate, min_frame=f0 + 1)     
        self.MainScrollBar = PlotScrollBar(self, self.__main_command, None,
                                           frames=frames, min_frame=min_frame,
                                           start_frame=start_frame, height=main_height,
                                           padx=padx, active_color=active_color,
                                           inactive_color=inactive_color,
                                           hover_color=hover_color,
                                           active_fill_color=active_fill_color,
                                           bg=bg, show_fill=True, active_fill=active_fill,
                                           fill_text=fill_text, active_x0=active_x0,
                                           active_x1=active_x1, mouse_wheel_steps=mouse_wheel_steps,
                                           font_name=font_name, label_font_size=label_font_size,
                                           tick_font_size=tick_font_size, active=active,
                                           confine_to_active_region=confine_to_active_region,
                                           active_fill_callback=fill_callback,
                                           frame_rate=self.frame_rate)
        self.SecondaryScrollBar = PlotScrollBar(self, self.__secondary_command,
                                                label, frames=self.MainScrollBar.active_x1,
                                                min_frame=self.MainScrollBar.active_x0,
                                                start_frame=start_frame,
                                                height=secondary_height, padx=padx,
                                                active_color=active_color, inactive_color=inactive_color,
                                                hover_color=hover_color, active_fill_color=active_fill_color, bg=bg,
                                                show_fill=False, active_fill=False,
                                                mouse_wheel_steps=mouse_wheel_steps,
                                                font_name=font_name, label_font_size=label_font_size,
                                                tick_font_size=tick_font_size, active=active,
                                                frame_rate=self.frame_rate)
        self.MainScrollBar.pack(side='top', fill='x')
        self.SecondaryScrollBar.pack(side='top', fill='x')

    def get_active_bounds(self, start_frame:int, min_frame:int, max_frame:int, width_perc:float):
        '''returns bounds of active region based
        
        Parameters
        ----------
            :param start_frame: int - current frame of slider
            :param min_frame: int - minimum frame - left edge of scrollbar
            :param max_frame: int - maximum frame - right edge of scrollbar
            :param width_perc: float between 0 and 1 - range of secondary scrollbar as a fraction of main scrollbar range
            
        Returns
        -------
            :return x0: int - left edge of active region
            :return x1: int - right edge of active region
        '''
        pad = (max_frame - min_frame) * width_perc / 2
        x0, x1 = start_frame - pad, start_frame + pad
        if x0 < min_frame:
            x0, x1 = min_frame, x1 + min_frame - x0
        if x1 > max_frame:
            x0, x1 = x0 - (x1 - max_frame), max_frame
        return int(x0), int(x1)
        
    def __main_command(self, frame:int):
        '''called internally when main scrollbar is moved by user'''
        self.SecondaryScrollBar.set_frame(frame)
        self.command(frame)

    def __secondary_command(self, frame:int):
        '''called internally when secondary scrollbar is moved by user'''
        self.MainScrollBar.set_frame(frame)
        self.command(frame)

    def set_frame_num(self, max_frame:int, frame_rate:float, min_frame:int=0):
        '''updates the min/max frame and frame rate'''
        self.MainScrollBar.set_frame_num(max_frame, frame_rate, min_frame=min_frame)
        self.MainScrollBar.update_active_fill(*self.get_active_bounds(*self.MainScrollBar.get_status(), self.secondary_width_perc))

    def set_frame(self, frame):
        '''set current frame - pushes to both scrollbars'''
        # this will update active region if necessary and propogate to SecondaryScrollBar
        self.MainScrollBar.set_frame(frame)
        self.SecondaryScrollBar.set_frame(frame)

    def set_active(self):
        '''sets state to active so that scrollbar will be responsive to user interactions'''
        self.MainScrollBar.set_active()
        self.SecondaryScrollBar.set_active()

    def set_inactive(self):
        '''sets state to inactive so that scrollbar will be unresponsive to user interactions'''
        self.MainScrollBar.set_inactive()
        self.SecondaryScrollBar.set_inactive()

    def get_current_frame(self):
        '''returns current frame of ScrollBar'''
        return self.MainScrollBar.get_current_frame()

    def update_active_fill(self, start_frame:int, end_frame:int):
        '''
        update region that can be scrolled by the bottom scrollbar
        this is the region displayed as active in the top scrollbar
        '''
        self.MainScrollBar.update_active_fill(start_frame, end_frame)

    def increment_frame(self, increment, loop=False, callback=True):
        '''returns False if the end has been reached or no effect is loaded, otherwise True
        calls callback with new frame'''
        current_frame, min_frame, max_frame = self.MainScrollBar.get_status()
        if current_frame + increment <= min_frame and increment < 0 and loop: # reached the beginning when going backward with loop
            new_frame = max_frame - 1
        elif current_frame + increment >= max_frame and increment > 0 and loop: # reached end with loop (going forward)
            new_frame = min_frame + 1
        else:
            new_frame = current_frame + increment

        set_frame = int(min(max_frame, max(min_frame + 1, new_frame)))
        self.set_frame(set_frame)
        if callback:
            self.command(set_frame - 1)
        return new_frame in range(min_frame, max_frame + 1)

