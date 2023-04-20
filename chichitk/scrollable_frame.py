import tkinter as tk
import tkinter.ttk as ttk


class ScrollableFrame(tk.Frame):
    ''' Frame that allows widgets to be placed outside the visible area and
        scrolled into view
        
        <MouseWheel> event must be bound to all widgets placed in the
        scrollable frame. By default, the <MouseWheel> event is only bound
        to the frame itself
        
        All widgets must be put in self.scrollable_frame, not self
    '''
    def __init__(self, master:tk.Frame, bg:str, include_scrollbar:bool=True,
                 scrollbar_side='right', yscrollincrement:int=1,
                 check_hover=False, *args, **kwargs):
        '''
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param bg: str (hex code) - background color
            :param include_scrollbar: bool - if True, scrollbar is packed right
            :param scrollbar_side: str - Literal['left', 'right']
            :param yscrollincrement: int - pixels scrolled per mouse scroll (70x)
            :param check_hover: bool - if True, will only respond to mousewheel
                                       events if the cursor is hovering on Frame
        '''
        assert scrollbar_side in ['left', 'right'], f'Invalide scrollbar side: {scrollbar_side}'
        self.hovering = not check_hover
        super().__init__(master, *args, **kwargs)
        style = ttk.Style(master)
        style.theme_use("alt")
        style.layout('arrowless.Vertical.TScrollbar',
                     [('Vertical.Scrollbar.trough', 
                     {'children': [('Vertical.Scrollbar.thumb',
                                    {'expand': '1', 'sticky': 'nswe'})],
                                    'sticky': 'ns'})])
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0,
                                yscrollincrement=yscrollincrement)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg)
        self.scrollable_frame.bind("<Configure>", self.OnFrameConfigure)
        self.canvas_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        if include_scrollbar:
            scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                      style='arrowless.Vertical.TScrollbar')
            self.canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=scrollbar_side, fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        style.configure("arrowless.Vertical.TScrollbar", troughcolor=bg)
        self.canvas.bind('<Configure>', self.FrameWidth)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self.on_mousewheel)
        if check_hover:
            self.bind('<Enter>', self.hover_enter)
            self.bind('<Leave>', self.hover_leave)

    def on_mousewheel(self, event, scroll_px=70):
        '''called when mouse wheel moves
        does not allow canvas to scroll past the top'''
        if self.hovering:
            scrollby = int(max(-self.canvas.canvasy(0), -event.delta * scroll_px /120))
            self.canvas.yview_scroll(scrollby, "units")

    def scroll_to_top(self):
        '''scrolls to the top of page'''
        self.canvas.yview_scroll(int(-self.canvas.canvasy(0)), "units")

    def hover_enter(self, event=None):
        '''called when the cursor enters frame'''
        self.hovering = True

    def hover_leave(self, event=None):
        '''called when the cursor leaves frame'''
        self.hovering = False

    def FrameWidth(self, event):
        '''called when canvas is resized'''
        self.canvas.itemconfig(self.canvas_id, width = event.width)

    def OnFrameConfigure(self, event):
        '''called when scrollable frame is resized'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
