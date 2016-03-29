#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 18:00:23 2016

@author: pavel
"""

class Logger(object):
    logger = None
    @staticmethod
    def get_logger():
        if Logger.logger is None:
            Logger.logger = Logger()
        return Logger.logger    
    def to_log(self, *args):
        log = ' '.join([str(arg) for arg in args])
        print(log)
        
        