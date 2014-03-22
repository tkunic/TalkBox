#!/usr/bin/env python

import sys
import traceback
import os.path

import pygtk
pygtk.require('2.0')
import gtk

import json

# set up default directory
home = os.path.expanduser("~")
desktop = os.path.join(home, "Desktop")
if os.path.exists(desktop) and os.path.isdir(desktop):
    default_dir = desktop
else:
    default_dir = home

# add mime types for the files we support
supported_mime_types = ["audio/x-wav"]

def errorDialog(msg):
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
    dialog.run()
    dialog.destroy()


class PinBox(gtk.HBox):
    def __init__(self, pin_number):
        super(PinBox, self).__init__()
        
        self.pin_number = pin_number

        self.pin_num_label = gtk.Label()
        self.pin_num_label.set_markup("<span font_desc=\"30.0\">%s</span>" % (pin_number))
        self.pack_start(self.pin_num_label, False, False, 0)
        self.pin_num_label.show()

        self.button = gtk.Button("Select Soundfile")
        self.button.connect("clicked", self.select_filename, None)
        self.pack_end(self.button, False, False, 0)
        self.button.show()

        self.soundfile_label = gtk.Label("soundfile_label")
        self.pack_end(self.soundfile_label, False, False, 10)
        self.soundfile_label.show()


    def select_filename(self, widget, data=None):
        chooser = gtk.FileChooserDialog("Pick soundfile for pin %d" % (self.pin_number),
                                             None,
                                             gtk.FILE_CHOOSER_ACTION_OPEN,
                                             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        filefilter = gtk.FileFilter()
        for mime_type in supported_mime_types:
            filefilter.add_mime_type(mime_type)
        chooser.set_filter(filefilter)

        chooser.set_current_folder(home)
        
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.filename = chooser.get_filename()
            self.soundfile_label.set_text(self.filename)
            
        chooser.destroy()
                    

class PinsConf:
    def __init__(self):
        self.conf = {}
        for i in xrange(12):
            self.conf[i] = {"filename": "", "image": "", "description": ""}

    def validate(self):
        # TODO for each key, verify validity
        print self.conf

    def load(self, config_path):
        try:
            with open(config_path) as fp:
                self.conf = json.load(fp)
        except:
            msg = "Failed to load %s" % config_path
            self.__error(msg)

        self.validate()

    def save(self, config_path):
        try:
            with open(config_path, 'w') as fp:
                json.dump(self.conf, fp, sort_keys=True, indent=4)
        except:
            msg = "Failed to write %s" % config_path
            self.__error(msg)
    
    def set_pin(self, pin_num, conf_map):
        self.conf[pin_num] = conf_map

    def get_pin(self, pin_num):
        return self.conf[pin_num]

    def __error(self, msg):
        sys.stderr.write(msg)
        sys.stderr.write(traceback.format_exc())
        errorDialog(msg)



class ConfWindow:
    def save_json(self, widget, data=None):
        # TODO make save instead of open, no copy-paste
        chooser = gtk.FileChooserDialog("Save Configuration...",
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        chooser.set_current_folder(home)
        chooser.set_current_name("pinsconf.json")
        
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            self.pinsconf.save(filename)
            
        chooser.destroy()
    
    def load_json(self, widget, data=None):
        chooser = gtk.FileChooserDialog("Load Configuration...",
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
 
        chooser.set_current_folder(home)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()

        chooser.destroy()

        new_conf = PinsConf()
        new_conf.load(filename)
        self.conf = new_conf
    
    def run_listener(self, widget, data=None):
        pass
    
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
        
    def __init__(self):
        self.pinsconf = PinsConf()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.connect("delete_event", self.delete_event, None)
        self.window.set_border_width(10)

        self.pins_box = gtk.VBox(False, 0)
        
        self.pins = []
        for i in xrange(12):
            pin_box = PinBox(i)
            self.pins.append(pin_box)

            self.pins_box.pack_start(pin_box, False, False, 0)
            pin_box.show()

            separator = gtk.HSeparator()
            separator.set_size_request(400, 15)
            self.pins_box.pack_start(separator, False, False, 0)
            separator.show()

        start_button = gtk.Button("START")
        cmap = start_button.get_colormap()
        color = cmap.alloc_color("green")
        style = start_button.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = color
        style.bg[gtk.STATE_ACTIVE] = color
        style.bg[gtk.STATE_SELECTED] = color
        style.bg[gtk.STATE_PRELIGHT] = color
        start_button.set_style(style)
        start_button.connect("clicked", self.run_listener, None)
        
        save_button = gtk.Button("Save")
        save_button.connect("clicked", self.save_json, None)
        
        load_button = gtk.Button("Load")
        load_button.connect("clicked", self.load_json, None)

        button_box = gtk.HBox(False, 0)
        button_box.set_size_request(-1, 40)
        button_box.pack_start(load_button, True, True, 10)
        button_box.pack_start(save_button, True, True, 10)
        button_box.pack_start(start_button, True, True, 10)
        load_button.show()
        save_button.show()
        start_button.show()
        
        self.pins_box.pack_start(button_box, False, False, 0)
        button_box.show()

        self.window.add(self.pins_box)
        self.pins_box.show()
        self.window.show()


if __name__ == "__main__":
    ConfWindow()
    gtk.main()

