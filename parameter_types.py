#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 07:15:48 2016

@author: pavel
"""
class ParameterManager(object):
    def __init__(self, param_changed_cb = None):
        """ param_changed_cb : function to be called 
                if value of some parameter was changed"""
        self.parameters = {}
        self.param_changed_cb = param_changed_cb
        
    def add_param(self, p_name, new_parameter):        
        self.parameters[p_name] = new_parameter   
        new_parameter.set_callback(self.param_changed_cb)
        
    def param_names(self):
        return self.parameters.keys()
    def all_params(self):
        return self.parameters.values()
    def get_param(self, p_name):
        return self.parameters.get(p_name, None)
    def num_params(self):
        return len(self.parameters)

        

class Parameter(object):
    def __init__(self, name, val, val_type):
        """name : name of parameter,
            val : initial value,
            val_type : type of value parameter can take (str, int, float, etc.)
        """
        self.name = name
        self.val = val
        self.val_type = val_type
        
        self.on_change_cb = None # callback function
    def _convert_val_type(self, some_val):
        # try to convert type of some_val
        try:
            some_val = self.val_type(some_val)
            return True, some_val #successful conversion
        except (TypeError, ValueError):
            return False, None    
    def get_name(self):
        return self.name
    def get_type(self):
        return self.val_type
    def get_val(self):
        return self.val    
    def set_val(self, new_val):
            res, new_val = self._convert_val_type(new_val)
            if res:
                self.val = new_val
                self._callback()
                return True #value was updated
            else:
                return False #value was not updated 
    def set_callback(self, on_change_cb):
        self.on_change_cb = on_change_cb
    def _callback(self):
        if self.on_change_cb is not None:
            self.on_change_cb(self)
        
class BoolParameter(Parameter):
    """True or False"""
    def __init__(self, name, val):
        super(BoolParameter, self).__init__(name, val, bool)
        
class ListParameter(Parameter):
    """Value should be in the list of allowed values"""
    def __init__(self, name, val, val_type, possible_vals):
        super(ListParameter, self).__init__(name, val, val_type)
        self.possible_vals = possible_vals
    def allowed_vals(self):
        return self.possible_vals
    def set_val(self, new_val):
        res, new_val = self._convert_val_type(new_val)
        if res and new_val in self.possible_vals:
            # update only if new_val is allowed
            self.val = new_val
            self._callback()
            return True #success
        return False
        
class RangeParameter(Parameter):
    """ Do nothing if value out of range"""
    def __init__(self, name, val, val_type, min_val, max_val):
        super(RangeParameter, self).__init__(name, val, val_type)
                   
        self.min_val = min_val
        self.max_val = max_val
    def _in_range(self, val):
        return val >= self.min_val and val <= self.max_val
    def get_range(self):
        return (self.min_val, self.max_val)
    def set_val(self, new_val):
        res, new_val = self._convert_val_type(new_val)
        if res and self._in_range(new_val):
            self.val = new_val
            self._callback()
            return True
        return False
                
class RangeParameterFit(RangeParameter):
    """ Set to closest boundary if value out of range"""
    def __init__(self, name, val, val_type, min_val, max_val):
        if min_val > max_val:
            min_val, max_val = max_val, min_val #swap       
        
        super(RangeParameterFit, self).__init__(name, val, val_type, min_val, max_val)
    def _fit(self, val):
        return min(self.max_val, max(self.min_val, val))
    def set_val(self, new_val):
        res, new_val = self._convert_val_type(new_val)
        if res:
            self.val = self._fit(new_val)
            self._callback()
            return True
        return False