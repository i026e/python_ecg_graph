#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 09:28:11 2016

@author: pavel
"""
import global_settings as settings
import parameter_types as prm

class PlotterSettingsManager(prm.ParameterManager):
    COLOR_NAME_V = "color A" # for correct values
    COLOR_NAME_E = "color B" # for wrong values
    REDRAW_CHUNK_SIZE = "samples to redraw"
    
    def __init__(self):
        super(PlotterSettingsManager, self).__init__()
        self.color_V = prm.ListParameter(self.COLOR_NAME_V, settings.VALID_COLOR_NAME, 
                                     str, settings.GRAPH_COLORS.keys())
        self.color_E = prm.ListParameter(self.COLOR_NAME_E, settings.ERROR_COLOR_NAME, 
                                     str, settings.GRAPH_COLORS.keys())
        self.chunk_size = prm.Parameter(self.REDRAW_CHUNK_SIZE, 
                                        settings.NUM_ENTRIES_BEFORE_PLOT, int)
        self.add_param(self.COLOR_NAME_V, self.color_V)
        self.add_param(self.COLOR_NAME_E, self.color_E)
        self.add_param(self.REDRAW_CHUNK_SIZE, self.chunk_size)
        
    def get_valid_color(self):
        return self.color_V.get_val()
    def get_invalid_color(self):
        return self.color_E.get_val()  
    def redraw_after_samples(self):
        return self.chunk_size.get_val()

class Plotter(object):
    def __init__(self, graph):
        self.graph = graph
        self.settings_mgr = PlotterSettingsManager()
        
        self.xVal = self.yVal = 0
        self.before_redraw = self.settings_mgr.redraw_after_samples()

    def plot_valid(self, val):
        self._plot(self.settings_mgr.get_valid_color(), int(round(val)))
    def plot_error(self, *val):
        #plot old value
        self._plot(self.settings_mgr.get_invalid_color(), self.yVal)
    def _plot(self, color_name, yVal) : 
        self._cls()
        
        self.graph.add_line(color_name, self.xVal, self.yVal, self.xVal+1, yVal)
        self.xVal += 1
        self.yVal = yVal
        
        self._redraw()
    def _cls(self):
        if self.xVal >= self.graph.get_width():
            self.xVal = 0
            self.graph.clear_screen()
    def _redraw(self):        
        if self.before_redraw <= 0:
            self.before_redraw = self.settings_mgr.redraw_after_samples()

            
            self.graph.update_screen()
        else:
            self.before_redraw -= 1
