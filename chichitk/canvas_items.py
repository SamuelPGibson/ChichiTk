from tkinter import Canvas, Menu


# helper function - makes a hex code color brighter or darker
def brighten(hex_code:str, fact:float):
    '''brightens hex_code by fact
    hex_code will be moved fact % of the way closer to full brightness
    
    :param hex_code: string - hex code in form "#0b0d34" or "0b0d34"
    :param fact: float between -1 and 1 - negative fact makes hex_code darker
    '''
    l = (hex_code[1:3], hex_code[3:5], hex_code[5:]) # split hex code into rgb components
    fact = max(-1, min(1, fact))
    if fact >= 0: # increase brightness
        values = [int(h, base=16) + (255 - int(h, base=16)) * fact for h in l]
    else: # decrease brightness
        values = [int(h, base=16) * (1 + fact) for h in l]
    return '#' + ''.join([f'{hex(int(round(v, 0)))[2:]:0>2}' for v in values])


class CanvasEditLine():
    ''' General class for draggable line in canvas

        Line can optionally call a callback function whenever slider is moved
        by user
    '''
    def __init__(self, canvas:Canvas, x:float, y0:float, height:int, width=4,
                 bg:str='#ffffff', drag_color:str='#e8ff00', hover_color=None,
                 select_color:str='#499de6', brighten_fact:float=-0.25,
                 select_brighten_fact:float=0.3, selectable:bool=True,
                 hoverable:bool=True, draggable:bool=True, show_drag_color=False,
                 drag_function=None, self_select_function=None, self_delete_function=None,
                 always_deselect:bool=False, menu_font_name='Segoe UI', menu_font_size=11,
                 double_click_to_delete:bool=True, deletable=True, active=True,
                 tag_name:str='tag', state:str='normal'):
        '''        
        Parameters
        ----------
            :param canvas: tk.Canvas - canvas in which to create rectangle
            :param x: float (pixels) - x coordinate of line
            :param y0: float (pixels) - line top in canvas
            :param height: float (pixels) - line height in canvas
            :param width: float (pixels) - line width
            :param bg: str (hex code) - fill color when not hovering
            :param drag_color: str (hex code) - fill color when line is being dragged - only if show_drag_color is True
            :param hover_color: str (hex code) or None - fill color when hovering
            :param select_color: str (hex code) - fill color when selected
            :param brighten_fact: float (-1, 1) - brighten fill color by brighten_fact on hover
            :param select_brighten_fact: float (-1, 1) - brighten fill color by brighten_fact on hover when selected
            :param selectable: bool - True if fill can be selected to select_color
            :param hoverable: bool - if False, color will not change on hover
            :param draggable: bool - if True, line can be dragged in x dimension by cursor
            :param show_drag_color: bool - if True, show drag_color instead of select_color when line is being dragged
            :param drag_function: 2-float input function (current_x, cursor_position_x) - returns 1 float (new_x)
            :param double_click_function: 1 argument function (event) or None - called when line is double clicked
            :param right_click_function: 1 argument function (event) or None - called when line is right clicked
            :param center_click_function: 1 argument function (event) or None - called when line is center clicked
            :param self_delete_function: 1 argument function (self) - called when item is self deleted (with popup menu)
            :param self_select_function: 1 argument function (self) - called when item is self selected (selected by clicking on Item)
            :param always_deselect: bool - if True, will deselect upon command even if cursor is hovering
            :param deletable: bool - if True, line can be deleted from right-click popup menu
            :param active: bool - if False, CanvasEditFill will be unresponsive to user actions, regardless of other settings - for toggling
            :param tag_name: str - tag name given to all canvas items - should be general for items of guitar track, chords track, etc
            :param state: str - state in canvas when item is created - options: ['normal', 'hidden', 'disabled']
        '''
        self.active = active
        self.canvas = canvas
        self.brighten_fact = brighten_fact
        self.show_drag_color, self.drag_color = show_drag_color, drag_color
        if hover_color:
            self.colors = [[bg, select_color], [hover_color, hover_color]]
        else:
            self.colors = [[bg, select_color], [brighten(bg, brighten_fact), brighten(select_color, select_brighten_fact)]]
        self.selected, self.dragging, self.hovering = [False] * 3
        self.drag_function = drag_function
        self.self_select_function, self.self_delete_function = self_select_function, self_delete_function
        self.always_deselect = always_deselect
        self.draggable, self.selectable, self.hoverable = draggable, selectable, hoverable        
        self.tag_name = tag_name

        self.id = self.canvas.create_line(x, y0, x, y0 + height, fill=self.get_color(), width=width, state=state,
                                            tags=[self.tag_name, self.tag_name + '_item'])
        
        self.canvas.tag_bind(self.id, '<Enter>', self.__hover_enter)
        self.canvas.tag_bind(self.id, '<Leave>', self.__hover_leave)
        if self.draggable or self.selectable:
            self.canvas.tag_bind(self.id, '<Button-1>', self.click)
        if self.draggable:
            self.canvas.tag_bind(self.id, '<ButtonRelease-1>', self.release)
            self.canvas.tag_bind(self.id, '<B1-Motion>', self.drag)

        if deletable:
            self.menu = Menu(canvas, tearoff=False, bg='#000000', fg='#ffffff',
                            activebackground='#222222', font=(menu_font_name, menu_font_size))
            self.menu.add_command(label="Delete", command=self.self_delete)
            self.canvas.tag_bind(self.id, "<Button-3>", self.right_click)
        if double_click_to_delete:
            self.canvas.tag_bind(self.id, "<Double-Button-1>", self.self_delete)

    def set_active(self):
        '''sets state to active so that user interactions proceed as normal'''
        self.active = True

    def set_inactive(self):
        '''sets state to inactive so that line is unresponsive to user interactions'''
        self.active = False

    def get_color(self):
        '''returns current line color based on hover/select/drag status'''
        if self.dragging and self.show_drag_color:
            return self.drag_color
        return self.colors[self.hovering][self.selected]

    def set_color(self, color:str):
        '''set fill color (when not selected)'''
        self.colors[0][0], self.colors[1][0] = color, brighten(color, self.brighten_fact)
        self.color_config()

    def color_config(self):
        '''configure the line color based on hover/select status'''
        self.canvas.itemconfig(self.id, fill=self.get_color())

    def __hover_enter(self, event=None):
        '''cursor enters line'''
        if not self.active:
            return
        self.hovering = self.hoverable
        if not self.dragging:
            if self.draggable:
                self.canvas.config(cursor='sb_h_double_arrow')
            self.color_config()

    def __hover_leave(self, event=None):
        '''cursor leaves line'''
        if not self.active:
            return
        self.hovering = False
        if not self.dragging:
            self.canvas.config(cursor='arrow')
            self.color_config()

    def click(self, event=None):
        '''cursor clicks on line'''
        if not self.active:
            return
        if self.selectable and not self.selected and self.self_select_function:
            self.self_select_function(self)
        self.selected, self.dragging = self.selectable, self.draggable
        self.color_config()
        self.canvas.tag_raise(self.id)

    def drag(self, event):
        '''cursor drags line'''
        if not self.active:
            return
        cursor_x = self.canvas.canvasx(event.x)
        x, y0, _, y1 = self.canvas.coords(self.id)
        if self.drag_function:
            x = self.drag_function(x, cursor_x)
        else:
            x = cursor_x
        self.canvas.coords(self.id, x, y0, x, y1)

    def release(self, event=None):
        '''cursor releases click'''
        if not self.active:
            return
        self.dragging = False
        if not self.hovering:
            self.__hover_leave()

    def right_click(self, event):
        '''called when user right-clicks on line'''
        if self.active:
            self.menu.tk_popup(event.x_root, event.y_root)

    def set_x(self, x:float):
        '''updates x coordinate of line - y coordinate remain the same'''
        _, y0, _, y1 = self.canvas.coords(self.id)
        self.canvas.coords(self.id, x, y0, x, y1)

    def get_x(self) -> float:
        '''returns the x coordinate of line'''
        return self.canvas.coords(self.id)[0]

    def raise_line(self):
        '''raises line within canvas'''
        self.canvas.tag_raise(self.id)

    def select(self):
        '''select line'''
        if not self.selected and self.selectable:
            self.selected = True
            self.color_config()
            self.canvas.tag_raise(self.id)

    def deselect(self, override=False):
        '''if override is True, will deselect even if hovering'''
        if self.selected and (not self.hovering or self.always_deselect or override):
            self.selected = False
            self.color_config()

    def self_delete(self, event=None):
        '''deleted with popup menu'''
        if self.self_delete_function:
            self.self_delete_function(self)
        self.canvas.config(cursor='arrow')
        self.delete()

    def delete(self):
        '''delete line'''
        self.canvas.delete(self.id)

