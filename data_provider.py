#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 07:53:06 2016

@author: pavel
"""
import threading, time

import serial
import serial.tools.list_ports

from random import randint, random

import global_settings as settings
import parameter_types as prm

class DataProvider(object):
    class AsyncThread(threading.Thread):
        def __init__(self, outer_instance, sleep_interval):
            self.outer_instance = outer_instance
            self.sleep_interval = sleep_interval
            self.enabled_flag = False

            super(DataProvider.AsyncThread, self).__init__()
        def run(self):
            self.enabled_flag = True
            while self.enabled_flag:
                self.outer_instance._acquire_data()
                time.sleep(self.sleep_interval)
        def stop_thread(self):
            self.enabled_flag = False

    def __init__(self, onData, onError, onStart, onStop):
        self.onData = onData
        self.onError = onError
        self.onStart = onStart
        self.onStop = onStop

        self._sleepInterval = settings.SLEEP_INTERVAL
        self._asyncThread = None

        self.is_active_flag = False
        
        self.settings_mgr = prm.ParameterManager()
        self._set_settings()

    #private methods
    def send_data(self, val):
        self.onData(val)
    def send_error(self, val):
        self.onError(val)
    def send_started(self, *val):
        if self.onStart is not None:
            self.onStart(*val)
    def send_stopped(self, *val):
        if self.onStop is not None:
            self.onStop(*val)

    #to override
    def _set_settings(self):
        #assign settings manager
        pass
    def _prepare(self):
        #called during activation
        #should return True if launch is allowed
        self.send_started()
        return True
    def _acquire_data(self):
        # continuously called by async thread
        # should return some value, that will be passed onData callback
        self.send_data(0)
    def _on_stop(self):
        # called after async thread is stopped
        self.send_stopped()
    #public
    def settings_manager(self):
        return self.settings_mgr
    def activate(self):
        # start data collecting
        # returns True if successfully started
        if not self.is_active_flag:
            self.is_active_flag = True
            if self._prepare():
                self._asyncThread = self.AsyncThread(self, self._sleepInterval)
                self._asyncThread.start()
                return True
            else:
                self.is_active_flag = False
                self._on_stop()
        return False
    def deactivate(self):
        if self.is_active_flag:
            self.is_active_flag = False
            if self._asyncThread is not None:
                self._asyncThread.stop_thread()
                self._asyncThread = None
            self._on_stop()
    def is_active(self):
        return self.is_active_flag


class RandomWalkDataProvider(DataProvider):
    #random walk
    def __init__(self, onData, onError,
                     onStart=None, onStop = None):
        super(RandomWalkDataProvider, self).__init__(onData, onError, onStart, onStop)

    def _set_settings(self):
        #assign settings manager
        self.settings_mgr = RandomWalkSettingsManager()
        self.val = 0
    def _acquire_data(self):
        if (random() < self.settings_mgr.get_err_prob()):
            self.send_data(settings.DATA_ERR_VALUE)
        else:
            step = self.settings_mgr.get_step()
            self.val = self.in_limits(self.val + randint(-step, step))

            self.send_data(self.val)

    def in_limits(self, value) :
        return max(self.settings_mgr.get_min(), min(self.settings_mgr.get_max(), value))

class SerialPortDataProvider(DataProvider):
    def __init__(self, onData, onError,
                 onStart=None, onStop = None):
        super(SerialPortDataProvider, self).__init__(onData, onError, onStart, onStop)
    def _set_settings(self):
        #assign settings manager
        self.settings_mgr = SerialPortSettingsManager()
        self.serialObj = None
        self.char_buffer = []
    def _prepare(self):
        super(SerialPortDataProvider, self)._prepare()
        port = self.settings_mgr.get_port()
        baudrate = self.settings_mgr.get_baudrate()
        try :
            self.serialObj = serial.Serial(port, baudrate)
            return True
        except Exception as e:
            self.send_error(str(e))
        return False
    def _on_stop(self):
        super(SerialPortDataProvider, self)._on_stop()
        if self.serialObj is not None:
            self.serialObj.close()
    def _acquire_data(self):
        for i in range(self.serialObj.inWaiting()):

            try:
                b = self.serialObj.read(1) #read 1 byte

            except Exception as e:
                self.send_error(str(e))
                self.deactivate()


            if b != '\n':
                self.char_buffer.append(b)
            else:
                self.send_data(''.join(self.char_buffer))
                self.char_buffer = []
                

class RandomWalkSettingsManager(prm.ParameterManager):
    MAX_VAL = "max value"
    MIN_VAL = "min value"
    STEP = "step"
    ERR_PROB = "error prob"
    def __init__(self):
        super(RandomWalkSettingsManager, self).__init__()
        
        self.step = prm.Parameter(self.STEP, settings.RWALK_DATA_STEP, int)
        self.max_val = prm.Parameter(self.MAX_VAL, settings.DATA_MAX_VALUE, int)
        self.min_val = prm.Parameter(self.MIN_VAL, settings.DATA_MIN_VALUE, int)
        self.err_prob = prm.RangeParameterFit(self.ERR_PROB, 
                                              settings.RWALK_DATA_ERROR_PROB, float, 0.0, 1.0)
        
        self.add_param(self.MAX_VAL, self.max_val)
        self.add_param(self.MIN_VAL, self.min_val)
        self.add_param(self.STEP, self.step)
        self.add_param(self.ERR_PROB, self.err_prob)
    def get_max(self):
        return self.max_val.get_val()
    def get_min(self):
        return self.min_val.get_val()
    def get_err_prob(self):
        return self.err_prob.get_val()
    def get_step(self):
        return self.step.get_val()
        

class SerialPortSettingsManager(prm.ParameterManager):
    PORT = "port"
    BAUDRATE = "baudrate"    
    
    def __init__(self):
        super(SerialPortSettingsManager, self).__init__()
        
        
        possible_ports = [port[0] for port in serial.tools.list_ports.comports()
                                                if port is not None]
        possible_ports.reverse()                            
        port = ""
        if settings.PREFERED_PORT_NAME in possible_ports:
            port = settings.PREFERED_PORT_NAME
        else:
            port_ind = 0
            num_ports = len(possible_ports)
            if (settings.DEFAULT_PORT_IND < 0): # negative DEFAULT_PORT_IND
                #subtraction
                port_ind = max(0, num_ports + settings.DEFAULT_PORT_IND)
            else:
                port_ind = min(settings.DEFAULT_PORT_IND, num_ports -1)

            port = possible_ports[port_ind]
        self.port = prm.ListParameter(self.PORT, port, str, possible_ports)
        
        self.baudrate = prm.ListParameter(self.BAUDRATE, 
                                          settings.DEFAULT_BAUDRATE, int, 
                                          settings.BAUDRATES)
        self.add_param(self.PORT, self.port)
        self.add_param(self.BAUDRATE, self.baudrate)
                                          
    def get_port(self):
        return self.port.get_val()
    def get_baudrate(self):
        return self.baudrate.get_val()

