#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 16:25:41 2016

@author: pavel
"""
from gi.repository import Gtk

import parameter_types as ptypes

from logger import Logger

logger = Logger.get_logger()


#
import gobject
gobject.threads_init()
 
#decorator is used to update gtk objects from another thread 
def idle_add_decorator(func):
    def callback(*args):
        gobject.idle_add(func, *args)
    return callback

class GTK_Wrapper(object):    
    def get_gui_object(self):
        raise NotImplementedError()
        
    @staticmethod
    def get_wrapper(obj):        
        wrapper = TYPE_MATCHES.get(type(obj), GTK_ReadOnlyWrapper)
        return wrapper(obj)
        

class GTK_ReadOnlyWrapper(GTK_Wrapper):
    def __init__(self, obj):
        self.label = Gtk.Label()
        self.label.set_text(repr(obj))
    
    def get_gui_object(self):
        return self.label    


class GTK_ParamWrapper(GTK_Wrapper):
    def __init__(self, parameter):
        self.parameter = parameter
        self.container = Gtk.Box(spacing=2)      
        self.container.set_homogeneous(False)
        
        self._set_name(parameter.get_name())
        
        
        self.param_gui_obj = None
        self._set_gui_obj()
        
        self._append_gui_obj()
        
        
    def get_gui_object(self):
        return self.container
    
    def _set_name(self, name):
        name_label = Gtk.Label()
        name_label.set_text(name)
        self.container.pack_start(name_label, True, True, 0)
    def _append_gui_obj(self):
        if self.param_gui_obj is not None:
            self.container.pack_start(self.param_gui_obj, True, True, 0)  
            self.param_gui_obj.set_hexpand(True)
        
    #override this with obj and add call 
        # also set on update callback    
    def _set_gui_obj(self):
        self.param_gui_obj = None
        
    
    # override this with method  
    def _on_update(self, widget, parameter_obj):
        logger.to_log(widget, parameter_obj)    
    

class GTK_ParamCheckBtn(GTK_ParamWrapper):
    def _set_gui_obj(self): 
        self.param_gui_obj = Gtk.CheckButton()
        self.param_gui_obj.set_active(self.parameter.get_val())
        self.param_gui_obj.connect("toggled", self._on_update, self.parameter)
    def _on_update(self, widget, param):
        new_val = widget.get_active()
        param.set_val(new_val)


class GTK_ParamTextBox(GTK_ParamWrapper):
    def _set_gui_obj(self):    
        self.param_gui_obj = Gtk.Entry()
        self.param_gui_obj.set_text(str(self.parameter.get_val()))
        self.param_gui_obj.connect("changed", self._on_update, self.parameter)        
        
    def _on_update(self, widget, param):
        new_val = widget.get_text()
        if not param.set_val(new_val):
            #if impossible to set new value restore previous one
            widget.set_text(str(param.get_val()))
            logger.to_log(new_val, widget)
            
        
class GTK_ParamList(GTK_ParamWrapper):
    def _set_gui_obj(self):  
        #value to select by default
        active_val = self.parameter.get_val()
        active_ind = 0
        counter = 0
        
        store = Gtk.ListStore(str)       
        
        for val in self.parameter.allowed_vals():
            store.append([str(val)])
            if val == active_val:
                active_ind = counter
            counter += 1
        
        
        self.param_gui_obj = Gtk.ComboBox.new_with_model_and_entry(store)
        self.param_gui_obj.set_entry_text_column(0)
        self.param_gui_obj.set_active(active_ind)
        

        self.param_gui_obj.connect("changed", self._on_update, self.parameter)
    def _on_update(self, combobox, param):        
        model = combobox.get_model()
        active = combobox.get_active()
        if active is not None and active >= 0:
            new_val = model[active][0]
            param.set_val(new_val)
            logger.to_log(new_val, combobox)
        


class GTK_ParamSlider(GTK_ParamWrapper):
    from math import log10
    NUM_STEPS = 100
    ORIENTATION = Gtk.Orientation.HORIZONTAL
        
    def _set_gui_obj(self):
        
        #(initial value, min value, max value,
        # step increment - press cursor keys to see!,
        # page increment - click around the handle to see!,
        
        init_val = self.parameter.get_val()
        min_val, max_val = self.parameter.get_range()
        step = float(max_val - min_val) / GTK_ParamSlider.NUM_STEPS    
        
        adj = Gtk.Adjustment(init_val, min_val, max_val, step, step, 0)
        
        self.param_gui_obj =  Gtk.Scale(orientation=GTK_ParamSlider.ORIENTATION, 
                                        adjustment = adj)
        self.param_gui_obj.connect("value-changed", self._on_update, self.parameter)
        self.param_gui_obj.set_digits(self._num_digits(step))
    def _on_update(self, widget, param):
        new_val = widget.get_value()
        param.set_val(new_val)
        logger.to_log(new_val, widget)
        #print dir(self)
        #print dir(super(GTK_ParamSlider, self))
        #print dir(param)
        #new_val = self.adj.get_value()
        #print new_val
    def _num_digits(self, step):
        #return the number of decimal places to display based on step
        remainder = abs(step - round(step))
        remainder_log = - GTK_ParamSlider.log10(remainder)
        return max(1, int(remainder_log))
        

TYPE_MATCHES = {ptypes.Parameter:GTK_ParamTextBox,
                ptypes.BoolParameter:GTK_ParamCheckBtn,
                ptypes.ListParameter:GTK_ParamList,
                ptypes.RangeParameter:GTK_ParamSlider,
                ptypes.RangeParameterFit:GTK_ParamSlider}