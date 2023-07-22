from tkinter import Canvas, Frame, Label

import numpy as np

from .tool_tip import ToolTip
from .labels import NumberEditLabel
from .canvas_items import CanvasEditLine, CanvasEditFill, brighten

__all__ = ['Slider', 'TimeSlider', 'HorizontalSlider', 'VerticalSlider', 'ScrollBar',
           'HorizontalSliderGroup', 'VerticalSliderGroup', 'PlotScrollBar', 'DoubleScrollBar', 'brighten']

# helper functions
def seconds_text(sec:float):
    '''converts seconds to text in form (hh):(m)m:ss'''
    sec = int(sec)
    if sec >= 3600: # at least one hour
        return f'{sec // 3600}:{(sec % 3600) // 60:0>2}:{(sec % 60) // 1:0>2}'
    else: # less than one hour
        return f'{sec // 60}:{(sec % 60) // 1:0>2}'


class Slider(Canvas):
    ''' Basic slider that takes values between 0 and 1

        Can be configured horizontally or vertically with circle or rectangle
        slider.
    '''
    def __init__(self, master:Frame, callback=None, default_value=0, bg='#000000',
                 line_color='#555555', active_line_color=None, active_line_hover_color=None,
                 slider_color='#ffffff', slider_drag_color=None, hide_slider=False,
                 slider_visible=True, slider_height=20, slider_width=20, slider_type='circle',
                 orientation='h', line_width=2, height=0, width=0, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param callback: function (float) - called only when slider is moved by user
            :param default_value: float between 0 and 1 - initial slider value
            :param bg: str (hex code) - background color
            :param line_color: str (hex code) - color of line
            :param active_line_color: str (hex code) - color of active portion of line (if different from line_color)
            :param active_line_hover_color: str (hex code) - color of active portion of line when hovering
                                                           - if different from active_line_color
            :param slider_color: str (hex code) - slider color
            :param slider_drag_color: str (hex code) - slider color when mouse is depressed (if different from slider color)
            :param hide_slider: bool - if True, slider is hidden when cursor is not hovering
            :param slider_visible: bool - if False, slider is never visible
            :param slider_height: int - height of slider in pixels (or diameter for circle slider)
            :param slider_width: int - width of slider in pixels
            :param slider_type: Literal['circle', 'rectangle'] - type of slider
            :param orientation: Literal['h', 'v'] - horizontal or vertical orientation
            :param line_width: int - width of slider line in pixels
            :param height: int - canvas height in pixels
            :param width: int - canvas width in pixels
        '''
        assert slider_type in ['circle', 'rectangle'], f'Slider Error: Invalid slider type: {slider_type}'
        assert orientation in ['h', 'v'], f'Slider Error: Invalid orientation: {orientation}'
        assert default_value >= 0 and default_value <= 1, f'Default value must be between 0 and 1, not {default_value}'
        if slider_type == 'circle' and slider_height != slider_width: # not a circle (not fatal)
            print(f'Slider Warning: Initiated circle slider but slider height ({slider_height}) does not equal slider width ({slider_width})')
        canvas_height = slider_height if orientation == 'h' else height
        canvas_width = slider_width if orientation == 'v' else width
        super().__init__(master, bg=bg, highlightthickness=0,
                         height=canvas_height, width=canvas_width, **kwargs)
        self.__value = default_value
        self.__callback = callback
        self.__orientation = orientation
        self.__slider_type = slider_type
        self.__slider_height, self.__slider_width = slider_height, slider_width
        self.__active_line_color = active_line_color if active_line_color is not None else line_color
        self.__hover_line_color = active_line_hover_color if active_line_hover_color is not None else self.__active_line_color
        self.__slider_color = slider_color if slider_color is not None else self.__active_line_color
        self.__slider_drag_color = slider_drag_color if slider_drag_color is not None else self.__slider_color
        self.__slider_state = 'hidden' if hide_slider or not slider_visible else 'disabled' # when not hovering
        self.__slider_hover_state = 'disabled' if slider_visible else 'hidden' # when hovering
        self.__dragging = False

        # Draw Lines and Slider
        self.__line_id = self.create_line(0, 0, 0, 0, fill=line_color,
                                          width=line_width, state='disabled')
        self.__active_line_id = self.create_line(0, 0, 0, 0, fill=self.__active_line_color,
                                                 width=line_width, state='disabled')
        if self.__slider_type == 'circle':
            self.__slider_id = self.create_oval(0, 0, 0, 0, fill=self.__slider_color,
                                                state=self.__slider_state)
        elif self.__slider_type == 'rectangle':
            self.__slider_id = self.create_rectangle(0, 0, 0, 0, fill=self.__slider_color,
                                                     width=0, state=self.__slider_state)
            
        # Event Bindings
        self.bind("<Button-1>", self.__click)
        self.bind("<ButtonRelease-1>", self.__release)
        self.bind("<B1-Motion>", self.__motion)
        self.bind("<Enter>", self.__hover_enter)
        self.bind("<Leave>", self.__hover_leave)
        self.bind('<Configure>', self.__set_coords)
        
        self.event_generate('<Configure>', when='tail')

    def __set_coords(self, event=None):
        '''updates coordinates of lines and slider based on canvas size and current value'''
        h, w = self.winfo_height(), self.winfo_width()
        rx, ry = self.__slider_width / 2, self.__slider_height / 2
        if self.__orientation == 'h': # horizontal
            x = (w - self.__slider_width) * self.__value + rx
            y = h / 2
            self.coords(self.__line_id, rx, y, w - rx, y)
            self.coords(self.__active_line_id, rx, y, x, y)
        elif self.__orientation == 'v': # vertical
            x = w / 2
            y = h - ry - (h - self.__slider_height) * self.__value
            self.coords(self.__line_id, w / 2, ry, w / 2, h - ry)
            self.coords(self.__active_line_id, x, y, x, h - ry)
        self.coords(self.__slider_id, x - rx, y - ry, x + rx, y + ry)

    def __get_value(self, x:float, y:float):
        '''computes value based on (x, y) coordinates'''
        if self.__orientation == 'h': # horizontal
            value = (x - self.__slider_width / 2) / (self.winfo_width() - self.__slider_width)
        elif self.__orientation == 'v': # vertical
            value = (self.winfo_height() - self.__slider_height / 2 - y) / (self.winfo_height() - self.__slider_height)
        return max(0, min(1, value))
    
    def __hover_enter(self, event=None):
        '''cursor enters canvas'''
        self.itemconfig(self.__active_line_id, fill=self.__hover_line_color)
        self.itemconfig(self.__slider_id, state=self.__slider_hover_state)

    def __hover_leave(self, event=None):
        '''cursor leaves canvas'''
        if not self.__dragging:
            self.itemconfig(self.__active_line_id, fill=self.__active_line_color)
            self.itemconfig(self.__slider_id, state=self.__slider_state)

    def __click(self, event):
        '''cursor clicks on canvas - move slider to click position'''
        self.__dragging = True
        self.itemconfig(self.__slider_id, fill=self.__slider_drag_color)
        self.__value = self.__get_value(event.x, event.y)
        self.__set_coords()
        if self.__callback is not None:
            self.__callback(self.__value)

    def __release(self, event):
        '''cursor releases click - change slider color to normal'''
        self.__dragging = False
        self.itemconfig(self.__slider_id, fill=self.__slider_color)
        w, h = self.winfo_width(), self.winfo_height()
        if event.x < 0 or event.x > w or event.y < 0 or event.y > h: # not hovering
            self.__hover_leave()

    def __motion(self, event):
        '''cursor drags slider'''
        self.__value = self.__get_value(event.x, event.y)
        self.__set_coords()
        if self.__callback is not None:
            self.__callback(self.__value)

    def set(self, value:float):
        '''sets slider value - must be between 0 and 1 (does not call callback function)'''
        assert value >= 0 and value <= 1, f'Slider Error: set slider to invalid value: {value}'
        self.__value = value
        self.__set_coords()

    def get(self):
        '''returns current slider value'''
        return self.__value

class TimeSlider(Frame):
    ''' Combines Slider with two labels to display a time slider.
    
        There can be multiple steps per second. The callback function is given
        the current step not the current time
    '''
    def __init__(self, master:Frame, callback=None, frame_num=100, start_frame=0,
                 steps_per_sec=1, bg='#000000', fg='#888888',
                 val_font_name='Segoe UI', limit_font_name='Segoe UI',
                 val_font_size=12, limit_font_size=12, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param callback: function (int) - called when slider is moved
            kwargs are passed to Slider (not Frame)
        '''
        super().__init__(master, bg=bg)
        self.__callback = callback
        self.__frame_num = frame_num
        self.__steps_per_sec = steps_per_sec

        # End Time Label - Right
        self.__end_label = Label(self, text=seconds_text(frame_num / steps_per_sec),
                                 bg=bg, fg=fg, font=(limit_font_name, limit_font_size))
        self.__end_label.pack(side='right')

        # Current Time Label - Left
        self.__label = Label(self, text=seconds_text(start_frame / steps_per_sec),
                             bg=bg, fg=fg, font=(val_font_name, val_font_size))
        self.__label.pack(side='left')

        # Slider - Center
        self.__Slider = Slider(self, self.__slider_callback,
                               default_value=start_frame / frame_num, bg=bg,
                               orientation='h', **kwargs)
        self.__Slider.pack(side='left', fill='x', expand=True)

    def __slider_callback(self, perc:float):
        '''called when slider is moved by user
        :param perc: float between 0 and 1 - new slider value
        '''
        frame = self.__frame_num * perc
        self.__label.config(text=seconds_text(frame / self.__steps_per_sec))
        if self.__callback is not None:
            self.__callback(int(frame))

    def set_frame(self, frame:int):
        '''sets current step - does not call callback function'''
        assert frame <= self.__frame_num, f'TimeSlider Error: Tried to set frame to {frame} which is greater than max frame: {self.__frame_num}'
        self.__Slider.set(frame / self.__frame_num)
        self.__label.config(text=seconds_text(frame / self.__steps_per_sec))

    def set_frame_num(self, frame_num:int, frame_rate):
        '''sets max frame - frame_rate is just there for consistency with Scrollbars'''
        self.__Slider.set(self.__frame_num * self.__Slider.get() / frame_num)
        self.__frame_num = frame_num
        self.__end_label.config(text=seconds_text(self.__frame_num / self.__steps_per_sec))

    def set_steps_per_sec(self, steps_per_sec:float):
        '''updates steps per sec without changing the number of steps'''
        self.__steps_per_sec = steps_per_sec
        self.__label.config(text=seconds_text(self.__Slider.get() * self.__frame_num / self.__steps_per_sec))
        self.__end_label.config(text=seconds_text(self.__frame_num / self.__steps_per_sec))

    def get(self) -> int:
        '''returns the current frame'''
        return int(self.__frame_num * self.__Slider.get())
    
    def get_sec(self) -> float:
        '''returns current slider position in seconds'''
        return self.__frame_num * self.__Slider.get() / self.__steps_per_sec

class LabelSlider(Frame):
    ''' Combination of Slider and NumberEditLabel so that slider value can be
        seen by the user.

        LabelSlider can handle any range of values, unlike Slider, which only
        handles values between 0 and 1.

        LabelSlider has three components: slider, number label, and text label.
        The number label displays the current value and text label is static.

        DO NOT user LabelSlider directly. It is only for inheritance from
        HorizontalSlider and VerticalSlider.
    '''
    def __init__(self, master:Frame, child_frame=None, callback=None, bg='#ffffff',
                 label:str='', popup_label=None, font_name='Segoe UI', font_size=10,
                 text_fg='#000000', popup_bg='#000000', popup_font_name=None,
                 popup_font_size=None, min_value=0, max_value=100, step=1, default_value=None,
                 label_editable=True, label_draggable=False, reference_width=2.0,
                 max_len=None, drag_threshold=0.2, label_justify='left', label_bg=None,
                 label_fg=None, label_hover_bg:str=None, label_error_color='#ff0000',
                 line_color='#555555', active_line_color=None, active_line_hover_color=None,
                 slider_color='#ffffff', slider_drag_color=None, hide_slider=False,
                 slider_visible=True, slider_height=20, slider_width=20, slider_type='circle',
                 orientation='h', line_width=2, canvas_height=0, canvas_width=0,
                 **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param child_frame: tk.Frame - to optionally put widgets in a frame other than self
            :param callback: function (int|float), called when value is changed

        Slider Parameters
        -----------------
            :param line_color: str (hex code) - color of line
            :param active_line_color: str (hex code) - color of active portion of line (if different from line_color)
            :param active_line_hover_color: str (hex code) - color of active portion of line when hovering
                                                           - if different from active_line_color
            :param slider_color: str (hex code) - slider color
            :param slider_drag_color: str (hex code) - slider color when mouse is depressed (if different from slider color)
            :param hide_slider: bool - if True, slider is hidden when cursor is not hovering
            :param slider_visible: bool - if False, slider is never visible
            :param slider_height: int - height of slider in pixels (or diameter for circle slider)
            :param slider_width: int - width of slider in pixels
            :param slider_type: Literal['circle', 'rectangle'] - type of slider
            :param orientation: Literal['h', 'v'] - horizontal or vertical orientation
            :param line_width: int - width of slider line in pixels
            :param canvas_height: int - slider canvas height in pixels
            :param canvas_width: int - slider canvas width in pixels

        Label Parameters
        ----------
            :param min_value: int or float - minimum value
            :param max_value: int or float - maximum value
            :param step: int or float - number increment
            :param default_value: int or float - default value if different from min_value
            :param label_editable: bool - if True, label can be double clicked to enter exact value
            :param label_draggable: bool - if True, label can be dragged to adjust value
            :param reference_width: float - fraction of label width
            :param max_len: int - maximum number of characters in entry box
            :param drag_threshold: float (seconds) - click duration to be considered a single click (not drag)
            :param label_justify: Literal['left', 'right', 'center'] - justification in label entry box
            :param label_bg: str (hex code) - label background color (if different from bg)
            :param label_fg: str (hex code) - label text color (if different from text_fg)
            :param label_hover_bg: str (hex code) - label background color when hovering (if different from label_bg)
            :param label_error_color: str (hex code) - background color in entry box for bad text
        '''
        if child_frame is None: # dont need to init Frame if nothing is being put in it
            super().__init__(master, bg=bg, **kwargs)
        self.__callback = callback

        child_frame = child_frame if child_frame is not None else self

        # Slider
        self.Slider = Slider(child_frame, self.__slider_callback,
                             bg=bg, line_color=line_color, active_line_color=active_line_color,
                             active_line_hover_color=active_line_hover_color,
                             slider_color=slider_color, slider_drag_color=slider_drag_color,
                             hide_slider=hide_slider, slider_visible=slider_visible,
                             slider_height=slider_height, slider_width=slider_width,
                             slider_type=slider_type, orientation=orientation,
                             height=canvas_height, width=canvas_width,
                             line_width=line_width)
        
        # Number Label
        label_bg = label_bg if label_bg is not None else bg
        label_fg = label_fg if label_fg is not None else text_fg
        label_hover_bg = label_hover_bg if label_hover_bg is not None else label_bg
        self.Label = NumberEditLabel(child_frame, self.__label_callback, min_value=min_value,
                                     max_value=max_value, step=step, default_value=default_value,
                                     reference_width=reference_width, max_len=max_len,
                                     drag_threshold=drag_threshold, draggable=label_draggable,
                                     editable=label_editable, justify=label_justify,
                                     bg=label_bg, fg=label_fg, hover_bg=label_hover_bg,
                                     error_color=label_error_color,
                                     font_name=font_name, font_size=font_size)
        
        # Static Text Label
        self.__popup_label = popup_label
        self.Text = Label(child_frame, text=label, bg=bg, fg=text_fg, font=(font_name, font_size))
        if self.__popup_label is not None:
            popup_font_name = popup_font_name if popup_font_name is not None else font_name
            popup_font_size = popup_font_size if popup_font_size is not None else font_size
            self.tool_tip = ToolTip(self.Text, bg=popup_bg, fg='#ffffff',
                                    font=(popup_font_name, popup_font_size))
            self.Text.bind('<Enter>', self.__text_hover_enter)
            self.Text.bind('<Leave>', self.__text_hover_leave)
        
        # Set Slider Value
        self.Slider.set(self.Label.get_perc())

    def __text_hover_enter(self, event=None):
        '''called when cursor enters the label'''
        if self.__popup_label is not None:
            self.tool_tip.fadein(0, self.__popup_label, event)

    def __text_hover_leave(self, event=None):
        '''called when cursor enters the label'''
        if self.__popup_label is not None:
            self.tool_tip.fadeout(1, event) # first argument is initial alpha
        
    def __slider_callback(self, perc:float):
        '''called when slider is moved by user
        :param perc: float between 0 and 1 - slider value
        '''
        self.Label.set_perc(perc)
        if self.__callback is not None:
            self.__callback(self.Label.get())

    def __label_callback(self, value:float):
        '''called when label value is changed by user'''
        self.Slider.set(self.Label.get_perc())
        if self.__callback is not None:
            self.__callback(value)

    def set_text(self, text:str):
        '''sets static text'''
        self.Text.config(text=text)

    def set_min_value(self, min_value):
        '''sets minimum value'''
        self.Label.set_min_value(min_value)
        self.Slider.set(self.Label.get_perc())

    def set_max_value(self, max_value):
        '''sets maximum value'''
        self.Label.set_max_value(max_value)
        self.Slider.set(self.Label.get_perc())

    def set(self, value):
        '''updates current value'''
        self.Label.set(value)
        self.Slider.set(self.Label.get_perc())

    def get(self):
        '''returns current value'''
        return self.Label.get()

class HorizontalSlider(LabelSlider):
    ''' Horizontal adaptation of LabelSlider
    
        Value label and static text label can be on either side of the slider

        There is the option for LabelSlider to be a single widget, or to grid
        the children directly in the parent frame. To grid children in the
        parent frame, specify the 'row' argument.
    '''
    def __init__(self, master:Frame, value_left=False, start_col=0, row=None,
                 slider_pady=0, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent frame
            :param value_left: bool - True to put value label on left side and text on right side
            :param start_col: int - start column (only if widgets are directly in master)
            :param row: int - row in master or None to put widgets in self
        '''
        child_frame = master if row is not None else None
        super().__init__(master, child_frame=child_frame, orientation='h', **kwargs)

        if row is not None: # to grid widgets in master
            if value_left:
                value_col, text_col = start_col, 2 + start_col
            else:
                value_col, text_col = 2 + start_col, start_col
            slider_col = 1 + start_col
            self.Slider.grid(row=row, column=slider_col, pady=slider_pady, sticky='ew')
            self.Label.grid(row=row, column=value_col, pady=slider_pady, sticky='nsew')
            self.Text.grid(row=row, column=text_col, pady=slider_pady, sticky='nsew')
        else: # pack in self
            if value_left:
                value_side, text_side = 'left', 'right'
            else:
                value_side, text_side = 'right', 'left'
            self.Label.pack(side=value_side)
            self.Text.pack(side=text_side)
            self.Slider.pack(side='left', fill='x', expand=True)

class VerticalSlider(LabelSlider):
    ''' Vertical adaptation of LabelSlider
    '''
    def __init__(self, master:Frame, **kwargs):
        super().__init__(master, orientation='v', label_justify='center', **kwargs)

        self.Label.pack(side='bottom', fill='x') # not sure if this should fill
        self.Slider.pack(side='bottom', fill='y', expand=True)
        if 'label' in kwargs.keys() and kwargs['label'] != '': # only pack Text if there is a label
            self.Text.pack(side='top')

class ScrollBar(Canvas):
    ''' ScrollBar for navigating scrollable widgets
    
        Only handles values between 0 and 1
        
        The current position is defined by two values that correspond to the
        visible start and end point of the linked scrollable widget
    '''
    def __init__(self, master:Frame, callback=None, default0=0, default1=1,
                 bg:str='#ffffff', slider_color:str='#000000',
                 slider_hover_color=None, slider_drag_color=None,
                 width=None, height=None, orientation='h',
                 disappear_when_filled=True):
        '''
        Parameters
        ----------
            :param master: Frame - parent widget
            :param callback: function (float, float) - called when slider is moved
                                                     - takes two values between 0 and 1
            :param default0: float (between 0 and 1) - default lower bound
            :param default1: float (between 0 and 1) - default upper bound
            :param bg: str (hex code) - slider background color
            :param slider_color: str (hex code) - slider color when not hovering or dragging
            :param slider_hover_color: str (hex code) - slider color when hovering (if different from slider color)
            :param slider_drag_color: str (hex code) - slider color when dragging (if different from hover color)
            :param width: int (pixels) or None - canvas width (for vertical orientation)
            :param height: int (pixels) or None - canvas height (for horiontal orientation)
            :param orientation: Literal['h', 'v'] - horizontal or vertical orientation
            :param disappear_when_filled: bool - if True hides slider when no scrolling is possible
        '''
        assert orientation in ['h', 'v'], f'ScrollBar Error: Invalid orientation: {orientation}'
        assert default0 >= 0 and default0 <= 1, f'ScrollBar Error: Default0 out of range: {default0}'
        assert default1 >= 0 and default1 <= 1, f'ScrollBar Error: Default1 out of range: {default1}'

        super().__init__(master, bg=bg, width=width, height=height, highlightthickness=0)

        self.__dragging = False
        self.__callback = callback
        self.__orientation = orientation
        self.__p0, self.__p1 = default0, default1
        self.__disappear_when_filled = disappear_when_filled
        self.__slider_color = slider_color
        self.__slider_hover_color = slider_hover_color if slider_hover_color is not None else self.__slider_color
        self.__slider_drag_color = slider_drag_color if slider_drag_color is not None else self.__slider_hover_color

        self.__slider_id = self.create_rectangle(0, 0, 0, 0, fill=self.__slider_color,
                                                 width=0, state='normal')
        
        # Event Bindings
        self.tag_bind(self.__slider_id, "<Button-1>", self.__click)
        self.tag_bind(self.__slider_id, "<ButtonRelease-1>", self.__release)
        self.tag_bind(self.__slider_id, "<B1-Motion>", self.__motion)
        self.tag_bind(self.__slider_id, "<Enter>", self.__hover_enter)
        self.tag_bind(self.__slider_id, "<Leave>", self.__hover_leave)
        
        self.bind('<Configure>', self.__set_coords)
        
        self.event_generate('<Configure>', when='tail')

    def __set_coords(self, event=None, filled_thresh=0.001):
        '''updates coordinates of lines and slider based on canvas size and current value'''
        # sets slider coordinates based on self.__p0 and self.__p1
        h, w = self.winfo_height(), self.winfo_width()
        if self.__orientation == 'h': # horizontal
            y0, y1 = 0, h
            x0, x1 = self.__p0 * w, self.__p1 * w
        elif self.__orientation == 'v': # vertical
            x0, x1 = 0, w
            y0, y1 = self.__p0 * h, self.__p1 * h
        self.coords(self.__slider_id, x0, y0, x1, y1)
        if self.__disappear_when_filled and self.__p0 < filled_thresh and self.__p1 > 1 - filled_thresh:
            self.itemconfig(self.__slider_id, state='hidden')
        else:
            self.itemconfig(self.__slider_id, state='normal')
    
    def __hover_enter(self, event=None):
        '''cursor enters canvas'''
        self.itemconfig(self.__slider_id, fill=self.__slider_hover_color)

    def __hover_leave(self, event=None):
        '''cursor leaves canvas'''
        if not self.__dragging:
            self.itemconfig(self.__slider_id, fill=self.__slider_color)

    def __click(self, event):
        '''cursor clicks on canvas - move slider to click position'''
        self.__dragging = True
        self.itemconfig(self.__slider_id, fill=self.__slider_drag_color)
        x0, y0, _, _ = self.coords(self.__slider_id)
        self.__click_x = event.x - x0 # pixels from mouse to left edge of slider
        self.__click_y = event.y - y0 # pixels from mouse to top edge of slider

    def __release(self, event):
        '''cursor releases click - change slider color to normal'''
        self.__dragging = False
        self.itemconfig(self.__slider_id, fill=self.__slider_hover_color)
        x0, y0, x1, y1 = self.coords(self.__slider_id)
        if event.x < x0 or event.x > x1 or event.y < y0 or event.y > y1: # not hovering
            self.__hover_leave()

    def __motion(self, event):
        '''cursor drags slider'''
        x0, y0, x1, y1 = self.coords(self.__slider_id)
        w, h = self.winfo_width(), self.winfo_height()
        if self.__orientation == 'h':
            add = max(-x0, min(w - x1, (event.x - x0) - self.__click_x))
            x0 += add
            x1 += add
            self.__p0, self.__p1 = x0 / w, x1 / w
        elif self.__orientation == 'v':
            add = max(-y0, min(h - y1, (event.y - y0) - self.__click_y))
            y0 += add
            y1 += add
            self.__p0, self.__p1 = y0 / h, y1 / h
        self.coords(self.__slider_id, x0, y0, x1, y1)
        if self.__callback is not None:
            self.__callback(self.__p0, self.__p1)

    def set(self, p0:float, p1:float):
        '''sets slider value - must be between 0 and 1 (does not call callback function)'''
        assert p0 >= 0 and p0 <= 1, f'ScrollBar Error: set lower bound to invalid value: {p0}'
        assert p1 >= 0 and p1 <= 1, f'ScrollBar Error: set upper bound to invalid value: {p1}'
        assert p1 >= p0 ,f'ScrollBar Error: lower bound is greater than upper bound! lower: {p0}, upper: {p1}'
        self.__p0, self.__p1 = p0, p1
        self.__set_coords()

    def get(self):
        '''returns current slider value'''
        return self.__p0, self.__p1


class HorizontalSliderGroup(Frame):
    ''' Group of horizontally oriented sliders connected by a single callback
        function
        
        The callback function is called whenever any of the slider values is
        changed by the user and is given 2 arguments: (slider_label, new_value)
    '''
    def __init__(self, master:Frame, parameters:list, callback, bg='#ffffff',
                 width=250, slider_pady=5, frame_padx=0, title_label=True,
                 **kwargs):
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
                        description: str - info displayed when mouse hovers on slider (optional)
            :param callback: function (parameter_name, value) - called whenever a slider is adjusted
            :param bg: str (hex code) - background color
            :param width: int - width of each slider in pixels
            :param slider_pady: int - y pad inside sliders
            :param frame_padx: int - x pad inside frame
            :param title_label: bool - if True display 'fade_in' as 'Fade In'
            **kwargs passed to each slider
        '''
        Frame.__init__(self, master, bg=bg, padx=frame_padx)
        self.grid_columnconfigure(0, weight=0) # text label
        self.grid_columnconfigure(1, weight=1) # slider
        self.grid_columnconfigure(2, weight=0) # value label
        self.sliders: list[HorizontalSlider] = []
        self.labels = [d['label'] for d in parameters]
        for i, param in enumerate(parameters):
            label = param['label'].replace('_', ' ').title() if title_label else param['label']
            popup_label = param['description'] if 'description' in param.keys() else None
            S = HorizontalSlider(self, start_col=0, row=i, bg=bg, canvas_width=width,
                                 callback=lambda x, l=param['label']: callback(l, x),
                                 min_value=param['min_value'], max_value=param['max_value'],
                                 step=param['step'], default_value=param['value'],
                                 label=label, popup_label=popup_label,
                                 slider_pady=slider_pady, **kwargs)
            self.sliders.append(S)

    def get(self) -> dict:
        '''returns dictionary with current value of each slider'''
        return [{label:slider.get()} for label, slider in zip(self.labels, self.sliders)]

class VerticalSliderGroup(Frame):
    ''' Group of vertically oriented sliders connected by a single callback
        function
        
        The callback function is called whenever any of the slider values is
        changed by the user and is given 2 arguments: (slider_label, new_value)
    '''
    def __init__(self, master, parameters:list, callback, bg:str, rows:int,
                 columns:int, height=250, slider_pady=5, slider_padx=5,
                 title_label=True, **kwargs):
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
            :param slider_pady: int - y pad between sliders
            :param slider_padx: int - x pad between sliders
            :param title_label: bool - if True display 'fade_in' as 'Fade In'
            **kwargs passed to each slider
        '''
        Frame.__init__(self, master, bg=bg)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        for i in range(columns):
            self.grid_columnconfigure(i, weight=1)
        self.sliders: list[VerticalSlider] = []
        self.labels = [d['label'] for d in parameters]
        for i, param in enumerate(parameters):
            label = param['label'].replace('_', ' ').title() if title_label else param['label']
            popup_label = param['description'] if 'description' in param.keys() else None
            S = VerticalSlider(self, callback=lambda x, l=param['label']: callback(l, x),
                               min_value=param['min_value'], max_value=param['max_value'],
                               step=param['step'], default_value=param['value'],
                               label=label, popup_label=popup_label, bg=bg,
                               canvas_height=height, **kwargs)
            S.grid(row=i // columns, column=i % columns, sticky='nsew',
                   padx=slider_padx, pady=slider_pady)
            self.sliders.append(S)

    def get(self) -> dict:
        '''returns dictionary with current value of each slider'''
        return [{label:slider.get()} for label, slider in zip(self.labels, self.sliders)]
   
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
        self.xmin, self.xmax = 0, 1 # only needed before Canvas has been rendered - '<Configure>'
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

