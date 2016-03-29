#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:05:05 2016

@author: pavel
"""
#import matplotlib
#matplotlib.use('GTKAgg')


from gi.repository import Gtk#, Gdk#,  Gio, GLib

from gtk_wrapper import GTK_Wrapper

import data_filter
from logger import Logger
from data_processor import DataProcessor, FileProcessor
from data_plotter import Plotter
from graph import GTK_Graph
from data_provider import RandomWalkDataProvider, SerialPortDataProvider

import global_settings as settings

logger = Logger.get_logger()


class GUI:
    GLADE_FILE = "GUI.glade"
    EXPORT_RESPONSE_OK = 1

    def __init__(self): 
        
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GUI.GLADE_FILE)
        
        # order is important!
        self._gui_elements_init_()
        self._graph_init_()
        self._data_procesor_init_()
        self._provider_init_()


        self.is_active = False

        self.builder.connect_signals(self)

        self.builder.get_object("main_window").show_all()

        self.stop()
        #
    def _gui_elements_init_(self):
        #attach elements to paned
        graph_window = self.builder.get_object("graph_window")
        control_panel = self.builder.get_object("control_panel")
        working_area_paned = self.builder.get_object("working_area_paned")
        
        #graph to the left: resizable
        #control panel to the right
        working_area_paned.pack1(graph_window, resize=True, shrink=True)
        working_area_paned.pack2(control_panel, resize=False, shrink=True)
         
        
        #start button
        self.gui_start_btn = self.builder.get_object("start_btn")
        self.gui_start_label = self.builder.get_object("start_lbl")
        self.gui_stop_label = self.builder.get_object("stop_lbl")

        #provider settings
        self.gui_provider_settings_area = self.builder.get_object("provider_settings_alignment")
        # 
        self.gui_provider_settings_box = self.builder.get_object("provider_settings_box")
        
        
        #filter settings
        self.gui_filter_settings_box = self.builder.get_object("filter_settings_box")
        
        #export dialog
        self.gui_export_btn = self.builder.get_object("export_btn")
        self.gui_export_dialog = None

        #error message dialog
        self.gui_error_message_dialog = None

    def _data_procesor_init_(self):
        filters = [data_filter.Invertor(), 
                   data_filter.SelfAdjustableNotchFilter()]
        self.data_processor = DataProcessor(self.plotter.plot_valid, 
                                            self.plotter.plot_error, filters)
        
        for filter_ in filters:
            name = filter_.get_name()
            name_repr = GTK_Wrapper.get_wrapper(name).get_gui_object()
            
            self.gui_filter_settings_box.pack_start(name_repr, True, True, 0)
            
            filter_settings_mgr = filter_.settings_manager()
            
            self._add_all_params(filter_settings_mgr, self.gui_filter_settings_box)
                
  
    def _provider_init_(self):
        
        self.data_provider = RandomWalkDataProvider(onData = self.data_processor.new_data, 
                                                    onError = self.error_stop)
        #self.data_provider = SerialPortDataProvider(self.data_processor.new_data, self.error_stop)
        
        data_provider_settings_mgr = self.data_provider.settings_manager()
        
        self._add_all_params(data_provider_settings_mgr, self.gui_provider_settings_box)
         

    def _graph_init_(self):
        # Create graph
        #self.graph = MatplotlibGraph(onClose=self.stop)        
        self.graph = GTK_Graph(self.builder.get_object("graph_area"),
                               settings.GRAPH_COLORS, 
                               settings.DATA_MIN_VALUE, settings.DATA_MAX_VALUE)
        self.plotter = Plotter(self.graph)                           

    def _add_all_params(self, obj_settings_mgr, gui_setting_box):
        for param in obj_settings_mgr.all_params():
            wrapper = GTK_Wrapper.get_wrapper(param)
            gui_obj = wrapper.get_gui_object()
            
            gui_setting_box.pack_start(gui_obj, True, True, 0)
        

    def close(self):
        self.stop()
        self.graph.close()        
        
    def start(self):
        if self.is_active:
            self.stop()

        logger.to_log("start")
        self.is_active = True

        # handling with gui first!!!

        #disable port settings
        self.gui_provider_settings_area.set_sensitive(False)
        #rename start button
        self.gui_start_btn.set_label(self.gui_stop_label.get_text())
        #disable export button
        self.gui_export_btn.set_sensitive(False)


        self.data_processor.enable()
        # start listening
        self.data_provider.activate()

    def error_stop(self, text):
        self.error_message(text)
        self.stop()

    def error_message(self, text):
        logger.to_log(text)
        
        if self.gui_error_message_dialog is None:
            self.gui_error_message_dialog = self.builder.get_object("error_message_dialog")

        self.gui_error_message_dialog.set_property("secondary-text", text)
        self.gui_error_message_dialog.run()
        self.gui_error_message_dialog.hide()

    def stop(self):
        logger.to_log("stop")
        self.data_provider.deactivate()
        self.data_processor.disable()

        self.is_active = False

        #enable settings
        self.gui_provider_settings_area.set_sensitive(True)
        #rename start button
        self.gui_start_btn.set_label(self.gui_start_label.get_text())
        #enable export button
        self.gui_export_btn.set_sensitive(True)


    def on_main_window_delete_event(self, *args):
        self.close()
        Gtk.main_quit()
    
    def on_start_clicked(self, *args):
        if self.is_active:
            self.stop()
        else:
            self.start()
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



if __name__ == "__main__":
    gui = GUI()
    Gtk.main()
