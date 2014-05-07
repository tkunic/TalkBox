from gi.repository import Gtk, Gdk

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

        confbox = self.create_config_box()
        rootbox.pack_start(confbox, True, True, 0)

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
        action_settbconboot.connect("activate", self.on_menu_run_settbconboot)
        action_group.add_action(action_settbconboot)


    def create_ui_manager(self):
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(UI_INFO)

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager
    
    def create_config_box(self):
                # Configuration Box for TBC and SoundSets TODO move this to separate file
        confbox = Gtk.Box(spacing=6)
        
        listbox = self.create_listbox()
        confbox.pack_start(listbox, True, True, 0)

        previewbox = self.create_previewbox()
        confbox.pack_start(previewbox, True, True, 0)

        return confbox

    def create_listbox(self):
        # TODO make TBCPreviewer.setTBC() instead of this
        listbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.liststore = Gtk.ListStore(str)
        # FIXME here only for mockup purposes
        tk_soundsets = ["Essentials 1", "Essentials 2", "Essentials 3", "Days in Week", "Months", "Feeling", "Attendance M", "Attendance F", "Temperature"]
        for elem in tk_soundsets:
            self.liststore.append([elem])

        treeview = Gtk.TreeView(model=self.liststore)

        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("editable", True)
        column_text = Gtk.TreeViewColumn("SoundSet Name", renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_text.connect("edited", self.on_text_edited)
        select = treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        listbox.pack_start(treeview, True, True, 0)

        addrm_button_box = Gtk.Box(spacing=6)

        add_button = Gtk.Button.new_from_stock(Gtk.STOCK_ADD)
        add_button.connect("clicked", self.on_add_button_clicked)
        addrm_button_box.pack_start(add_button, True, True, 0)
        
        rm_button = Gtk.Button.new_from_stock(Gtk.STOCK_REMOVE)
        rm_button.connect("clicked", self.on_rm_button_clicked)
        addrm_button_box.pack_start(rm_button, True, True, 0)

        listbox.pack_start(addrm_button_box, False, True, 0)
        return listbox
    
    def create_previewbox(self):
        previewbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        # TODO make SoundSetPreviewer.setSoundSet() instead of this. Inherist from ListBox
        for i in range(12):
            previewbox.pack_start(self.create_pinbox(i), True, True, 0)
        return previewbox

    def create_pinbox(self, pin_num):
        pinbox = Gtk.Box(spacing=6)
        pin_num_label = Gtk.Label(xalign=0)
        pin_num_label.set_markup("<span font=\"32\">{0}</span>".format("  " + str(pin_num) if (pin_num < 10) else pin_num))
        pinbox.pack_start(pin_num_label, False, False, 0)
        
        switchbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        pinbox.pack_start(switchbox, True, True, 0)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(500)
        
        synth_entry = Gtk.Entry()
        stack.add_titled(synth_entry, "synth_entry", "Synth Entry")
        
        filebox = Gtk.Box(spacing=6)
        filebutton = Gtk.Button("Browse...")
        filebutton.connect("clicked", self.on_browse_soundfiles, pin_num)
        filebox.pack_start(filebutton, True, True, 0)
        fileentry = Gtk.Entry()
        filebox.pack_start(fileentry, True, True, 0)
        stack.add_titled(filebox, "filebox", "Sound File")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        switchbox.pack_start(stack_switcher, True, True, 0)
        switchbox.pack_start(stack, True, True, 0)
        
        play_button = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
        play_button.connect("clicked", self.on_play_button_clicked, pin_num)
        pinbox.pack_start(play_button, True, True, 0)
        
        return pinbox
    
    def on_menu_file_new(self, widget):
        print("A File|New menu item was selected.")

    def on_menu_file_open(self, widget):
        print("file open")
        print "Selected TBC file: " + self.select_file_dialog("tbc")

    def on_menu_file_save(self, widget):
        print("file save")

    def on_menu_file_quit(self, widget):
        Gtk.main_quit()

    def on_menu_run_playsoundset(self, widget):
        print("run playsoundset")

    def on_menu_run_settbconboot(self, widget):
        print("run settbconboot")

    def on_menu_others(self, widget):
        print("Menu item " + widget.get_name() + " was selected")

    def on_menu_choices_changed(self, widget, current):
        print(current.get_name() + " was selected.")

    def on_menu_choices_toggled(self, widget):
        if widget.get_active():
            print(widget.get_name() + " activated")
        else:
            print(widget.get_name() + " deactivated")


    def on_text_edited(self, widget, path, text):
        self.liststore[path][0] = text
        print("text edited: path = " + path + ", text = " + text)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            print("You selected: " + model[treeiter][0])
            
    def on_add_button_clicked(self, widget):
        print "add button clicked"
        
    def on_rm_button_clicked(self, widget):
        print "rm button clicked"
        
    def on_browse_soundfiles(self, widget, pin_num):
        print "Soundfile for pin {0} selected: {1}".format(pin_num, self.select_file_dialog("wav"))
        
    def on_play_button_clicked(self, widget, pin_num):
        print "Play button for pin_number {0} clicked".format(pin_num)
    
    def select_file_dialog(self, extension):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

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
            print("Open clicked")
            filename = dialog.get_filename()
            print("File selected: " + filename)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
        return filename
        
if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    window = TalkBoxWindow()        
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    #window.fullscreen()
    Gtk.main()