class CanvasEditFill():
    ''' General class for draggable rectangle displayed in canvas

        This is abominable overkill for its use in ChichiTk, but CanvasEditFill
        was created for another purpose and it works for ChichiTk as well.
    '''
    def __init__(self, canvas:Canvas, id:str, x0:float, x1:float, y0:float, height:int,
                 relative_coordinates:bool=False, line_width:int=2,
                 bg:str='#ffffff', text_color:str='#000000',
                 text_hover_color:str='#000000', text_select_color:str='#000000',
                 text_hover_select_color:str='#000000', corner_line_color:str='#ffffff',
                 border_color=None, bar_color=None, select_color:str='#499de6',
                 brighten_fact:float=-0.25, select_brighten_fact:float=0.3,
                 main_font_name:str='Segoe UI bold', main_font_size:int=16,
                 hover_font_name:str='Segoe UI bold', hover_font_size:int=14,
                 active_bar=False, active_bar_height=0.2, main_text_justify:str='center',
                 main_text_hover_justify:str='left', hover_text_justify:str='right',
                 main_text:str='', hover_text:str='', selectable:bool=True,
                 hoverable:bool=True, connectable:bool=False, box_draggable:str='both',
                 dot_width:int=7, corner_drag_function=None, corner_release_function=None,
                 drag_callback_function=None, double_click_function=None,
                 right_click_function=None, center_click_function=None,
                 self_delete_function=None, self_select_function=None,
                 x0_lock:bool=False, x1_lock:bool=False, y0_lock:bool=False, y1_lock:bool=False,
                 left_draggable:bool=False, right_draggable:bool=False,
                 top_draggable:bool=False, bottom_draggable:bool=False,
                 left_drag_function:bool=None, right_drag_function:bool=None,
                 top_drag_function:bool=None, bottom_drag_function:bool=None,
                 box_drag_function:bool=None, border_hover:bool=True,
                 always_deselect:bool=False, raise_on_click:bool=True,
                 bind_center_button:bool=False, active=True,
                 tag_name:str='tag', state:str='normal'):
        '''

        Canvas Tags
        -----------
            fill will have tag: tag_name + '_fill'
            border lines will have tag: tag_name + '_line'
            text will have tag: tag_name + '_text'
            all items will have id as tag for internal reference and tag_name as tag for full track toggle
        
        Parameters
        ----------
            :param canvas: tk.Canvas - canvas in which to create rectangle
            :param id: str - id unique to this fill item - used to change color of fill and lines at once, and delete
            :param x0: float (pixels) - box left edge in canvas
            :param x1: float (pixels) - box right edge in canvas
            :param y0: float (pixels) - box top edge in canvas - top left corner is (0, 0)
            :param height: float (pixels) - box height in canvas
            :param relative_coordinates: bool - if True x0, x1, y0, and height will be considered as percentages of canvas width and height
            :param line_width: float (pixels) - width of box edges - only drawn for dragging
            :param bg: str (hex code) - fill color when not hovering
            :param text_color: str (hex code) - text color when not hovering and not selected
            :param text_hover_color: str (hex code) - text color when hovering and not selected
            :param text_select_color: str (hex code) - text color when selected and not hovering
            :param text_hover_select_color: str (hex code) - text color when hovering and selected
            :param border_color: str (hex code) or None - color of border if different from bg
            :param bar_color: str (hex code) or None - color of bar if different from bg and border_color
            :param select_color: str (hex code) - fill color when hovering
            :param brighten_fact: float (-1, 1) - brighten fill color by brighten_fact on hover
            :param select_brighten_fact: float (-1, 1) - brighten fill color by brighten_fact on hover when selected
            :param main_font_name: str - font name for main text, such as "Segoe UI"
            :param main_font_size: int - main text font size
            :param hover_font_name: str - font name for hover text, such as "Segoe UI"
            :param hover_font_size: int - hover text font size
            :param main_text_justify: str - options: ['center', 'left', 'right']
            :param main_text_hover_justify: str - options: ['center', 'left', 'right']
            :param hover_text_justify: str - options: ['center', 'left', 'right']
            :param main_text: str
            :param hover_text: str
            :param active_bar: bool - if True, display bar when active instead of changing entire colour
            :param active_bar_height: float between 0 and 1 - active bar will start at bottom and occupy active_bar_height percent of height
            :param selectable: bool - True if fill can be selected to select_color
            :param hoverable: bool - if False, color will not change on hover
            :param connectable: bool - if True, item will have dots on corners to drag connections with other items
            :param dot_width: int - width of corner dots in pixels (completely inside box)
            :param corner_drag_function: 2 argument function (cursor_x, cursor_y) - called when corner dots are dragged
            :param corner_release_function: 3 argument function (self, cursor_x, cursor_y) - called when corner dots are released
            :param drag_callback_function: 1 argument function (self) - called when an edge or entire object is dragged by cursor
            :param double_click_function: 1 argument function (event) or None - called when box is double clicked
            :param right_click_function: 1 argument function (event)or None - called when box is right clicked
            :param center_click_function: 1 argument function (event) or None - called when bo is center clicked
            :param self_delete_function: 1 argument function (self) - called when item is self deleted (with popup menu)
            :param self_select_function: 1 argument function (self) - called when item is self selected (selected by clicking on Item)
            :param x0_lock: bool - toggleable setting for x0 drag
            :param x1_lock: bool - toggleable setting for x1 drag
            :param y0_lock: bool - toggleable setting for y0 drag
            :param y1_lock: bool - toggleable setting for y1 drag
            :param box_draggable: bool - options: ['horizontal', 'vertical', 'both', ''] - '' for not draggable
            :param left_draggable: bool - if True, left edge can be dragged independently
            :param right_draggable: bool - if True, right edge can be dragged independently
            :param top_draggable: bool - if True, top edge can be dragged independently
            :param bottom_draggable: bool - if True, bottom edge can be dragged independently
            :param left_drag_function: 3-float input function (current_x0, current_x1, cursor_position_x) - returns 1 float (new_x0)
            :param right_drag_function: 3-float input function (current_x0, current_x1, cursor_position_x) - returns 1 float (new_x1)
            :param top_drag_function: 3-float input function (current_y0, current_y0, cursor_position_y) - returns 1 float (new_y0)
            :param bottom_drag_function: 3-float input function (current_y0, current_y1, cursor_position_y) - returns 1 float (new_y1)
            :param box_drag_function: function to control box motion - inputs and outputs depend on box_draggable setting
                                if box_draggable == 'both':
                                    inputs (10) : (x0, x1, y0, y1, cursor_x, cursor_y, new_x0, new_x1, new_y0, new_y1)
                                    returns (4) : (new_x0, new_x1, new_y0, new_y1) or None to not do any movement
                                elif box_draggable == 'horizontal':
                                    inputs (5) : (x0, x1, cursor_x, new_x0, new_x1)
                                    returns (2) : (new_x0, new_x1) or None to not do any movement
                                elif box_draggable == 'vertical':
                                    inputs (5) : (y0, y1, cursor_y, new_y0, new_y1)
                                    returns (2) : (new_y0, new_y1) or None to not do any movement
                                else:
                                    box_drag_function will never be called
            :param border_hover: bool - if True, bind edge line hover to fill hover
            :param always_deselect: bool - if True, will deselect upon command even if cursor is hovering
            :param raise_on_click: bool - if True, CanvasEditFill will be raised in canvas whenever it is clicked
            :param bind_center_button: bool - if True, binds mouse center click/drag to the same functions (if any) as mouse left click/drag
            :param active: bool - if False, CanvasEditFill will be unresponsive to user actions, regardless of other settings - for toggling
            :param tag_name: str - tag name given to all canvas items - should be general for items of guitar track, chords track, etc
            :param state: str - state in canvas when item is created - options: ['normal', 'hidden']
        '''
        self.active = active
        self.id = id
        self.canvas = canvas
        self.text_states = ['hidden', 'disabled']
        self.anchors = {'center':'center', 'left':'w', 'right':'e'}
        self.brighten_fact = brighten_fact
        self.corner_line_color = corner_line_color
        self.text_colors = [[text_color, text_select_color], [text_hover_color, text_hover_select_color]]
        self.bg_colors = [[bg, select_color], [brighten(bg, brighten_fact), brighten(select_color, select_brighten_fact)]]
        border_bg = border_color if border_color else bg
        self.border_colors = [[border_bg, select_color], [brighten(border_bg, brighten_fact), brighten(select_color, select_brighten_fact)]]
        if bar_color:
            self.bar_colors = [[bar_color] * 2, [brighten(bar_color, brighten_fact)] * 2]
        else:
            self.bar_colors = [[border_bg, select_color], [brighten(border_bg, brighten_fact), brighten(select_color, select_brighten_fact)]]
        self.selected, self.dragging, self.corner_dragging, self.hovering, self.text_on = False, False, False, False, True
        self.left_draggable, self.right_draggable = left_draggable, right_draggable
        self.top_draggable, self.bottom_draggable = top_draggable, bottom_draggable
        self.left_drag_function, self.right_drag_function = left_drag_function, right_drag_function
        self.top_drag_function, self.bottom_drag_function = top_drag_function, bottom_drag_function
        self.self_select_function, self.self_delete_function = self_select_function, self_delete_function
        self.box_drag_function, self.drag_callback_function = box_drag_function, drag_callback_function
        self.corner_drag_function, self.corner_release_function = corner_drag_function, corner_release_function
        self.x0_lock, self.x1_lock, self.y0_lock, self.y1_lock = x0_lock, x1_lock, y0_lock, y1_lock # used to temporarily lock coordinates
        self.main_text_justify, self.main_text_hover_justify, self.hover_text_justify = main_text_justify, main_text_hover_justify, hover_text_justify
        self.main_font_name, self.main_font_size = main_font_name, main_font_size
        self.hover_font_name, self.hover_font_size = hover_font_name, hover_font_size
        self.main_text, self.hover_text = main_text, hover_text
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if relative_coordinates:
            x0, x1, y0, height = x0 * w, x1 * w, y0 * h, height * h
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y0 + height
        self.rx0, self.rx1, self.ry0, self.ry1 = self.x0 / w, self.x1 / w, self.y0 / h, self.y1 / h
        self.raise_on_click = raise_on_click
        self.always_deselect = always_deselect
        self.box_draggable = box_draggable
        self.selectable = selectable
        self.hoverable = hoverable
        self.connectable = connectable
        self.dot_width = dot_width
        self.line_width = line_width
        self.border_hover = border_hover
        self.tag_name = tag_name
        self.active_bar = active_bar
        self.active_bar_height = active_bar_height * self.active_bar # zero if no active bar

        # Map cursors and motion functions
        self.cursor = 'box' # indicates mode of cursor within rectangle
        self.cursors = {'nw':'dot', 'ne':'dot', 'se':'dot', 'sw':'dot', 'box':'arrow',
                        'top':'sb_v_double_arrow', 'bottom':'sb_v_double_arrow', 'right':'sb_h_double_arrow', 'left':'sb_h_double_arrow'}
        self.motion_functions = {'nw':self.__nw_motion, 'ne':self.__ne_motion, 'se':self.__se_motion, 'sw':self.__sw_motion, 'box':self.__box_motion,
                                    'top':self.__y0_motion, 'bottom':self.__y1_motion, 'right':self.__x1_motion, 'left':self.__x0_motion}

        # tags
        base_tags = [self.tag_name, self.tag_name + '_item', self.id]
        text_tags = base_tags + [self.tag_name + '_text', self.tag_name + '_disabled', self.id + 't']
        hover_text_tags = base_tags + [self.tag_name + '_text', self.tag_name + '_hidden', self.id + 't']
        box_tags = base_tags + [self.tag_name + '_fill', self.id + 'box']
        active_bar_tags = base_tags + [self.tag_name + '_fill', self.tag_name + '_disabled', self.id + 'box']
        disabled_state = 'disabled' if state == 'normal' else state

        # Create Fill and Text objects
        self.box_id = canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1,
                                                width=self.line_width, state=state, tags=box_tags)
        self.active_bar_id = canvas.create_rectangle(self.x0, self.y0 + (self.y1 - self.y0) * (1 - self.active_bar_height),
                                                     self.x1, self.y1, width=0, state=disabled_state, tags=active_bar_tags)

        self.main_text_id = canvas.create_text(self.get_text_x(self.main_text_justify), self.get_text_y(),
                                                text=self.main_text, font=(main_font_name, main_font_size),
                                                anchor=self.anchors[self.main_text_justify], state=disabled_state, tags=text_tags)
        self.hover_text_id = canvas.create_text(self.get_text_x(self.hover_text_justify), self.get_text_y(),
                                                text=self.hover_text, font=(hover_font_name, hover_font_size),
                                                anchor=self.anchors[self.hover_text_justify], state=self.text_states[self.hovering],
                                                tags=hover_text_tags)

        # Bind Events
        self.canvas.tag_bind(self.box_id, '<Motion>', self.__motion)
        if self.hoverable:
            self.canvas.tag_bind(self.box_id, '<Enter>', self.__hover_enter)
            self.canvas.tag_bind(self.box_id, '<Leave>', self.__hover_leave)
        if self.box_draggable != '' or self.selectable:
            self.canvas.tag_bind(self.box_id, '<Button-1>', self.__select_click)
            if bind_center_button:
                self.canvas.tag_bind(self.box_id, '<Button-2>', self.__select_click)
        if self.box_draggable != '':
            self.canvas.tag_bind(self.box_id, '<ButtonRelease-1>', self.__button_release)
            self.canvas.tag_bind(self.box_id, '<B1-Motion>', self.__drag_motion)
            if bind_center_button:
                self.canvas.tag_bind(self.box_id, '<ButtonRelease-2>', self.__button_release)
                self.canvas.tag_bind(self.box_id, '<B2-Motion>', self.__drag_motion)

        if double_click_function:
            self.canvas.tag_bind(self.box_id, "<Double-Button-1>", double_click_function)
        if right_click_function:
            self.canvas.tag_bind(self.box_id, "<Button-3>", right_click_function)
        if center_click_function:
            self.canvas.tag_bind(self.box_id, "<Button-2>", center_click_function)

        self.connections = [] # list of tuples (CanvasEditFill, ConnectionLine)

        self.color_config()

    def get_base_color(self) -> str:
        '''
        returns color for box and borders
        when self.active_bar is True, background will be regular bg and
        border will be selected color
        '''
        return self.bg_colors[self.hovering][not self.active_bar and self.selected]
        
    def get_border_color(self) -> str:
        '''returns border color based on select/hover state'''
        return self.border_colors[self.hovering][self.selected]
    
    def get_bar_color(self) -> str:
        '''returns bar color based on select/hover status'''
        return self.bar_colors[self.hovering][self.selected]

    def get_text_color(self) -> str:
        '''returns the text color based on hover/select status'''
        return self.text_colors[self.hovering][self.selected]

    def get_indicator_color(self) -> str:
        '''returns color for opposite of selection status'''
        return self.bg_colors[self.hovering][not self.selected]
    
    def get_bg_color(self) -> str:
        '''returns background color - regardless of hover/select status'''
        return self.bg_colors[0][0]
    
    def get_selected_color(self) -> str:
        '''returns color when selected - regardless of hover status'''
        return self.bg_colors[0][1]

    def get_text_x(self, justify:str) -> float:
        '''justify options: ['center', 'left', 'right']'''
        if justify == 'left':
            return self.x0
        elif justify == 'right':
            return self.x1
        elif justify == 'center':
            return self.x0 + (self.x1 - self.x0) / 2

    def get_text_y(self) -> float:
        '''returns text center height as float'''
        if self.selected and self.active_bar:
            return self.y0 + (self.y1 - self.y0) * (1 - self.active_bar_height) / 2
        else:
            return self.y0 + (self.y1 - self.y0) / 2

    def set_active(self):
        '''sets state to active so that user interactions proceed as normal'''
        self.active = True

    def set_inactive(self):
        '''sets state to inactive so that CanvasEditFill is unresponsive to user interactions'''
        self.active = False

    def set_color(self, color:str, and_border=True):
        '''set fill color (when not selected)'''
        self.bg_colors[0][0], self.bg_colors[1][0] = color, brighten(color, self.brighten_fact)
        if and_border:
            self.border_colors[0][0], self.border_colors[1][0] = color, brighten(color, self.brighten_fact)
        self.color_config()

    def set_bar_color(self, color=None):
        '''
        sets bar color
        if color is None, changes bar color to the same as border color
        '''
        if color:
            self.bar_colors = [[color] * 2, [brighten(color, self.brighten_fact)] * 2]
        else:
            self.bar_colors = [c[:] for c in self.border_colors] # deep copy
        self.color_config()

    def set_main_text(self, text:str):
        '''update main text'''
        self.main_text = text
        self.canvas.itemconfig(self.main_text_id, text=self.main_text)

    def set_hover_text(self, text:str):
        '''update hover text'''
        self.hover_text = text
        self.canvas.itemconfig(self.hover_text_id, text=self.hover_text)

    def add_connection(self, Item, Line):
        '''Line (ConnectionLine) binds self to Item (CanvasEditFill)'''
        self.connections.append((Item, Line))
        self.color_config()

    def remove_connection(self, Line):
        '''removes the given connection line'''
        self.connections = [tup for tup in self.connections if tup[1] != Line]
        self.color_config()

    def location_config(self, callback=False):
        '''
        moves box, border lines, and text according to self.x0, self.x1, self.y0, and self.y1
        called when position is set using one of the self.set* functions or some part of the objects is dragged
        callback should only be True when location_config is called from an internal drag function
        '''
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.rx0, self.rx1, self.ry0, self.ry1 = self.x0 / w, self.x1 / w, self.y0 / h, self.y1 / h
        self.canvas.coords(self.box_id, self.x0, self.y0, self.x1, self.y1)
        self.canvas.coords(self.active_bar_id, self.x0, self.y0 + (self.y1 - self.y0) * (1 - self.active_bar_height), self.x1, self.y1)
        self.text_move(compute_coords=False)
        for connection in self.connections:
            connection[1].location_config()
        if callback and self.drag_callback_function:
            self.drag_callback_function(self)

    def color_config(self):
        '''changes fill and text color based on hover and select status'''
        self.canvas.itemconfig(self.box_id, fill=self.get_base_color(), outline=self.get_border_color())
        self.canvas.itemconfig(self.active_bar_id, fill=self.get_bar_color())
        self.canvas.itemconfig(self.id + 't', fill=self.get_text_color()) # text color

    def text_move(self, compute_coords=True):
        '''called whenever borders move or hover changes to move text according to borders and hover status'''
        if compute_coords:
            self.x0, self.y0, self.x1, self.y1 = self.canvas.coords(self.box_id)
        if self.hovering or self.dragging:
            self.canvas.coords(self.main_text_id, self.get_text_x(self.main_text_hover_justify), self.get_text_y())
        else:
            self.canvas.coords(self.main_text_id, self.get_text_x(self.main_text_justify), self.get_text_y())
        self.canvas.coords(self.hover_text_id, self.get_text_x(self.hover_text_justify), self.get_text_y())


    def __motion(self, event, update_cursor=False):
        '''cursor moves on item while no buttons are depressed'''
        if not self.active:
            return
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.remember_coords() # sets self.x0, self.y0, self.x1, and self.y1
        if self.connectable and x < self.x0 + self.dot_width and y < self.y0 + self.dot_width: # top left corner
            cursor = 'nw'
        elif self.connectable and x > self.x1 - self.dot_width and y < self.y0 + self.dot_width: # top right corner
            cursor = 'ne'
        elif self.connectable and x > self.x1 - self.dot_width and y > self.y1 - self.dot_width: # bottom right corner
            cursor = 'se'
        elif self.connectable and x < self.x0 + self.dot_width and y > self.y1 - self.dot_width: # bottom left corner
            cursor = 'sw'
        elif self.top_draggable and not self.y0_lock and y < self.y0 + self.line_width: # top edge
            cursor = 'top'
        elif self.right_draggable and not self.x1_lock and x > self.x1 - self.line_width: # right edge
            cursor = 'right'
        elif self.bottom_draggable and not self.y1_lock and y > self.y1 - self.line_width: # bottom edge
            cursor = 'bottom'
        elif self.left_draggable and not self.x0_lock and x < self.x0 + self.line_width: # left edge
            cursor = 'left'
        else: # inside box
            cursor = 'box'
        if update_cursor or cursor != self.cursor:
            self.canvas.config(cursor=self.cursors[cursor])
        self.cursor = cursor

    def __hover_enter(self, event=None):
        '''cursor hovers on item - change box and lines to hover colors'''
        if not self.active:
            return
        self.hovering = True
        if not self.dragging:
            self.color_config()
            self.text_move()
            self.canvas.itemconfig(self.main_text_id, anchor=self.anchors[self.main_text_hover_justify]) # main text justify
            self.canvas.itemconfig(self.hover_text_id, state=self.text_states[self.hovering])
            if event != None:
                self.__motion(event, update_cursor=True)

    def __hover_leave(self, event=None):
        '''cursor leaves item - change box and lines to regular colors'''
        if not self.active:
            return
        self.hovering = False
        if not self.dragging:
            self.color_config()
            self.text_move()
            self.canvas.itemconfig(self.main_text_id, anchor=self.anchors[self.main_text_justify]) # main text justify
            self.canvas.itemconfig(self.hover_text_id, state=self.text_states[self.hovering])
            self.canvas.config(cursor=self.cursors['box'])

    def __select_click(self, event):
        '''cursor clicks on item'''
        if not self.active:
            return
        if self.cursor in ['nw', 'ne', 'se', 'sw']:
            self.__corner_click(event)
            return None
        if self.selectable and not self.selected and self.self_select_function:
            self.self_select_function(self)
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.selected, self.dragging = self.selectable, True
        self.cursor_dist_x, self.cursor_dist_y = x - self.x0, y - self.y0 # relative cursor position inside box
        self.color_config()
        self.text_move()
        if self.raise_on_click:
            self.canvas.tag_raise(self.id)

    def __button_release(self, event):
        '''cursor releases click on item'''
        if not self.active:
            return
        if self.cursor in ['nw', 'ne', 'se', 'sw']:
            self.__corner_release(event)
            return None
        self.dragging = False
        if not self.hovering:
            self.__hover_leave()

    def __corner_click(self, event):
        '''cursor clicks on one of four corner dots'''
        self.corner_dragging = True
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.corner_line_id = self.canvas.create_line(x, y, x, y, fill=self.corner_line_color, width=2, state='normal')

    def __corner_release(self, event):
        '''cursor releases click on one of four corner dots'''
        self.corner_dragging = False
        self.canvas.delete(self.corner_line_id)
        if self.corner_release_function:
            self.corner_release_function(self, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))


    def __drag_motion(self, event):
        '''
        master drag function called whenever any part of the box is dragged
        calls the appropriate internal drag function based on cursor status
        '''
        if self.active:
            self.motion_functions[self.cursor](event)

    def __box_motion(self, event):
        '''drag entire box - self.box_draggable will be in ['horizontal', 'vertical', 'both']'''
        if self.box_draggable == '': # box is not draggable so do nothing
            return
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.remember_coords()
        width, height = self.x1 - self.x0, self.y1 - self.y0
        new_x0, new_y0 = x - self.cursor_dist_x, y - self.cursor_dist_y
        new_x1, new_y1 = new_x0 + width, new_y0 + height
        if self.box_draggable == 'both':
            if self.box_drag_function:
                box_drag_result = self.box_drag_function(self.x0, self.x1, self.y0, self.y1, x, y, new_x0, new_x1, new_y0, new_y1)
                if box_drag_result == None:
                    return None
                x0, x1, y0, y1 = box_drag_result
                if not self.x0_lock and not self.x1_lock:
                    self.x0, self.x1 = x0, x1
                if not self.y0_lock and not self.y1_lock:
                    self.y0, self.y1 = y0, y1
            else:
                if not self.x0_lock and not self.x1_lock:
                    self.x0, self.x1 = new_x0, new_x1
                if not self.y0_lock and not self.y1_lock:
                    self.y0, self.y1 = new_y0, new_y1
        elif self.box_draggable == 'horizontal' and not self.x0_lock and not self.x1_lock: # only move x if not locked
            if self.box_drag_function:
                box_drag_result = self.box_drag_function(self.x0, self.x1, x, new_x0, new_x1)
                if box_drag_result == None:
                    return None
                self.x0, self.x1 = box_drag_result
            else:
                self.x0, self.x1 = new_x0, new_x1
        elif self.box_draggable == 'vertical' and not self.y0_lock and not self.y1_lock: # only move y if not locked
            if self.box_drag_function:
                box_drag_result = self.box_drag_function(self.y0, self.y1, y, new_y0, new_y1)
                if box_drag_result == None:
                    return None
                self.y0, self.y1 = box_drag_result
            else:
                self.y0, self.y1 = new_y0, new_y1        
        #self.cursor_dist_x, self.cursor_dist_y = x - self.x0, y - self.y0 # not sure if this should be done
        self.location_config(callback=True)

    def __x0_motion(self, event):
        '''left edge is dragged'''
        x = self.canvas.canvasx(event.x)
        self.remember_coords()
        if self.left_drag_function:
            self.x0 = self.left_drag_function(self.x0, self.x1, x)
        else:
            self.x0 = x
        self.location_config(callback=True)

    def __x1_motion(self, event):
        '''right edge is dragged'''
        x = self.canvas.canvasx(event.x)
        self.remember_coords()
        if self.right_drag_function:
            self.x1 = self.right_drag_function(self.x0, self.x1, x)
        else:
            self.x1 = x
        self.location_config(callback=True)

    def __y0_motion(self, event):
        '''top edge is dragged'''
        y = self.canvas.canvasy(event.y)
        self.remember_coords()
        if self.top_drag_function:
            self.y0 = self.top_drag_function(self.y0, self.y1, y)
        else:
            self.y0 = y
        self.location_config(callback=True)

    def __y1_motion(self, event):
        '''bottom edge is dragged'''
        y = self.canvas.canvasy(event.y)
        self.remember_coords()
        if self.bottom_drag_function:
            self.y1 = self.bottom_drag_function(self.y0, self.y1, y)
        else:
            self.y1 = y
        self.location_config(callback=True)

    def __nw_motion(self, event):
        '''top left corner dot is dragged'''
        self.remember_coords()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.coords(self.corner_line_id, self.x0, self.y0, x, y)
        if self.corner_drag_function:
            self.corner_drag_function(x, y)

    def __ne_motion(self, event):
        '''top right corner dot is dragged'''
        self.remember_coords()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.coords(self.corner_line_id, self.x1, self.y0, x, y)
        if self.corner_drag_function:
            self.corner_drag_function(x, y)

    def __se_motion(self, event):
        '''bottom right corner dot is dragged'''
        self.remember_coords()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.coords(self.corner_line_id, self.x1, self.y1, x, y)
        if self.corner_drag_function:
            self.corner_drag_function(x, y)

    def __sw_motion(self, event):
        '''bottom left corner dot is dragged'''
        self.remember_coords()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.coords(self.corner_line_id, self.x0, self.y1, x, y)
        if self.corner_drag_function:
            self.corner_drag_function(x, y)


    def get_x0(self) -> float:
        '''cannot simply get self.x0 because values may have changed do to zoom in or zoom out'''
        return self.canvas.coords(self.box_id)[0]

    def get_x1(self) -> float:
        '''returns the right edge of item'''
        return self.canvas.coords(self.box_id)[2]

    def get_y0(self) -> float:
        '''returns the top edge of item'''
        return self.canvas.coords(self.box_id)[1]

    def get_y1(self) -> float:
        '''returns the bottom edge of item'''
        return self.canvas.coords(self.box_id)[3]

    def get_x_center(self):
        '''returns the x coordinate of item center point'''
        x0, _, x1, _ = self.canvas.coords(self.box_id)
        return x0 + (x1 - x0) / 2

    def get_y_center(self):
        '''returns the y coordinate of item center point'''
        _, y0, _, y1 = self.canvas.coords(self.box_id)
        return y0 + (y1 - y0) / 2

    def get_coords(self):
        '''returns box position in canvas (x0, y0, x1, y1)'''
        return self.canvas.coords(self.box_id)

    def get_relative_coords(self):
        '''
        returns (x0, y0, x1, y1) coordinates as a percentage of canvas width and height
        only works when canvas is not being scrolled or zoomed
        '''
        x0, y0, x1, y1 = self.canvas.coords(self.box_id)
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        return x0 / w, y0 / h, x1 / w, y1 / h

    def get_last_coords(self):
        '''
        returns coordinates (x0, y0, x1, y1) stored in self without checking canvas
        if canvas has been resized or scaled, coordinates will be wrong
        '''
        return self.x0, self.y0, self.x1, self.y1

    def get_last_relative_coords(self):
        '''
        returns relative coordinates (x0, y0, x1, y1) stored in self without checking canvas
        if canvas has be resized or scaled, coordinates will be wrong
        '''
        return self.rx0, self.ry0, self.rx1, self.ry1

    def remember_coords(self):
        '''sets coords internally from canvas'''
        self.x0, self.y0, self.x1, self.y1 = self.get_coords()


    def set_x0(self, x0):
        '''does exactly what the function name implies'''
        self.remember_coords()
        self.x0 = x0
        self.location_config()

    def set_x1(self, x1):
        '''does exactly what the function name implies'''
        self.remember_coords()
        self.x1 = x1
        self.location_config()

    def set_y0(self, y0):
        '''does exactly what the function name implies'''
        self.remember_coords()
        self.y0 = y0
        self.location_config()

    def set_y1(self, y1):
        '''does exactly what the function name implies'''
        self.remember_coords()
        self.y1 = y1
        self.location_config()

    def set_x_coords(self, x0, x1):
        '''sets x coordinates'''
        _, self.y0, _, self.y1 = self.canvas.coords(self.box_id)
        self.x0, self.x1 = x0, x1
        self.location_config()

    def set_y_coords(self, y0, y1):
        '''sets y coordinates'''
        self.x0, _, self.x1, _ = self.canvas.coords(self.box_id)
        self.y0, self.y1 = y0, y1
        self.location_config()

    def set_relative_x_coords(self, x0, x1):
        '''
        takes as input x0 and x1 coordinates as percentages of canvas width
        ONLY works when canvas is not being scrolled or zoomed
        '''
        self.set_x_coords(x0 * self.canvas.winfo_width(), x1 * self.canvas.winfo_width())

    def set_relative_y_coords(self, y0, y1):
        '''
        takes as input y0 and y1 coordinates as percentages of canvas height
        ONLY works when canvas is not being scrolled or zoomed
        '''
        self.set_y_coords(y0 * self.canvas.winfo_height(), y1 * self.canvas.winfo_height())

    def set_coords(self, x0:float, y0:float, x1:float, y1:float):
        '''sets item coordinates in parent canvas'''
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.location_config()

    def set_relative_coords(self, x0:float, y0:float, x1:float, y1:float):
        '''
        takes as input coordinates as percentages of canvas width and height
        ONLY works when canvas is not being scrolled or zoomed
        '''
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.set_coords(x0 * w, y0 * h, x1 * w, y1 * h)

    def move_x(self, x_increment):
        '''moves item in x dimension by a given increment'''
        self.remember_coords()
        self.x0, self.x1 = self.x0 + x_increment, self.x1 + x_increment
        self.location_config()    

    def move_y(self, y_increment):
        '''moves item in y dimension by a given increment'''
        self.remember_coords()
        self.y0, self.y1 = self.y0 + y_increment, self.y1 + y_increment
        self.location_config()


    def overlaps_rectangle(self, rx0:float, rx1:float, ry0:float, ry1:float) -> bool:
        '''returns True if rectangle define by x0, x1, y0, y1 overlaps with Item'''
        x0, y0, x1, y1 = self.canvas.coords(self.box_id)
        return max(rx0, rx1) > x0 and min(rx0, rx1) < x1 and max(ry0, ry1) > y0 and min(ry0, ry1) < y1

    def contains_point(self, x, y) -> bool:
        '''returns True if (x, y) is within the bounds of this Item'''
        x0, y0, x1, y1 = self.get_coords()
        return x > x0 and x < x1 and y > y0 and y < y1

    def connected_left(self) -> bool:
        '''returns True if Item is connected to an Item to the left'''
        if len(self.connections) == 0:
            return False
        return max([tup[0].get_x0() < self.get_x0() for tup in self.connections])

    def connected_right(self) -> bool:
        '''returns True if Item is connected to an Item to the right'''
        if len(self.connections) == 0:
            return False
        return max([tup[0].get_x1() > self.get_x1() for tup in self.connections])

    def raise_fill(self):
        '''raises CanvasEditFill within parent canvas'''
        self.canvas.tag_raise(self.id)

    def select(self):
        '''select item'''
        if not self.selected and self.selectable:
            self.selected = True
            self.color_config()
            self.text_move()
            self.canvas.tag_raise(self.id)

    def deselect(self, override=False):
        '''if override is True, will deselect even if hovering'''
        if self.selected and (not self.hovering or self.always_deselect or override):
            self.selected = False
            self.color_config()
            self.text_move()

    def self_delete(self):
        '''delete from popup menu'''
        if self.self_delete_function:
            self.self_delete_function(self)
        self.delete()

    def delete(self):
        '''delete item and all connections'''
        for connection in self.connections:
            connection[1].delete()
        self.canvas.delete(self.id)
