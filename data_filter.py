#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 08:11:58 2016

@author: pavel
"""
import math
import time

import global_settings as settings
import parameter_types as prm
from data_storage import CircularBuffer

class FilterSettingsManager(prm.ParameterManager):
    ALLOWED = "allowed"
    def __init__(self, param_changed_cb=None):
        super(FilterSettingsManager, self).__init__(param_changed_cb)
        
        self.allowed = prm.BoolParameter(self.ALLOWED, settings.USE_FILTER)
        self.add_param(self.ALLOWED, self.allowed)
    def is_allowed(self):
        return self.allowed.get_val()

class FreqFilterSettingsManager(FilterSettingsManager):
    FS = "sampling freq"
    FREQ = "freq"
    
    def __init__(self, param_changed_cb=None):
        super(FreqFilterSettingsManager, self).__init__(param_changed_cb)
        
        self.sampling_freq = prm.Parameter(self.FS, settings.FILTER_SAMPLING_FREQ, float)
        self.freq = prm.Parameter(self.FREQ, settings.FILTER_FREQ, float)        
        
        self.add_param(self.FS, self.sampling_freq)
        self.add_param(self.FREQ, self.freq)
        
    def get_smpl_freq(self):
        return self.sampling_freq.get_val()
    def get_freq(self):
        return self.freq.get_val()


class SimpleNotchFilterSettingsManager(FreqFilterSettingsManager):
    SHARPNESS = "sharpness" # [0..1)
    def __init__(self, param_changed_cb):
        super(SimpleNotchFilterSettingsManager, self).__init__(param_changed_cb)
        
        self.sharpness = prm.RangeParameter(self.SHARPNESS, 
                                            settings.FILTER_STRENGTH, float, 0.0, 0.99)
        self.add_param(self.SHARPNESS, self.sharpness)
    def get_sharpness(self):
        return self.sharpness.get_val()    
        

class AdjNotchFilterSettingsManager(SimpleNotchFilterSettingsManager):
    SAMPLES = "samples" #to measure time
    def __init__(self, param_changed_cb):
        super(AdjNotchFilterSettingsManager, self).__init__(param_changed_cb)
        
        self.samples_to_measure = prm.Parameter(self.SAMPLES, 
                                            settings.SAMPLS_TO_MEASURE_SAMPL_RATE, int)
        self.add_param(self.SAMPLES, self.samples_to_measure)
    def get_samples(self):
        return self.samples_to_measure.get_val()
    def set_sampling_freq(self, new_val):
        return self.sampling_freq.set_val(new_val)

class InvertorSettingsManager(FilterSettingsManager):
    INVERSION_VAL = "inversion point" # max possible value of data entry
    
    def __init__(self):
        super(InvertorSettingsManager, self).__init__()
        self.max_val = prm.Parameter(self.INVERSION_VAL, 
                                               settings.DATA_MAX_VALUE, int)
        self.add_param(self.INVERSION_VAL, self.max_val)                                       
    def max_data_val(self):
        return self.max_val.get_val()

class Filter(object):
    def __init__(self):
        self.settings_mgr = FilterSettingsManager()
        self.name = "filter"
    def get_name(self):
        return self.name
    def settings_manager(self):
        return self.settings_mgr
    def filtered(self, val):
        if self.settings_mgr.is_allowed():
            return self._filtered(val)
        return val      
    # override following method
    def _filtered(self, val):
        return val

class SimpleNotchFilter(Filter):
    #http://dsp.stackexchange.com/a/25679
    def __init__(self):
        #super(SimpleNotchFilter, self).__init__()
        self.name = "Notch Filter"
        self.settings_mgr = SimpleNotchFilterSettingsManager(param_changed_cb = self._compute_params)
        self._compute_params()
        
        self.a0a2, self.a1, self.b1, self.b2 = 0, 0, 0, 0


        self.in_buffer = CircularBuffer(2)
        self.out_buffer = CircularBuffer(2)
        
    def _compute_params(self, *args):
        freq = self.settings_mgr.get_freq()
        sampling_freq = self.settings_mgr.get_smpl_freq()
        r = self.settings_mgr.get_sharpness()
        
        z1x = math.cos(2*math.pi*freq/sampling_freq)
        
        self.a0a2 = (1.0 - r)*(1.0 - r)/(2.0*(abs(z1x) + 1.0)) + r
        self.a1 = -2.0*z1x*self.a0a2
        self.b1 = 2.0*z1x*r
        self.b2 = -r*r
        
        
    def _filtered(self, val):
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

class SelfAdjustableNotchFilter(SimpleNotchFilter):
    """sampling freq is adjusted by the filter itself"""

    def __init__(self):
        super(SelfAdjustableNotchFilter, self).__init__()
        self.settings_mgr = AdjNotchFilterSettingsManager(param_changed_cb = self._compute_params)
        
        
        self.countdown = 0
        self.measurement_start_time = 0

    def _adjust(self):
        current_time = time.time()
        interval = current_time - self.measurement_start_time
        
        sampling_rate = interval*1.0 / self.settings_mgr.get_samples()
        self.settings_mgr.set_sampling_freq(sampling_rate)
        
        
        self.countdown = self.settings_mgr.get_samples()
        self.measurement_start_time = time.time()
        
       
    def _filtered(self, val):
        if self.countdown <= 0:
            self._adjust()
        self.countdown -= 1
        
        return super(SelfAdjustableNotchFilter, self)._filtered(val)
        
class Invertor(Filter):
    def __init__(self):
        #super(Invertor, self).__init__()
        self.name = "Invertor"
        self.settings_mgr = InvertorSettingsManager()
    def _filtered(self, val):
        return self.settings_mgr.max_data_val() - val

