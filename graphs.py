#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 08:18:51 2016

@author: pavel
"""
import Queue

class GTK_Graph:
    class Color:
        def __init__(self, (r, g, b)):
            self.r = r
            self.g = g
            self.b = b
    
    def __init__(self, drawingArea, colors, yMin, yMax):
        """drawingArea: gtk drawingArea
        colors: dict of color_name : GTK_Graph_Color
        yMin, yMax: min and max values y can take (needed for proper scaling)
        """
        self.drawingArea = drawingArea
        self.colors = colors
        
        self.queues = {}
        self.pathes = {}
        for color_name in colors.keys():
            self.queues[color_name] = Queue.Queue()
            self.pathes[color_name] = None
       
        self.drawingArea.connect("configure-event", self.on_configure)
        self.drawingArea.connect("draw", self.draw)
        
        self.scale_coef = 1.0
        self.area_width = self.area_height = 0

        self.yMin, self.yMax = yMin, yMax
        
        
    def show(self):
        #glib.timeout_add(100, self.on_timer)
        pass
    def hide(self):
        pass
    def add_line(self, color_name, x1, y1, x2, y2):
        if color_name in self.colors:
            self.queues[color_name].put( (x1, self.scale_data(y1), 
                                        x2, self.scale_data(y2)) )
        
    def update_screen(self):
        self.drawingArea.queue_draw()
    def clear_screen(self):
        for path_name in self.pathes.keys():
            self.pathes[path_name] = None

    def on_configure(self, widget, event):
        #x, y, width, height = widget.get_allocation()
        self.area_width = widget.get_allocation().width
        self.area_height = widget.get_allocation().height
        
        self.scale_coef = 1.0 * self.area_height / (self.yMax - self.yMin)
        
        print("graph was resized to " + 
                    str(self.area_width) + 'x' + str(self.area_height))
        
    def get_width(self):
        return self.area_width
    def get_height(self):
        return self.area_height
    def draw(self, widget, event):
        cr = widget.get_property('window').cairo_create()
        cr.set_line_width(1)
        
        for color_name in self.colors:
            color = self.colors[color_name]
            cr.set_source_rgb(color.r, color.g, color.b) #set color
            
            if self.pathes[color_name] is not None:
                cr.append_path(self.pathes[color_name]) #restore prev drawn line
                
            # draw new lines    
            while not self.queues[color_name].empty():
                (x1, y1, x2, y2) = self.queues[color_name].get()
                cr.move_to(x1, y1)
                cr.line_to(x2, y2)
            self.pathes[color_name] = cr.copy_path_flat()
            cr.stroke()
   
    def scale_data(self, value):
        return round(value * self.scale_coef)
        
        
