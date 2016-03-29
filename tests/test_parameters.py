#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 09:50:30 2016

@author: pavel
"""
import sys
sys.path.insert(0, '../')

import parameter_types

import unittest

class TestParameterManager(unittest.TestCase):
    def test_pm(self):
        pm = parameter_types.ParameterManager()
        param1 = parameter_types.Parameter("1", "abc", str)
        param2 = parameter_types.ListParameter("2", "a", str, ["a", "b", "c"])
        param3 = parameter_types.ListParameter("3", 2, int, [1, 2, 3])
        param4 = parameter_types.RangeParameter("4", 2, int, 0, 10)
        param5 = parameter_types.RangeParameterFit("5", 7.3, float, 0.1, 9.9)
        
        parameters = [param1, param2, param3, param4, param5]
        for param in parameters:
            pm.add_param(param.get_name(), param)
            
        self.assertEqual(pm.num_params(), len(parameters))
        
        for p_name in pm.param_names():
            param = pm.get_param(p_name)
            
            self.assertTrue(param in parameters)
            
        for param in parameters:
            p = pm.get_param(param.get_name())
            self.assertEqual(p, param)
            
        # override first parameter    
        param6 = parameter_types.Parameter(param1.get_name(), "ddd", str)
        pm.add_param(param1.get_name(), param6)
        
        self.assertEqual(pm.num_params(), len(parameters))
        self.assertNotEqual(param1, pm.get_param(param1.get_name()))        
        self.assertEqual(param6, pm.get_param(param6.get_name()))
            

class TestParameter(unittest.TestCase):    
    def test_str(self):
        param = parameter_types.Parameter('string', 'abc', str)
        self.assertEqual(param.get_name(), 'string')
        self.assertEqual(param.get_val(), 'abc') 
        
        res, val = param._convert_val_type(12345)
        self.assertTrue(res)
        self.assertEqual(val, '12345')        
        
        self.assertTrue(param.set_val('DeF'))
        self.assertEqual(param.get_val(), 'DeF')
        
        self.assertTrue(param.set_val(None))
        self.assertEqual(param.get_val(), 'None')
        
        self.assertTrue(param.set_val(123))
        self.assertEqual(param.get_val(), '123')
        
        self.assertTrue(param.set_val(0.2))
        self.assertEqual(param.get_val(), '0.2')

    def test_int(self):
        param = parameter_types.Parameter('sillyName', 1, int)     
        self.assertEqual(param.get_name(), 'sillyName')
        self.assertEqual(param.get_val(), 1)       
        
        
        self.assertTrue(param.set_val(0.2))
        self.assertEqual(param.get_val(), 0)
        
        self.assertTrue(param.set_val(-5))
        self.assertEqual(param.get_val(), -5)
        
        self.assertTrue(param.set_val("123"))
        self.assertEqual(param.get_val(), 123)
        
        self.assertTrue(param.set_val("-321"))
        self.assertEqual(param.get_val(), -321)
        
        self.assertTrue(param.set_val("00012"))
        self.assertEqual(param.get_val(), 12)
        
        self.assertFalse(param.set_val("aaa00"))
        self.assertEqual(param.get_val(), 12)
        
        self.assertFalse(param.set_val("0.2"))
        self.assertEqual(param.get_val(), 12)
    def test_float(self):
        param = parameter_types.Parameter('', 1, float)
        self.assertEqual(param.get_val(), 1.0)
        
        self.assertTrue(param.set_val(0.2))
        self.assertEqual(param.get_val(), 0.2)
        
        self.assertTrue(param.set_val("00012"))
        self.assertEqual(param.get_val(), 12)
        
        self.assertFalse(param.set_val("aaa00"))
        self.assertEqual(param.get_val(), 12)
        
        self.assertTrue(param.set_val("0.8"))
        self.assertEqual(param.get_val(), 0.8)
    def test_wrong_init_type(self):
        #current behavior -- initial value is not checked
        param = parameter_types.Parameter('', "abc", int)
        
        self.assertEqual(param.get_val(), "abc")
        
        self.assertTrue(param.set_val(123))
        self.assertEqual(param.get_val(), 123)
        
        self.assertFalse(param.set_val("abc"))
        self.assertEqual(param.get_val(), 123)
    
        
class TestListParameter(unittest.TestCase):
    def test_str(self):
        vals = ["a", "b", "cde", "d", "1", "2", "4.2"]
        param = parameter_types.ListParameter('name', "a", str, vals)      
        self.assertEqual(param.get_val(), "a")
        
        for val in vals:
            self.assertTrue(val in param.allowed_vals())
        for val in param.allowed_vals():
            self.assertTrue(val in vals)
            
        self.assertTrue(param.set_val("b"))
        self.assertEqual(param.get_val(), "b")    
            
        self.assertTrue(param.set_val(4.2))
        self.assertEqual(param.get_val(), "4.2")
        
        self.assertTrue(param.set_val("cde"))
        self.assertEqual(param.get_val(), "cde")
        
        self.assertFalse(param.set_val("abc"))
        self.assertEqual(param.get_val(), "cde")
        
        self.assertFalse(param.set_val(123))
        self.assertEqual(param.get_val(), "cde")
    def test_int(self):
        vals = [0, 1, 7, 99]
        param = parameter_types.ListParameter('name', 7, int, vals)
        
        self.assertEqual(param.get_val(), 7)
        
        self.assertTrue(param.set_val(0))
        self.assertEqual(param.get_val(), 0)
        
        self.assertTrue(param.set_val("99"))
        self.assertEqual(param.get_val(), 99)
        
        self.assertFalse(param.set_val(123))
        self.assertEqual(param.get_val(), 99)
        
        self.assertFalse(param.set_val("a"))
        self.assertEqual(param.get_val(), 99)
        
class TestRangeParameter(unittest.TestCase):
    def test_chr(self):
        min_val = "c"
        max_val = "k"
        
        param = parameter_types.RangeParameter("", "d", str, min_val, max_val)
        self.assertEqual(param.get_val(), "d")
        
        self.assertTrue(param.set_val("h"))
        self.assertEqual(param.get_val(), "h")
        
        self.assertTrue(param.set_val("c"))
        self.assertEqual(param.get_val(), "c")
        
        self.assertFalse(param.set_val("a"))
        self.assertEqual(param.get_val(), "c")
        
        self.assertFalse(param.set_val("x"))
        self.assertEqual(param.get_val(), "c")
        
        self.assertFalse(param.set_val("D"))
        self.assertEqual(param.get_val(), "c")
        
        self.assertFalse(param.set_val("!"))
        self.assertEqual(param.get_val(), "c")
        
        self.assertTrue(param.set_val("d"))
        self.assertEqual(param.get_val(), "d")
    def test_str(self):
        min_val = "abc"
        max_val = "xyz"
        
        param = parameter_types.RangeParameter("", "eee", str, min_val, max_val)
        self.assertEqual(param.get_val(), "eee")
        
        self.assertTrue(param.set_val("uvwxyz"))
        self.assertEqual(param.get_val(), "uvwxyz")
        
        self.assertTrue(param.set_val("abcdefg"))
        self.assertEqual(param.get_val(), "abcdefg")
        
        self.assertTrue(param.set_val("abc"))
        self.assertEqual(param.get_val(), "abc")
        
        self.assertFalse(param.set_val("a"))
        self.assertEqual(param.get_val(), "abc")
        
        self.assertFalse(param.set_val("aaaaaaa"))
        self.assertEqual(param.get_val(), "abc")
        
        self.assertFalse(param.set_val("DAC"))
        self.assertEqual(param.get_val(), "abc")
        
        self.assertFalse(param.set_val("1"))
        self.assertEqual(param.get_val(), "abc")
        
        self.assertFalse(param.set_val(1))
        self.assertEqual(param.get_val(), "abc")      
       
        self.assertFalse(param.set_val("zzz"))
        self.assertEqual(param.get_val(), "abc")
        
        self.assertTrue(param.set_val("xyz"))
        self.assertEqual(param.get_val(), "xyz")
        
        self.assertTrue(param.set_val("bCD123!!!"))
        self.assertEqual(param.get_val(), "bCD123!!!")
        
def test_int(self):
        min_val = -500
        max_val = 999
        
        param = parameter_types.RangeParameter("", 1, int, min_val, max_val)
        
        self.assertTrue(param.set_val(-499))
        self.assertEqual(param.get_val(), -499)
        
        self.assertTrue(param.set_val(999))
        self.assertEqual(param.get_val(), 999)
        
        self.assertFalse(param.set_val(1000))
        self.assertEqual(param.get_val(), 999)        
      
        self.assertFalse(param.set_val(-501))
        self.assertEqual(param.get_val(), 999)
        
        self.assertTrue(param.set_val(-500))
        self.assertEqual(param.get_val(), -500)
class TestRangeParameterFit(unittest.TestCase):
     def test_str(self):
        min_val = "abc"
        max_val = "xyz" 
        
        param = parameter_types.RangeParameterFit("", "d", str, min_val, max_val)
        
        self.assertTrue(param.set_val("aaa"))
        self.assertEqual(param.get_val(), min_val)
        
        self.assertTrue(param.set_val("bcfex"))
        self.assertEqual(param.get_val(), "bcfex")
        
        self.assertTrue(param.set_val("123"))
        self.assertEqual(param.get_val(), min_val)
        
        self.assertTrue(param.set_val("ZZZ"))
        self.assertEqual(param.get_val(), min_val)
        
        self.assertTrue(param.set_val("zzz"))
        self.assertEqual(param.get_val(), max_val)
        
     def test_int(self):
        min_val = 111
        max_val = 999
        
        param = parameter_types.RangeParameterFit("", 555, int, min_val, max_val)
        
        self.assertTrue(param.set_val(-100))
        self.assertEqual(param.get_val(), min_val)
        
        self.assertTrue(param.set_val(9999))
        self.assertEqual(param.get_val(), max_val)
        
        self.assertTrue(param.set_val(777))
        self.assertEqual(param.get_val(), 777)
        
        self.assertFalse(param.set_val("aaa"))
        self.assertEqual(param.get_val(), 777)
        
if __name__ == "__main__":
    unittest.main()

