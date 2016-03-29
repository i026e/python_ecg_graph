#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 11:46:50 2016

@author: pavel
"""

import time
from datetime import datetime

import numbers

import global_settings as settings
from data_storage import CircularBuffer


class DataProcessor:
    def __init__(self, output_correct_funct, output_err_funct, filter_cascade=[]):
        """

        """
        self.output_correct_funct = output_correct_funct
        self.output_err_funct = output_err_funct

        self.filter_cascade = filter_cascade

        self.export_data = CircularBuffer(settings.NUM_ENTRIES_TO_EXPORT)

        self.busy_flag = False

    def _process_entry(self, entry):
        if entry == settings.DATA_ERR_VALUE:
            return entry

        if isinstance(entry, numbers.Number):
            return entry
        return self._process_as_string(entry)

    def _process_as_string(self, entry):
        entry = str(entry).strip()
        if len(entry) > 0:
            try :
                entry = float(entry)
            except :
                print("unexpected value " + entry)
                entry = settings.DATA_ERR_VALUE
        return entry

    def new_data(self, entry):
        """ data : string or int or float from input """

        if entry is not None and not self.busy_flag:
        # process only if real data
        # skip data if busy
            self.busy_flag = True

            entry = self._process_entry(entry)

            if entry == settings.DATA_ERR_VALUE:
                self.output_err_funct(entry)

            else:
                #apply filters
                for _filter in  self.filter_cascade:
                    entry = _filter.filtered(entry)
                self.output_correct_funct(entry)

            #keep entry for export
            self.export_data.write(entry)

            self.busy_flag = False


    def get_export_data(self):
        while self.busy_flag:
            time.sleep(settings.SLEEP_INTERVAL)
        self.busy_flag = True

        # create new circular buffer
        tmp_data = self.data_to_export
        self.data_to_export = CircularBuffer(settings.NUM_ENTRIES_TO_EXPORT)
        self.busy_flag = False

        return tmp_data
    def disable(self):
        self.busy_flag = True
    def enable(self):
        self.busy_flag = False

class FileProcessor:
    def __init__(self):
        date = datetime.now()
        self.filename = (date.strftime(settings.FILENAME_DATE_FORMAT) +
                                        settings.FILENAME_EXTENSION)
    def get_name(self):
        return self.filename
    def set_name(self, new_name):
        self.filename = new_name
        print("new filename: " + new_name)
    def do_export(self, data_processor, onError):
        try:
            f_obj = open(self.filename, 'w')
            circ_buffer = data_processor.get_export_data()

            index = 0
            for entry in circ_buffer.all_entries():
                line = str(index) + settings.CSV_SEPARATOR + str(entry)
                f_obj.write(line + settings.CSV_LINE_TERMINATOR)
                index += 1

            f_obj.close()

        except Exception as e:
            f_obj.close()
            onError(str(e))


