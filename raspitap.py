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
SUPPORTED_MIME_TYPES = ["audio/x-wav"]
NUMBER_OF_PINS = 12

def errorDialog(msg):
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
    dialog.run()
    dialog.destroy()


class PinBox(gtk.HBox):
    def __init__(self, pin_number):
        super(PinBox, self).__init__()
        
        # Initialize fields
        self.pin_number = pin_number
        self.soundfile = None
        self.imagefile = None
        self.description = None
        
        # create and display pin number label
        self.pin_num_label = gtk.Label()
        self.pin_num_label.set_markup("<span font_desc=\"30.0\">%s</span>" % (pin_number))
        self.pack_start(self.pin_num_label, False, False, 0)
        self.pin_num_label.show()

        # create and display "Select Soundfile" button
        self.button = gtk.Button("Select Soundfile")
        self.button.connect("clicked", self.__select_soundfile, None)
        self.pack_end(self.button, False, False, 0)
        self.button.show()

        # create and display soundfile label
        self.soundfile_label = gtk.Label("No Soundfile Assigned")
        self.pack_end(self.soundfile_label, False, False, 10)
        self.soundfile_label.show()


    def get_number(self):
        return self.pin_number
    
    def set_soundfile(self, soundfile):
        self.soundfile = soundfile
        if self.soundfile is not None:
            self.soundfile_label.set_text(self.soundfile)
        else:
            self.soundfile_label.set_text("No Soundfile Assigned")
    
    def get_soundfile(self):
        return self.soundfile
    
    def set_imagefile(self, imagefile):
        self.imagefile = imagefile
    
    def get_imagefile(self):
        return self.imagefile
    
    def set_description(self, description):
        self.description = description
    
    def get_description(self):
        return self.description
    
    def __select_soundfile(self, widget, data=None):
        chooser = gtk.FileChooserDialog("Pick soundfile for pin %d" % (self.pin_number),
                                             None,
                                             gtk.FILE_CHOOSER_ACTION_OPEN,
                                             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        filefilter = gtk.FileFilter()
        for mime_type in SUPPORTED_MIME_TYPES:
            filefilter.add_mime_type(mime_type)
        chooser.set_filter(filefilter)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            self.set_soundfile(filename)
            
        chooser.destroy()
                    

# FIXME: PinsConf + pins VBox => PinsConf(gtk.VBox)
class PinsConf:
    def __init__(self):
        self.confmap = {}
        for i in xrange(NUMBER_OF_PINS):
            self.confmap[i] = {"soundfile": "", "imagefile": "", "description": ""}

    def validate(self):
        # TODO for each key, verify validity
        # if wrong raise Exception
        print self.confmap

    def load(self, config_path, pin_boxes):
        try:
            with open(config_path) as fp:
                self.confmap = json.load(fp)
                self.validate()
                
            for pin_box in pin_boxes:
                pin_num = str(pin_box.get_number())
                pin_box.set_soundfile(self.confmap[pin_num]["soundfile"])
                pin_box.set_imagefile(self.confmap[pin_num]["imagefile"])
                pin_box.set_description(self.confmap[pin_num]["description"])
            
        except:
            msg = "Failed to load %s" % config_path
            self.__error(msg)

    def save(self, config_path):
        try:
            with open(config_path, 'w') as fp:
                json.dump(self.confmap, fp, sort_keys=True, indent=4)
        except:
            msg = "Failed to write %s" % config_path
            self.__error(msg)
    
    def set_pin_boxes(self, pin_boxes):
        for pin_box in pin_boxes:
            pin_num = pin_box.get_number()
            self.confmap[pin_num]["soundfile"] = pin_box.get_soundfile()
            self.confmap[pin_num]["imagefile"] = pin_box.get_imagefile()
            self.confmap[pin_num]["description"] = pin_box.get_description()

    def get_pin_map(self, pin_num):
        return self.confmap[pin_num]

    def __error(self, msg):
        sys.stderr.write(msg)
        sys.stderr.write(traceback.format_exc())
        errorDialog(msg)



class ConfWindow:
    def __init__(self):
        self.pinsconf = PinsConf()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event, None)
        self.window.set_border_width(10)

        self.pins_box = gtk.VBox(False, 0)
        
        self.pins = []
        for i in xrange(NUMBER_OF_PINS):
            pin_box = PinBox(i)
            self.pins.append(pin_box)

            self.pins_box.pack_start(pin_box, False, False, 0)
            pin_box.show()

            separator = gtk.HSeparator()
            separator.set_size_request(400, 15)
            self.pins_box.pack_start(separator, False, False, 0)
            separator.show()
        
        load_button = gtk.Button("Load")
        load_button.connect("clicked", self.load_json, None)

        save_button = gtk.Button("Save")
        save_button.connect("clicked", self.save_json, None)
        
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
    
    def save_json(self, widget, data=None):
        # TODO make save instead of open, no copy-paste
        chooser = gtk.FileChooserDialog("Save current configuration...",
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        chooser.set_current_folder(home)
        chooser.set_current_name("pinsconf.json")
        
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            self.pinsconf.set_pin_boxes(self.pins)
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
        new_conf.load(filename, self.pins)
        self.conf = new_conf
    
    def run_listener(self, widget, data=None):
        self.listener = TapListener(self.conf)
        self.listener.run()
        # TODO change the START button to a red STOP button
    
    def stop_listener(self, widget, data=None):
        self.listener.stop()
        # TODO change the red STOP button to a START button
        
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
        

class TapListener:
    def __init__(self, config):
        self.filename = config
    
    def run(self):
        # TODO put hrairhlessil/TalkBox code here
        pass
    
    def stop(self):
        pass

if __name__ == "__main__":
    ConfWindow()
    gtk.main()

