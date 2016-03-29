#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 10:27:34 2016

@author: pavel
"""
class CircularBuffer:
        def __init__(self, size):
            self.array = [None]*(size)
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
                    
class Queue:
    def __init__(self):
        self.size = 0
        self.data = []
    def put(self, obj):
        self.size += 1
        self.data.append(obj)
    def get(self):
        if not self.empty():
            self.size -= 1
            return self.data.pop(0)
        return None
    def empty(self):
        return self.size == 0