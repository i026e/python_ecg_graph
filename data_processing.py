#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 11:46:50 2016

@author: pavel
"""
import math
import time
from datetime import datetime

import settings


class CircularBuffer:
        def __init__(self, size):
            self.array = range(size)
            self.full = False
            self.size = size

            self.pointer = 0
            
        def is_full(self):
            return self.full
        def write(self, val):
            #check if point to last +1 entry in array
            if self.pointer == self.size:
                self.pointer = 0 #override the data
                self.full = True
            self.array[self.pointer] = val
            self.pointer += 1
        def clear(self):
            self.pointer = 0
            self.full = False
        def get_entry(self, index):
            """index: positive integer to LIFO entry
            1 - last entry
            2 - entry before last etc
            """
            if (index < 1) or (index > self.size) or (not self.full and index > self.pointer):
                return None
            index = (self.pointer - index) % self.size
            return self.array[index]
        def all_entries(self):
            """get data as it was added (FIFO)"""
            
            #data stored in reversed order
            index = self.pointer - 1
            while index >= 0:
                yield self.array[index]
                index -= 1
            if self.full:
                index = self.size - 1
                while index >= self.pointer:
                    yield self.array[index]
                    index -= 1
            
class Filter:
    #http://dsp.stackexchange.com/a/25679
    def __init__(self, fs, f, r):
        """fs = sampling frequency
            f = notch frequency
            r = sharpness, 0..1 excluding 1
        """        
        z1x = math.cos(2*math.pi*f/fs)
        self.a0a2 = (1.0 - r)*(1.0 - r)/(2.0*(abs(z1x) + 1.0)) + r
        self.a1 = -2.0*z1x*self.a0a2
        self.b1 = 2.0*z1x*r
        self.b2 = -r*r
        
        self.in_buffer = CircularBuffer(2)
        self.out_buffer = CircularBuffer(2)
        
    def filtered(self, val):
        """ apply filter to value"""
        new_val = val
        if self.out_buffer.is_full():
            new_val = ( self.a0a2*(val + self.in_buffer.get_entry(2)) +
                        self.a1*self.in_buffer.get_entry(1) + 
                        self.b1*self.out_buffer.get_entry(1) + 
                        self.b2*self.out_buffer.get_entry(2) )
                
            
        self.in_buffer.write(val)
        self.out_buffer.write(new_val)
        return new_val
        
class AdjustableFilter:
    """posible to change parameters of filter"""
    
    def __init__(self, freq, roughness):
        self.freq = freq
        self.roughness = roughness
        
        self.sampl_freq = 1.0 # not yet known
        self.sampl_freq_known = False
        self.countdown = settings.SAMPLS_TO_MEASURE_SAMPL_RATE
        self.measure_start_time = 0
        
        self.in_buffer = CircularBuffer(2)
        self.out_buffer = CircularBuffer(2)
        
    def filtered(self, val):
        new_val = val
        if self.out_buffer.is_full() and self.sampl_freq_known:
            new_val = ( self.a0a2*(val + self.in_buffer.get_entry(2)) +
                        self.a1*self.in_buffer.get_entry(1) + 
                        self.b1*self.out_buffer.get_entry(1) + 
                        self.b2*self.out_buffer.get_entry(2) )
            #print(val, new_val)
            
        else:
            #measure time for SAMPLES_TO_MEASURE_FREQ samples
            if self.countdown == settings.SAMPLS_TO_MEASURE_SAMPL_RATE:
                self.measure_start_time = time.time()
            elif self.countdown <= 0:
                self._calc_sampl_freq()
                
            self.countdown -= 1    
        self.in_buffer.write(val)
        self.out_buffer.write(new_val)
        return int(round(new_val))
        
    def set_roughness(self, roughness):
        self.roughness = roughness
        self._init_values()
    
    def get_freq(self):
        return self.freq
    def set_freq(self, freq):
        self.freq = freq
        self._init_values()
        
    def reset_sampling_freq(self):
        self.sampl_freq_known = False
        self.countdown = settings.SAMPLS_TO_MEASURE_SAMPL_RATE
        
    def _calc_sampl_freq(self):
        self.sampl_freq_known = True
        time_interval = time.time() - self.measure_start_time # seconds
        print("time for " + str(settings.SAMPLS_TO_MEASURE_SAMPL_RATE) +
                 " samples : " + str(time_interval) + " seconds")
        self.sampl_freq = (settings.SAMPLS_TO_MEASURE_SAMPL_RATE 
                                                    / time_interval) # Hz
        self._init_values()
    def _init_values(self):
        z1x = math.cos(2*math.pi*self.freq/self.sampl_freq)
        self.a0a2 = (1.0 - self.roughness)*(1.0 - self.roughness)/(2.0*(abs(z1x) + 1.0)) + self.roughness
        self.a1 = -2.0*z1x*self.a0a2
        self.b1 = 2.0*z1x*self.roughness
        self.b2 = -self.roughness*self.roughness
        
        
class DataProcessor:
    def __init__(self, output_graph, valid_color_name, error_color_name, 
                 do_filtering, filter_freq, filter_roughness): 
        """
        do_filtering: boolean should filter be used  
        filter_freq: frequency to supress        
        filter_roughness: filter strength in [0,1)
        
        output_graph: Graph obj
        valid_color_name = color name for valid data
        error_color_name = color name for invalid data 
        """
        self.graph = output_graph
        self.val_col_nm = valid_color_name
        self.err_color_nm = error_color_name
        
        self.data_to_export = CircularBuffer(settings.NUM_ENTRIES_TO_EXPORT)      
        
        self.lastX = self.lastY = 0
        self.samples_before_plotting = settings.NUM_ENTRIES_BEFORE_PLOT
        
        self.busy_flag = False
        self.filtering_flag = do_filtering
        
        self.filter = AdjustableFilter(filter_freq, filter_roughness)
        
    def new_data(self, data):
        """ data : string of from input """
        
        if data is not None and not self.busy_flag:
        # process only if real data
        # skip data if busy
            self.busy_flag = True
            
            line = data.strip()
            if len(line) > 0:                
                try:
                    #integer value received
                    y = int(line)
                    
                    if self.filtering_flag:
                        y = self.filter.filtered(y)
                        
                    self.graph.add_line(self.val_col_nm, 
                                        self.lastX, self.lastY, 
                                        self.lastX+1, y)
                    self.lastY = y
                    self.data_to_export.write(y)
                except ValueError:                        
                    # non integer value
                    self.graph.add_line(self.err_color_nm, 
                                    self.lastX, self.lastY, 
                                    self.lastX+1, self.lastY)
                except:
                    print("unexpected value " + str(y))
            
            self.lastX += 1
            self.samples_before_plotting -= 1
            
            if (self.samples_before_plotting <= 0):
                self.redraw_graph()
                
            self.busy_flag = False
    def enable_filter(self):
        self.filtering_flag = True
    def disable_filter(self):
        self.filtering_flag = False
        
    def get_filter_freq(self):
        return self.filter.get_freq()
    def set_filter_freq(self, new_freq):
        self.filter.set_freq(new_freq)
    def set_filter_roughness(self, roughness):
        self.filter.set_roughness(roughness)
    def reset_filter_sampl_freq(self):
        self.filter.reset_sampling_freq()
        
    def redraw_graph(self):
        self.samples_before_plotting = settings.NUM_ENTRIES_BEFORE_PLOT
        self.graph.update_screen()
        
        if self.lastX > self.graph.get_width():
            self.lastX = 0
            self.graph.clear_screen()
    def get_export_data(self):
        while self.busy_flag:
            time.sleep(settings.SLEEP_INTERVAL)
        self.busy_flag = True
        
        # create new circular buffer
        tmp_data = self.data_to_export
        self.data_to_export = CircularBuffer(settings.NUM_ENTRIES_TO_EXPORT)
        self.busy_flag = False      

        return tmp_data
    def disable_accepting_data(self):
        self.busy_flag = True
    def enable_accepting_data(self):
        self.busy_flag = False
        self.reset_filter_sampl_freq()

class FileProcessor:
    def __init__(self):
        date = datetime.now()
        self.filename = (date.strftime(settings.FILENAME_DATE_FORMAT) +
                                        settings.FILENAME_EXTENSION)  
    def get_name(self):
        return self.filename
    def set_name(self, new_name):
        self.filename = new_name
        print("new filename: " + new_name)
    def do_export(self, data_processor, onError):
        try:            
            f_obj = open(self.filename, 'w')
            circ_buffer = data_processor.get_export_data()
            
            index = 0
            for entry in circ_buffer.all_entries():
                line = str(index) + settings.CSV_SEPARATOR + str(entry)
                f_obj.write(line + settings.CSV_LINE_TERMINATOR)
                index += 1
            
            f_obj.close()
            
        except Exception as e:
            f_obj.close()
            onError(str(e))
        
        
        