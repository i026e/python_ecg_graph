#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 07:58:34 2016

@author: pavel
"""

import threading, time
import matplotlib.pyplot as plt
import Queue

SLEEP_INTERVAL = 0.01

class AsyncPlotting(threading.Thread):
    def __init__(self, data_queue, width, height, onClose):  
        self.onClose = onClose
        
        self.prevX = self.prevY = 0
        self.width = width
        self.height = height
        
        self.y_data = []
        self.queue = data_queue
       
        self.enabled = False
        super(AsyncPlotting, self).__init__()
    
    def cls(self):
        #plt.cls()
        self.prevX = self.prevY = 0
        self.plot_data_x = [self.prevX]
        self.plot_data_y = [self.prevY]
        
    def run(self):
        self.enabled = True
        
        plt.ion()
        self.figure = plt.figure() 
        
        plt.axis([0,self.width, 0,self.height]) 
        plt.show(block=False)
        
        self.cls()
        self.line, = plt.plot((self.prevX, self.prevY))
        
        #mng = plt.get_current_fig_manager()
        
        while self.prevX < 1000:
        #while self.enabled and plt.get_fignums(): # graph allowed and not closed            
            while not self.queue.empty():
                is_valid, y = self.queue.get()
                if is_valid:
                    self.plot_data_y.append(y)
                    self.plot_data_x.append(self.prevX)
                    self.line.set_data(self.plot_data_x, self.plot_data_y)
                    
                    #plt.plot((self.prevX-1, self.prevY, self.prevX, y))
                    #plt.scatter(self.prevX, y)
                    self.prevX += 1
                    #self.prevY = y
                
                if self.prevX > self.width:
                    self.cls()
            #plt.draw()
            plt.pause(SLEEP_INTERVAL)
            time.sleep(SLEEP_INTERVAL)
            
        self.enabled = False
        plt.clf()
        #plt.ioff()
        plt.close(self.figure)
        self.onClose()
    def stop_plotting(self):
        self.enabled = False
      

class Matplotlib_Graph: 
    WIDTH = 2000
    HEIGHT = 1200
    def __init__(self, onClose):
        self.queue = Queue.Queue()
        self.onGraphClose = onClose
        self.async_plot = None
        self.is_shown = False
    def add_val(self, is_valid, val):
        self.queue.put((is_valid, val))
    def show(self):
        if not self.is_shown:
            self.is_shown = True
            self.async_plot = AsyncPlotting(self.queue, 
                                        Matplotlib_Graph.WIDTH, 
                                        Matplotlib_Graph.HEIGHT, 
                                        self.onGraphClose)
            self.async_plot.start()
    def hide(self):
        if self.is_shown:
            self.is_shown = False
            self.async_plot.stop_plotting()
            #self.async_plot = None