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

import settings

class SerialThread(threading.Thread):
    #data from serial port
        def __init__(self, serialObj,
                     onAnswer, onError,
                     onStart=None, onStop = None):
            self.enabled = False

            self.serial = serialObj
            self.onAnswer = onAnswer
            self.onError = onError
            self.onStart = onStart
            self.onStop = onStop
            super(SerialThread, self).__init__()
        def run(self):
            #open port
            #self.serial.open()
            #self.serial.reset_input_buffer()
            char_buffer = []

            while self.enabled:
                for i in range(self.serial.inWaiting()):

                    try:
                        b = self.serial.read(1) #read 1 byte

                    except Exception as e:
                        self.serial.close()
                        self.onError(str(e))
                        return


                    if b != '\n':
                        char_buffer.append(b)
                    else:
                        self.onAnswer(''.join(char_buffer))
                        char_buffer = []
                time.sleep(settings.SLEEP_INTERVAL)

            # debug
                #self.onEvent(b)
            #close port
            self.serial.close()


class DummySerialThread(threading.Thread):
    #random walk

    def __init__(self, onAnswer, onError,
                     onStart=None, onStop = None):
        self.enabled = False

        self.onAnswer = onAnswer
        self.onError = onError
        self.onStart = onStart
        self.onStop = onStop

        self.val = int((settings.DATA_MIN_VALUE + settings.DATA_MAX_VALUE)/2)

        super(DummySerialThread, self).__init__()
    def run(self):
        while self.enabled:
            if (random() < settings.DUMMY_DATA_ERROR_PROB):
                self.onAnswer(settings.DATA_ERR_VALUE)
            else:
                self.val = self.in_limits(self.val +
                randint(- settings.DUMMY_DATA_STEP, settings.DUMMY_DATA_STEP))

                #call function
                self.onAnswer(str(self.val))
            time.sleep(settings.SLEEP_INTERVAL)

    def in_limits(self, value) :
        return max(settings.DATA_MIN_VALUE, min(settings.DATA_MAX_VALUE, value))

class SerialPort:

    def __init__(self):
        self.active = False
        self.port_listener = None

        self.port_addr = None
        self.baudrate = None
        self.all_ports = [port[0] for port in serial.tools.list_ports.comports()
                                                if port is not None]
        self.all_ports.reverse()     #seems to be in reversed order

    # get all available port names
    def enumerate_port_names(self):
        for port in self.all_ports:
            yield port

    #return total number of ports
    def num_ports(self):
        return len(self.all_ports)
    def set_port(self, port):
        self.port_addr = port
        print("port: "+port)

    def set_rate(self, baudrate_str):
        try:
            self.baudrate = int(baudrate_str)
            print("baudrate: "+ baudrate_str)
        except ValueError:
            print ("Not valid baudrate: " + str(baudrate_str) )

    def activate(self, onAnswer, onError, onStart=None, onStop=None, ):
        # do not open port twice
        if self.active:
            return

        self.active = True

        try :
            if settings.DUMMY_DATA: #virtual data
                self.port_listener = DummySerialThread(onAnswer, onError,
                                                       onStart, onStop)
            else:
                if self.port_addr not in self.all_ports or self.baudrate is None:
                    raise ValueError("Invalid port or baudrate")


                serialObj = serial.Serial(self.port_addr, self.baudrate)
                self.port_listener = SerialThread(serialObj, onAnswer, onError,
                                                  onStart, onStop)
        except Exception as e:
            self.deactivate()
            onError(str(e))
            return

        self.port_listener.enabled = True
        self.port_listener.start()
    def deactivate(self):
        if self.active:
            self.active = False
            if self.port_listener is not None:
                self.port_listener.enabled = False
                self.port_listener = None

    def get_prefered_port_ind(self):
        ind = 0
        for port in self.all_ports:
            if port == settings.PREFERED_PORT_NAME:
                return ind
            ind += 1
        return None
    def get_default_port_ind(self):
        if (settings.DEFAULT_PORT_IND < 0): # negative DEFAULT_PORT_IND
            #subtraction
            return max(0, self.num_ports()+ settings.DEFAULT_PORT_IND)
        else:
            return min(settings.DEFAULT_PORT_IND, self.num_ports() -1)
