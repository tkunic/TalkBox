from gi.repository import Gtk, Gdk
from models import TalkBoxConf, SoundSet, PinConf
from player import TBPlayer

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='FileNew' />
      <menuitem action='FileOpen' />
      <menuitem action='FileSave' />
      <separator />
      <menuitem action='FileQuit' />
    </menu>
    <menu action='EditMenu'>
      <menuitem action='EditCopy' />
      <menuitem action='EditPaste' />
      <menuitem action='EditSomething' />
    </menu>
    <menu action='RunMenu'>
      <menuitem action='PlaySoundSet' />
      <menuitem action='SetTBCOnBoot' />
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='FileNew' />
    <toolitem action='FileOpen' />
    <toolitem action='FileSave' />
    <separator />
    <toolitem action='FileQuit' />
    <separator />
    <toolitem action='PlaySoundSet' />
    <toolitem action='SetTBCOnBoot' />
  </toolbar>
</ui>
"""

class TalkBoxWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="TalkBox")

        self.set_border_width(10)
        self.set_default_size(600, 400)

        action_group = Gtk.ActionGroup("my_actions")

        self.add_file_menu_actions(action_group)
        self.add_edit_menu_actions(action_group)
        self.add_run_menu_actions(action_group)

        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/MenuBar")

        rootbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        rootbox.pack_start(menubar, False, False, 0)

        toolbar = uimanager.get_widget("/ToolBar")
        rootbox.pack_start(toolbar, False, False, 0)

        self.tbcview = TBCView()
        rootbox.pack_start(self.tbcview, True, True, 0)

        self.add(rootbox)

    def add_file_menu_actions(self, action_group):
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)

        action_filenew = Gtk.Action("FileNew", None, None, Gtk.STOCK_NEW)
        action_filenew.connect("activate", self.on_menu_file_new)
        action_group.add_action(action_filenew)

        action_fileopen = Gtk.Action("FileOpen", None, None, Gtk.STOCK_OPEN)
        action_fileopen.connect("activate", self.on_menu_file_open)
        action_group.add_action(action_fileopen)

        action_filesave = Gtk.Action("FileSave", None, None, Gtk.STOCK_SAVE)
        action_filesave.connect("activate", self.on_menu_file_save)
        action_group.add_action(action_filesave)

        action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
        action_filequit.connect("activate", self.on_menu_file_quit)
        action_group.add_action(action_filequit)

    def add_edit_menu_actions(self, action_group):
        action_group.add_actions([
            ("EditMenu", None, "Edit"),
            ("EditCopy", Gtk.STOCK_COPY, None, None, None,
             self.on_menu_others),
            ("EditPaste", Gtk.STOCK_PASTE, None, None, None,
             self.on_menu_others),
            ("EditSomething", None, "Something", "<control><alt>S", None,
             self.on_menu_others)
        ])

    def add_run_menu_actions(self, action_group):
        action_filemenu = Gtk.Action("RunMenu", "Run", None, None)
        action_group.add_action(action_filemenu)

        action_playsoundset = Gtk.Action("PlaySoundSet", None, None, Gtk.STOCK_MEDIA_PLAY)
        action_playsoundset.connect("activate", self.on_menu_run_playsoundset)
        action_group.add_action(action_playsoundset)

        action_settbconboot = Gtk.Action("SetTBCOnBoot", None, None, Gtk.STOCK_APPLY)
        action_settbconboot.connect("activate", self.on_menu_run_tbconboot)
        action_group.add_action(action_settbconboot)


    def create_ui_manager(self):
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(UI_INFO)

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager
    
    
    def on_menu_file_new(self, widget):
        print("A File|New menu item was selected.")
        global tbc
        tbc = TalkBoxConf()
        self.tbcview.refresh()

    def on_menu_file_open(self, widget):
        print("file open")
        filename = select_file_dialog("tbc")
        print("Selected TBC file: " + filename)
        tbc.set_from_file(filename)
        self.tbcview.refresh()
        

    def on_menu_file_save(self, widget):
        print("file save")
        filename = select_file_dialog("tbc", action="save")
        print("Selected TBC file: " + filename)
        tbc.write_to_file(filename)

    def on_menu_file_quit(self, widget):
        Gtk.main_quit()

    def on_menu_run_playsoundset(self, widget):
        if player.is_playing():
            player.stop_SoundSet()
        else:
            current_soundset = tbc.get_soundset(current_soundset_name)
            player.play_SoundSet(current_soundset)
            
        if player.is_playing():
            # TODO? gray out sound selection until the pause button is unpaused?
            widget.set_stock_id(Gtk.STOCK_MEDIA_PAUSE)
        else:
            widget.set_stock_id(Gtk.STOCK_MEDIA_PLAY)

    def on_menu_run_tbconboot(self, widget):
        print("run settbconboot")
        player.set_TalkBoxConf(tbc)
        alert("TalkBox boot configuration set!")

    def on_menu_others(self, widget):
        print("Menu item " + widget.get_name() + " was selected")

    def on_menu_choices_changed(self, widget, current):
        print(current.get_name() + " was selected.")

    def on_menu_choices_toggled(self, widget):
        if widget.get_active():
            print(widget.get_name() + " activated")
        else:
            print(widget.get_name() + " deactivated")


        
class TBCView(Gtk.Box):
    def __init__(self):
        super(TBCView, self).__init__(spacing=6)
        
        self.soundsetview = SoundSetView()
        self.pack_start(self.soundsetview, False, True, 0)

        self.previewbox = PreviewBox()
        
        self.pack_start(self.previewbox, True, True, 0)
        
    def refresh(self):
        self.soundsetview.set_tbc(tbc)
        self.previewbox.set_soundset(tbc.get_soundset(current_soundset_name))

class SoundSetView(Gtk.Box):
    def __init__(self):
        super(SoundSetView, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        self.liststore = Gtk.ListStore(str)
            
        self.set_tbc(tbc)

        self.treeview = Gtk.TreeView(model=self.liststore)

        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("editable", True)
        # FIXME: the " " * 30 is a dirty hack to set minimum width
        column_text = Gtk.TreeViewColumn("SoundSet Name" + " " * 30, renderer_text, text=0)
        self.treeview.append_column(column_text)

        renderer_text.connect("edited", self.on_text_edited)
        select = self.treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        self.pack_start(self.treeview, True, True, 0)

        addrm_button_box = Gtk.Box(spacing=6)

        add_button = Gtk.Button.new_from_stock(Gtk.STOCK_ADD)
        add_button.connect("clicked", self.on_add_button_clicked)
        addrm_button_box.pack_start(add_button, True, True, 0)
        
        rm_button = Gtk.Button.new_from_stock(Gtk.STOCK_REMOVE)
        rm_button.connect("clicked", self.on_rm_button_clicked)
        addrm_button_box.pack_start(rm_button, True, True, 0)

        self.pack_start(addrm_button_box, False, True, 0)
    
    def set_tbc(self, tbc):
        self.liststore.clear() # FIXME! this clear is a problem, it de-selects what you edited immediately after the fact
        for soundset in tbc.list_soundsets():
            self.liststore.append([soundset.get_name()])
        
    def on_text_edited(self, widget, path, text):
        # FIXME terrible design. shouldn't update and keep track of so many things from here 
        old_name = self.liststore[path][0]
        soundset = tbc.get_soundset(old_name).set_name(text)
        self.liststore[path][0] = text
        global current_soundset_name
        current_soundset_name = text
        
        print("text edited: path = " + path + ", text = " + text)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            print("You selected: " + model[treeiter][0])
            global current_soundset_name
            current_soundset_name = model[treeiter][0]
            window.tbcview.previewbox.set_soundset(tbc.get_soundset(current_soundset_name))
            
    def on_add_button_clicked(self, widget):
        print("add button clicked")
        ss_name = self.get_untitled_name()
        ss = SoundSet(ss_name)
        tbc.add_soundset(ss)
        self.liststore.append([ss_name])
        
    def on_rm_button_clicked(self, widget):
        print("rm button clicked")
        model, treeiter = self.treeview.get_selection().get_selected()
        if treeiter != None:
            soundset_name = model[treeiter][0]
            self.liststore.remove(treeiter)
            tbc.remove_soundset(soundset_name)
        
    def get_untitled_name(self):
        counter = 1
        while True:
            name = "Untitled {0}".format(counter)
            if tbc.get_soundset(name) != None:
                counter = counter + 1
            else:
                return name

class PreviewBox(Gtk.Box):
    def __init__(self):
        super(PreviewBox, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.pinviews = []
        for i in range(12):
            self.pinviews.append(PinView(i))
            self.pack_start(self.pinviews[i], True, True, 0)
            
    def set_soundset(self, soundset):
        if soundset is None:
            self.hide()
            return
        for i, pinview in enumerate(self.pinviews):
            soundstring = soundset.get_pin(i).get_soundstring()
            print soundstring
            pinview.set_entry_text(soundstring)
        self.show()
        

class PinView(Gtk.Box):
    def __init__(self, pin_num):
        super(PinView, self).__init__(spacing=6)
        self.pin_num = pin_num
        
        pin_num_label = Gtk.Label(xalign=0)
        pin_num_label.set_markup("<span font=\"32\">{0}</span>".format("  " + str(pin_num) if (pin_num < 10) else pin_num))
        self.pack_start(pin_num_label, False, False, 0)
        
        filebox = Gtk.Box(spacing=6)
        self.fileentry = Gtk.Entry()
        self.fileentry.connect("changed", self.on_edit)
        filebox.pack_start(self.fileentry, True, True, 0)
        filebutton = Gtk.Button(label="Open Sound File", image=Gtk.Image(stock=Gtk.STOCK_OPEN))
        filebutton.connect("clicked", self.on_browse_soundfiles)
        filebox.pack_start(filebutton, False, False, 0)
        self.pack_start(filebox, True, True, 0)
        
        play_button = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
        play_button.connect("clicked", self.on_play_button_clicked)
        self.pack_start(play_button, False, True, 0)
        
    def get_entry_text(self):
        return self.fileentry.get_text()
    
    def set_entry_text(self, text):
        self.fileentry.set_text(text)
    
    def on_edit(self, widget):
        text = self.fileentry.get_text()
        print "edit at pin {0}, new text: {1}".format(self.pin_num, text)
        tbc.get_soundset(current_soundset_name).get_pin(self.pin_num).set_soundstring(text)
        
    def on_browse_soundfiles(self, widget):
        wavpath = select_file_dialog("wav")
        self.fileentry.set_text(wavpath)
        print("Soundfile for pin {0} selected: {1}".format(self.pin_num, wavpath))
        
    def on_play_button_clicked(self, widget):
        current_soundset = tbc.get_soundset(current_soundset_name)
        if current_soundset is not None:
            soundstring = current_soundset.get_pin(self.pin_num).get_soundstring()
            print "playing soundstring: " + soundstring
            player.play_soundstring(soundstring)
        print("Play button for pin_number {0} clicked".format(self.pin_num))
        

def select_file_dialog(extension, action="open"):
    if action == "save":
        fc_action = Gtk.FileChooserAction.SAVE
        fc_button = Gtk.STOCK_SAVE
    else:
        fc_action = Gtk.FileChooserAction.OPEN
        fc_button = Gtk.STOCK_OPEN
    
    dialog = Gtk.FileChooserDialog("Please choose a file", window,
        fc_action,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         fc_button, Gtk.ResponseType.OK))
    
    if action == "save" and extension == "tbc":
        dialog.set_current_name("Untitled.tbc")

    # Add some filters for supported content types
    if (extension == "wav"):
        filter_wav = Gtk.FileFilter()
        filter_wav.set_name("WAV files")
        filter_wav.add_mime_type("audio/x-wav")
        dialog.add_filter(filter_wav)
    elif (extension == "tbc"):
        filter_tbc = Gtk.FileFilter()
        filter_tbc.set_name("TalkBox files")
        filter_tbc.add_mime_type("application/zip")
        dialog.add_filter(filter_tbc)

    filter_any = Gtk.FileFilter()
    filter_any.set_name("Any files")
    filter_any.add_pattern("*")
    dialog.add_filter(filter_any)

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        print("File selected: " + filename)
    elif response == Gtk.ResponseType.CANCEL:
        print("Cancel clicked")

    dialog.destroy()
    return filename

def alert(msg):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, msg)
    dialog.run()
    dialog.destroy()


tbc = TalkBoxConf()
#tbc.set_from_file('/home/ehbemtu/devt/raspitap/tests/resources/bigtest.tbc') #tk_ loads a soundset by default for test purposes only
player = TBPlayer()
current_soundset_name = '' # FIXME should abolish this in favour of querying the selection

if __name__ == '__main__':
    #import signal
    #signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    window = TalkBoxWindow()        
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    #window.fullscreen()
    Gtk.main()
