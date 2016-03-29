#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 12:02:33 2016

@author: pavel
"""
import sys
sys.path.insert(0, '../')

import global_settings
import data_provider as dp

import unittest
from time import sleep

class SimpleDataProviderTest(unittest.TestCase):
    def setUp(self):
        self.val = None
        f = self.set_val #response of all function should be saved in self.val
        self.provider = dp.DataProvider(onData=f, onError=f, onStart=f, onStop=f)
        self.provider2 = dp.DataProvider(onData=f, onError=f, onStart=None, onStop=None)
    def test_send_data(self):
        self.provider.send_data(1)
        self.assertEqual(self.val, 1)
        
        self.provider.send_data("a")
        self.assertEqual(self.val, "a")
    def test_send_error(self):
        self.provider.send_error("error")
        self.assertEqual(self.val, "error")
        
    def test_send_started_stopped(self):
        self.provider.send_started("started_1")
        self.assertEqual(self.val, "started_1")
        
        self.provider2.send_started("started_2") #no onStart callback
        self.assertEqual(self.val, "started_1")
        
        self.provider.send_started("stopped_1")
        self.assertEqual(self.val, "stopped_1")
        
        self.provider2.send_started("stopped_2")
        self.assertEqual(self.val, "stopped_1")
        
    def set_val(self, val):
        self.val = val
        
class AsyncDataProviderTest(unittest.TestCase):
    def add_val(self, val):
        self.vals.append(val)
    def on_start(self):
        self.provider_status = "running"
    def on_stop(self):
        self.provider_status = "stopped"

    def setUp(self):
        self.vals = []
        self.provider_status = None
        f = self.add_val
        self.provider = dp.DataProvider(onData=f, onError=f, 
                                        onStart=self.on_start, 
                                        onStop=self.on_stop)
    
    def test_async(self):
        self.assertFalse(self.provider.is_active())
        self.provider.activate()
        
        self.assertTrue(self.provider.is_active())
        self.assertEqual(self.provider_status, "running")
        
        # activate active provider        
        self.provider.activate()
        self.assertTrue(self.provider.is_active())
        
        sleep(global_settings.SLEEP_INTERVAL*50)
        
        
        self.assertTrue(self.provider.is_active())
        self.provider.deactivate()
        
        self.assertFalse(self.provider.is_active())
        self.assertEqual(self.provider_status, "stopped")
        
        length = len(self.vals)
        self.assertGreater(length, 0)
        
        sleep(global_settings.SLEEP_INTERVAL*3)
        
        #no more data
        self.assertEqual(length, len(self.vals))
        
class RandomWalkDataProviderTest(unittest.TestCase):
    def add_val(self, val):
        self.vals.append(val)
    def setUp(self):
        self.vals = []
        f = self.add_val
        
        self.provider = dp.RandomWalkDataProvider(onData = f, onError = f)
        self.provider_set_mgr = self.provider.settings_manager()        
        
    def test_async(self):
        self.provider.activate()
        
        sleep(global_settings.SLEEP_INTERVAL*20)
        self.provider.deactivate()
        
        self.assertGreater(len(self.vals), 0)
        
        for val in self.vals:
            if val != global_settings.DATA_ERR_VALUE:
                self.assertEqual(self.provider.in_limits(val), val)
                self.assertGreaterEqual(val, self.provider_set_mgr.get_min())
                self.assertLessEqual(val, self.provider_set_mgr.get_max())
                
        
class SerialPortDataProviderTest(unittest.TestCase):
    def setUp(self):
        self.val = None
        f = self.set_val
        self.provider = dp.SerialPortDataProvider(f, f)

    def set_val(self, val):
        self.val = val
    def test_init(self):        
        self.provider.activate()
        #serial port should return error or some data
        sleep(global_settings.SLEEP_INTERVAL*20)
        self.provider.deactivate()
        
        self.assertIsNotNone(self.val)

class SettingsManagersTest(unittest.TestCase):
    def test_RandomWalkSettingsManager(self):
        sm = dp.RandomWalkSettingsManager()
        
        self.assertEqual(sm.get_max(), global_settings.DATA_MAX_VALUE)
        self.assertEqual(sm.get_min(), global_settings.DATA_MIN_VALUE)
        
        self.assertEqual(sm.get_err_prob(), global_settings.RWALK_DATA_ERROR_PROB)
        self.assertEqual(sm.get_step(), global_settings.RWALK_DATA_STEP)
        
    def test_SerialPortSettingsManager(self):
        sm = dp.SerialPortSettingsManager()
        
        port_params = sm.get_param(dp.SerialPortSettingsManager.PORT)
        brates_params = sm.get_param(dp.SerialPortSettingsManager.BAUDRATE)
        
        ports = port_params.allowed_vals()
        baudrates = brates_params.allowed_vals()
        
        self.assertGreater(len(ports), 0)
        self.assertGreater(len(baudrates), 0)
        
        self.assertIn(sm.get_port(), ports)
        self.assertIn(sm.get_baudrate(), baudrates)
        
        
    
    
if __name__ == "__main__":
    unittest.main()
