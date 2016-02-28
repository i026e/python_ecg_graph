#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:05:05 2016

@author: pavel
"""
#import matplotlib
#matplotlib.use('GTKAgg')


from gi.repository import Gtk#, Gdk,  Gio, GLib

from data_processing import DataProcessor, FileProcessor
from graphs import GTK_Graph
from serial_port import SerialPort

import settings




class GUI:
    GLADE_FILE = "ECG.glade"
    EXPORT_RESPONSE_OK = 1

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GUI.GLADE_FILE)

        self._gui_elements_init_()

        self._ports_init_()
        self._graph_init_()
        self._data_procesor_init_()


        self.is_active = False

        self.builder.connect_signals(self)

        self.builder.get_object("main_window").show()

        self.stop()
        #
    def _gui_elements_init_(self):
        #filter settings
        self.gui_filter_chkbox = self.builder.get_object("filter_button")
        self.gui_freq_txtbox = self.builder.get_object("freq_entry")
        self.gui_filter_rough_adj = self.builder.get_object("filter_adj")
        self.gui_invert_chkbox = self.builder.get_object("invert_button")


        self.gui_filter_chkbox.set_active(settings.USE_FILTER)
        self.gui_invert_chkbox.set_active(settings.INVERT_SIGNAL)
        self.gui_freq_txtbox.set_text(str(settings.FILTER_FREQ))
        self.gui_filter_rough_adj.set_value(settings.FILTER_INV_STRENGTH)

        #start button
        self.gui_start_btn = self.builder.get_object("start_btn")
        self.gui_start_label = self.builder.get_object("start_lbl")
        self.gui_stop_label = self.builder.get_object("stop_lbl")

        #port settings
        self.gui_settings_area = self.builder.get_object("settings_alignment")
        # combobox with serial ports
        self.gui_serial_ports_list = self.builder.get_object("serial_ports")
        #combobox with baudrates
        self.gui_baudrates_list = self.builder.get_object("baudrates")


        #export dialog
        self.gui_export_btn = self.builder.get_object("export_btn")
        self.gui_export_dialog = None

        #error message
        self.gui_error_message_dialog = None

    def _ports_init_(self):
        self.serial_port = SerialPort()


        for port in self.serial_port.enumerate_port_names():
            self.gui_serial_ports_list.append_text(port)

        for baudrate in settings.BAUDRATES:
            self.gui_baudrates_list.append_text(str(baudrate))

        # compute index of port sected by default
        # first try by name , no guarantee
        selected_port = self.serial_port.get_prefered_port_ind()
        if selected_port is None:
            #next by index
            selected_port = self.serial_port.get_default_port_ind()

        self.gui_serial_ports_list.set_active(selected_port)

        self.gui_baudrates_list.set_active(settings.DEFAULT_BAUDRATE_IND)
        self.on_serial_port_changed()
        self.on_baudrate_changed()

    def _graph_init_(self):
        # Create graph
        #self.graph = MatplotlibGraph(onClose=self.stop)
        error_color = GTK_Graph.Color(settings.ERROR_COLOR_RGB)
        valid_color = GTK_Graph.Color(settings.VALID_COLOR_RGB)

        colors = {settings.ERROR_COLOR_NAME:error_color,
                  settings.VALID_COLOR_NAME:valid_color}
        self.graph = GTK_Graph(self.builder.get_object("graph_area"),
                               colors, settings.DATA_MIN_VALUE, settings.DATA_MAX_VALUE)

    def _data_procesor_init_(self):
        self.data_processor = DataProcessor(output_graph = self.graph,
                                            valid_color_name = settings.VALID_COLOR_NAME,
                                            error_color_name = settings.ERROR_COLOR_NAME,
                                            do_filtering = settings.USE_FILTER,
                                            filter_freq = settings.FILTER_FREQ,
                                            filter_roughness = settings.FILTER_INV_STRENGTH,
                                            do_inversion = settings.INVERT_SIGNAL)


    def close(self):
        self.stop()

    def start(self):
        if self.is_active:
            self.stop()

        print("start")
        self.is_active = True

        # handling with gui first!!!

        #disable port settings
        self.gui_settings_area.set_sensitive(False)
        #rename start button
        self.gui_start_btn.set_label(self.gui_stop_label.get_text())
        #disable export button
        self.gui_export_btn.set_sensitive(False)


        self.data_processor.enable_accepting_data()
        # start listening
        self.serial_port.activate(onAnswer=self.data_processor.new_data,
                                  onError = self.error_stop)

    def error_stop(self, text):
        self.error_message(text)
        self.stop()

    def error_message(self, text):
        print text
        if self.gui_error_message_dialog is None:
            self.gui_error_message_dialog = self.builder.get_object("error_message_dialog")

        self.gui_error_message_dialog.set_property("secondary-text", text)
        self.gui_error_message_dialog.run()
        self.gui_error_message_dialog.hide()

    def stop(self):
        print("stop")
        self.serial_port.deactivate()
        self.data_processor.disable_accepting_data()

        self.is_active = False

        #enable settings
        self.gui_settings_area.set_sensitive(True)
        #rename start button
        self.gui_start_btn.set_label(self.gui_start_label.get_text())
        #enable export button
        self.gui_export_btn.set_sensitive(True)


    def on_main_window_delete_event(self, *args):
        self.close()
        Gtk.main_quit()

    def on_serial_port_changed(self, *args):
        self.serial_port.set_port(self.gui_serial_ports_list.get_active_text())
    def on_baudrate_changed(self, *args):
        self.serial_port.set_rate(self.gui_baudrates_list.get_active_text())

    def on_start_clicked(self, *args):
        if self.is_active:
            self.stop()
        else:
            self.start()
    def on_invert_toggled(self, *args):
        #print(dir(self.filter_chkbox))
        self.data_processor.set_inversion(
                                self.gui_invert_chkbox.get_active())

        print("inversion changed to " + str(self.gui_invert_chkbox.get_active()))
    def on_filter_toggled(self, *args):
        #print(dir(self.filter_chkbox))
        self.data_processor.set_filtering(
                self.gui_filter_chkbox.get_active())
        print("filtering changed to " + str(self.gui_filter_chkbox.get_active()))
    def on_freq_changed(self, *args):
        #print dir(self.gui_freq_txtbox)
        str_val = self.gui_freq_txtbox.get_text()
        try:
            val = 0 # treat empty string as implicit 0
            if str_val != "":
                val = int(str_val)
            self.data_processor.set_filter_freq(val)
            print("set frequency to " + str_val)
        except:
            print("unexpected frequency " + str_val)
            #restore prev value
            self.gui_freq_txtbox.set_text(
                            str(self.data_processor.get_filter_freq()))
    def on_export_clicked(self, *args):
        if self.gui_export_dialog is None:
            self.gui_export_dialog = self.builder.get_object("export_filechooser_dialog")

        fproc = FileProcessor()
        self.gui_export_dialog.set_current_name(fproc.get_name())

        response = self.gui_export_dialog.run()

        if response == gui.EXPORT_RESPONSE_OK:
            fproc.set_name(self.gui_export_dialog.get_filename())
            fproc.do_export(self.data_processor, onError=self.error_message)

        self.gui_export_dialog.hide()

    def on_filter_rough_value_changed(self, *args):
        #print(dir(self.gui_filter_rough_adj))
        val = self.gui_filter_rough_adj.get_value()
        self.data_processor.set_filter_roughness(val)
        print("roughness " + str(val))

if __name__ == "__main__":
    gui = GUI()
    Gtk.main()
