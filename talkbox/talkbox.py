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

        # Configuration Box for TBC and SoundSets TODO move this to separate file
        confbox = Gtk.Box(spacing=6)
        # TODO make TBCPreviewer.setTBC() instead of this
        listbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.liststore = Gtk.ListStore(str)
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

        listbox.add(treeview)

        addrm_button_box = Gtk.Box(spacing=6)

        add_button = Gtk.Button.new_from_stock(Gtk.STOCK_ADD)
        # TODO add_button.connect("clicked", self.on_add_button_clicked)
        addrm_button_box.pack_start(add_button, True, True, 0)
        
        rm_button = Gtk.Button.new_from_stock(Gtk.STOCK_REMOVE)
        # TODO rm_button.connect("clicked", self.on_rm_button_clicked)
        addrm_button_box.pack_start(rm_button, True, True, 0)

        listbox.pack_start(addrm_button_box, True, True, 0)
        confbox.pack_start(listbox, True, True, 0)


        previewbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        # TODO make SoundSetPreviewer.setSoundSet() instead of this. Inherist from ListBox
        for i in range(12):
            vbox = Gtk.Box(spacing=6)
            pin_num_label = Gtk.Label(xalign=0)
            pin_num_label.set_markup("<span size=\"x-large\">{0}</span>".format(i))
            vbox.pack_start(pin_num_label, True, True, 0)
            previewbox.pack_start(vbox, True, True, 0)

        confbox.pack_start(previewbox, True, True, 0)

        rootbox.add(confbox)

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

    def on_menu_file_new(self, widget):
        print("A File|New menu item was selected.")

    def on_menu_file_open(self, widget):
        print("file open")

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
            print("You selected" + model[treeiter][0])

window = TalkBoxWindow()        
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
