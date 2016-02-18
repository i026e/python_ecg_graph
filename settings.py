#!/usr/bin/env python
# -*- coding: utf-8 -*-

SLEEP_INTERVAL = 0.01

"""data section"""
# describing data
DATA_ERR_VALUE = '!' #error symbol
DATA_MIN_VALUE = 0 #min possible serial data input
DATA_MAX_VALUE = 1023 #max possible serial data input

#use random walking data
DUMMY_DATA = True
# probability of error between 0.0 and 1.0
DUMMY_DATA_ERROR_PROB = 0.008 
# random walk max step
# actual step will be somewhere in [-max_step..+max_step]
DUMMY_DATA_STEP = 10


"""graph section"""
#color for drawing error line
ERROR_COLOR_NAME = "red"
ERROR_COLOR_RGB = (0.9, 0.1, 0.1) # rgb
#color for valid data line
VALID_COLOR_NAME = "blue"
VALID_COLOR_RGB = (0.1, 0.1, 0.9) # rgb

NUM_ENTRIES_BEFORE_PLOT = 5 # redraw plot only after receiving so much samples

#does not matter
#PYPLOT_GRAPH = False


"""port settings section"""
BAUDRATES = [600, 1200, 1800, 2400, 4800, 9600, 
             19200, 38400, 57600, 115200, 230400, 460800, 500000]
    
DEFAULT_BAUDRATE_IND = 5 #9600
PREFERED_PORT_NAME = "/dev/ttyS20" #will be selected if exists
DEFAULT_PORT_IND = -1 # else select last one



"""filter section"""
# supress this frequency
FILTER_FREQ = 50 #Hz
USE_FILTER = True
#filter strength in [0, 1) 
#0 = max strength
FILTER_INV_STRENGTH = 0.7 #
# how many samples need to receive to estimate sampling rate
SAMPLS_TO_MEASURE_SAMPL_RATE = 100



"""data processing and saving section"""
#last NUM_ENTRIES_TO_EXPORT records will be exported
NUM_ENTRIES_TO_EXPORT = 1000000 
FILENAME_EXTENSION = ".csv"
FILENAME_DATE_FORMAT = "%Y-%m-%d_%H-%M" # data is used as filename
CSV_SEPARATOR = ";"
CSV_LINE_TERMINATOR = "\r\n"

