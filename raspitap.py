#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class ConfWindow:
    def write_json(self, widget, data=None):
        pass

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
        
    def __make_pin(self, pin_number):
        pin_box = gtk.HBox(False, 0)

        lejbl = gtk.Label("%d" % (pin_number))
        buton = gtk.Button("This is a button")

        pin_box.pack_start(lejbl, False, False, 0)
        lejbl.show()

        pin_box.pack_end(buton, False, False, 0)
        buton.show()

        self.pins_box.pack_start(pin_box, False, False, 0)
        pin_box.show()

        separator = gtk.HSeparator()
        separator.set_size_request(400, 5)
        self.pins_box.pack_start(separator, False, False, 0)
        separator.show()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.connect("delete_event", self.delete_event)
        self.window.set_border_width(10)

        self.pins_box = gtk.VBox(False, 0)
        
        for i in xrange(12):
            self.__make_pin(i)

        start_button = gtk.Button("START")
        cmap = start_button.get_colormap()
        color = cmap.alloc_color("green")
        style = start_button.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = color
        style.bg[gtk.STATE_ACTIVE] = color
        style.bg[gtk.STATE_SELECTED] = color
        style.bg[gtk.STATE_PRELIGHT] = color
        start_button.set_style(style)

        self.pins_box.pack_start(start_button, False, False, 0)
        start_button.connect("clicked", self.write_json, None)
        start_button.show()

        self.window.add(self.pins_box)
        self.pins_box.show()
        self.window.show()

if __name__ == "__main__":
    ConfWindow()
    gtk.main()

