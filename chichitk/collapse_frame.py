from tkinter import Label, Frame


class CollapseFrame(Frame):
    ''' Extension of tk.Frame that includes a header that is always visible,
        and a body frame that can be shown/hidden by clicking on the header
        or with an external command.

        Contains the attributes 'header' and 'frame' which are both tk.Frame
        objects refering to the header and body frames respectively.

        DO NOT put anything directly in the CollapseFrame. Only user the header
        and body frames.

        Warning: if CollapseFrame is initially close, and not collapsable,
        there will be no way for user to access the content of the body frame.
    '''
    def __init__(self, master:Frame, open_callback=None, close_callback=None,
                 label=None, bg='#ffffff', border_bg=None,
                 inactive_bg=None, active_bg=None, inactive_hover_bg=None,
                 active_hover_bg=None, inactive_fg='#000000', active_fg=None,
                 inactive_hover_fg=None, active_hover_fg=None,
                 label_side='left', font_name='Segoe UI', font_size=10,
                 label_padx=0, label_pady=0, body_padx=0, body_pady=0,
                 active=True, collapsable=True, **kwargs):
        '''active refers to the state when the body frame is visible
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param open_callback: function () - called when body frame is made visible
            :param close_callback: function () - called when body frame is hidden
            :param label: str or None - header text
            :param bg: str (hex code) - background color
            :param border_bg: str (hex code) - color of base frame (border around body frame)
            :param inactive_bg: str (hex code) - inactive header background color (if different from bg)
            :param active_bg: str (hex code) - active header background color (if different from inactive_bg)
            :param inactive_hover_bg: str (hex code) - inactive hover background color (if different from inactive_bg)
            :param active_hover_bg: str (hex code) - active hover background color (if different from active_bg)
            :param inactive_fg: str (hex code) - inactive label color
            :param active_fg: str (hex code) - active label color
            :param inactive_hover_fg: str (hex code) - inactive hover label color (if different from inactive_fg)
            :param active_hover_fg: str (hex code) - active hover label color (if different from active_fg)
            :param label_side: str Literal['left', 'right', 'top'] - label justification
            :param font_name: str - label font name
            :param font_size: str - label font size
            :param label_padx: int - x padding of label within header frame
            :param label_pady: int - y padding of label within header frame
            :param body_padx: int - x padding around body frame
            :param body_pady: int - y padding around body frame
            :param active: bool - initial visibility of body frame
            :param collapsable: bool - if True, CollapseFrame is static
        '''
        super_bg = border_bg if border_bg is not None else bg
        super().__init__(master, bg=super_bg, **kwargs)
        self.__open_callback = open_callback
        self.__close_callback = close_callback
        self.__body_padx, self.__body_pady = body_padx, body_pady
        inactive_bg = inactive_bg if inactive_bg is not None else bg
        active_bg = active_bg if active_bg is not None else inactive_bg
        inactive_hover_bg = inactive_hover_bg if inactive_hover_bg is not None else inactive_bg
        active_hover_bg = active_hover_bg if active_hover_bg is not None else active_bg
        self.__bg_colors = [[inactive_bg, active_bg], [inactive_hover_bg, active_hover_bg]]
        active_fg = active_fg if active_fg is not None else inactive_fg
        inactive_hover_fg = inactive_hover_fg if inactive_hover_fg is not None else inactive_fg
        active_hover_fg = active_hover_fg if active_hover_fg is not None else active_fg
        self.__fg_colors = [[inactive_fg, active_fg], [inactive_hover_fg, active_hover_fg]]
        self.__draw_label = label is not None
        self.__collapsable = collapsable
        self.__active, self.__hovering = active, False

        # Header Frame
        self.header = Frame(self)
        self.header.pack(side='top', fill='x')
        if self.__collapsable:
            self.header.bind('<Enter>', self.hover_enter)
            self.header.bind('<Leave>', self.hover_leave)
            self.header.bind('<Button-1>', self.header_click)
        if self.__draw_label:
            self.label = Label(self.header, text=label, font=(font_name, font_size))
            self.label.pack(side=label_side, padx=label_padx, pady=label_pady)
            if self.__collapsable:
                self.label.bind('<Enter>', self.hover_enter)
                self.label.bind('<Leave>', self.hover_leave)
                self.label.bind('<Button-1>', self.header_click)

        # Body Frame
        self.frame = Frame(self, bg=bg)
        if self.__active:
            self.show(callback=False)

        self.__color_config()

    def __color_config(self):
        '''updates header color based on active/hover status'''
        bg = self.__bg_colors[self.__hovering][self.__active]
        fg = self.__fg_colors[self.__hovering][self.__active]
        self.header.config(bg=bg)
        if self.__draw_label:
            self.label.config(bg=bg, fg=fg)

    def set_bg(self, color:str, hovering=False, active=False):
        '''updates background color for given hover/select status'''
        self.__bg_colors[hovering][active] = color

    def set_fg(self, color:str, hovering=False, active=False):
        '''updates foreground color for given hover/select status'''
        self.__fg_colors[hovering][active] = color

    def hover_enter(self, event=None):
        '''called when mouse enters header'''
        if not self.__collapsable:
            print('CollapseFrame Error: tried to hover enter when CollapseFrame is not collapsable')
            return
        self.__hovering = True
        self.__color_config()

    def hover_leave(self, event=None):
        '''called when mouse leaves header'''
        if not self.__collapsable:
            print('CollapseFrame Error: tried to hover leave when CollapseFrame is not collapsable')
            return
        self.__hovering = False
        self.__color_config()

    def header_click(self, event=None):
        '''called when mouse clicks on header - toggles active status'''
        if not self.__collapsable:
            print('CollapseFrame Error: tried to toggle body frame when CollapseFrame is not collapsable')
            return
        if self.__active:
            self.hide(callback=True)
        else:
            self.show(callback=True)

    def show(self, callback=True):
        '''makes body frame visible'''
        self.__active = True
        self.__color_config()
        self.frame.pack(fill='both', expand=True,
                        padx=self.__body_padx, pady=self.__body_pady)
        if callback and self.__open_callback is not None:
            self.__open_callback()

    def hide(self, callback=True):
        '''hides body frame'''
        self.__active = False
        self.__color_config()
        self.frame.pack_forget()
        if callback and self.__close_callback is not None:
            self.__close_callback()

