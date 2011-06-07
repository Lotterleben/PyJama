#! /usr/bin/env python
# -*- coding: utf-8 

import ConfigParser
import os
import pygtk
pygtk.require('2.0')
import gtk
import string
import eyeD3

class PyJama:
    # warning: I never said it was going to be pretty.
    # this little script provides a klickibunti Environment that lets you create
    # crontabs für viirus' DIY alarm clock: http://f.pherth.net/vip/
    
    # this will only work if you've got your VIP's sshd up&running and 
    # didn't set a root password. 
    # (yess, will fix the latter.)
    # you also need to install the python-eyed3 module to make this work

    def __init__(self):
        self.init_stuff()
        self.create_window()
        self.load_config()
        self.window.show_all()

    def create_window(self):
        #create window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("PyJama alarm clock manager")
        
        # create actual containers
        self.ipbox= gtk.HBox()
        self.daybox= gtk.VBox()
        labelbox = gtk.VBox()
        buttonbox = gtk.HBox()
        musicbox = gtk.VBox()
        self.timebox = gtk.HBox()
        self.column_1 = gtk.VBox()
        self.column_2 = gtk.VBox()
        self.allbox = gtk.HBox()

        # create IP entry field
        l_ip = gtk.Label("your VIP's IP:")
        self.e_ip = gtk.Entry()	

        #create text fields
        self.days = []
        for i in range (0,7):
            self.days.append(gtk.Entry())    

        #labels... yupp, fugly.
        l_mon = gtk.Label("monday")
        l_tue = gtk.Label("tuesday")
        l_wed = gtk.Label("wednesday")
        l_thu = gtk.Label("thursday")
        l_fri = gtk.Label("friday")
        l_sat = gtk.Label("saturday")
        l_sun = gtk.Label("sunday")
        #just so the days will align correctly. yes, eww. :D
        #l_space = gtk.Label(None)
        
        #creating the buttons (duh)
        #button_show = gtk.Button("show crontab")
        button_scp = gtk.Button("Set Alarm")
        b_music_chooser = gtk.Button("Select Music")
        b_music_uploader = gtk.Button("Upload Music")
        #button_show.connect("clicked", self.launcher,"show")
        button_scp.connect("clicked",self.launcher, "copy")
        b_music_chooser.connect("clicked", self.launcher, "choose_music")
        b_music_uploader.connect("clicked", self.launcher, "upload_music")

        # lists n stuff
        self.trackstore = gtk.ListStore(str, str)
        self.trackview = gtk.TreeView(self.trackstore)
        
        self.titlecolumn = gtk.TreeViewColumn('Title')
        self.artistcolumn = gtk.TreeViewColumn('Artist')
        self.trackview.append_column(self.titlecolumn)
        self.trackview.append_column(self.artistcolumn)
        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        # add the cell to the tvcolumn and allow it to expand
        self.titlecolumn.pack_start(self.cell, True)
        self.artistcolumn.pack_start(self.cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        # copypasta- no idea if i need this. waaaay too derp for that right now.
        self.titlecolumn.add_attribute(self.cell, 'text', 0)
        self.artistcolumn.add_attribute(self.cell, 'text', 1)
        
        # Allow drag and drop reordering of rows
        #The developer can listen to these changes by connecting to the model's row_inserted and row_deleted signals. 
        self.trackview.set_reorderable(True)
        
        self.trackstore.connect("row-changed", self.rchanged)
        
        #killswitch
        self.window.connect("destroy", self.destroy)
        self.window.connect("delete_event", self.delete_event)
        
        # add & show geraffel
        self.ipbox.add(l_ip)
        self.ipbox.add(self.e_ip)
        for i in range(0,7):
            self.daybox.add(self.days[i])
        labelbox.add(l_mon)
        labelbox.add(l_tue)
        labelbox.add(l_wed)
        labelbox.add(l_thu)
        labelbox.add(l_fri)
        labelbox.add(l_sat)
        labelbox.add(l_sun)
        #labelbox.add(l_space)
        #buttonbox.add(button_show)
        buttonbox.add(button_scp)
        musicbox.add(b_music_chooser)
        musicbox.add(self.trackview)
        musicbox.add(b_music_uploader)
        self.timebox.add(labelbox)
        self.timebox.add(self.daybox)
        self.column_1.add(self.ipbox)
        self.column_1.add(self.timebox)
        self.column_2.add(musicbox)
        self.column_1.add(buttonbox)
        self.allbox.add(self.column_1)
        self.allbox.add(self.column_2)
        self.window.add(self.allbox)
        
    
    def load_config(self):
        #loading the configs to the window's panels
        self.config=ConfigParser.ConfigParser()
        print self.pyjamapath
        # control structure- double tap.
        if os.path.exists(self.pyjamapath):
            # only read from the file if it exists :D
            if os.path.exists(self.pyjamapath +'PyJama.cfg'):
                pyjamafile= open(self.pyjamapath +'PyJama.cfg')
                self.config.readfp(pyjamafile)
                self.config.read(pyjamafile)
                #copy stored configs to textfields                                                         
                for i in range (0,7):
                    self.days[i].set_text(self.config.get('days',str(i)))
                self.e_ip.set_text(self.config.get('IP','ip'))
                pyjamafile.close()
        else: 
            os.makedirs(self.pyjamapath)

    def init_stuff(self):
        """ inits some Variables that I didn't want to throw all over the place."""
        self.pyjamapath = os.path.expanduser('~')+'/.config/PyJama/'
        
        # storing the selected music ([str],absolute paths)
        self.tracklist = []
    
    #for testing puropses    
    def rchanged(self, widget, new_row, track):
        print "row changed", "new row: " , new_row, "\n track: ", type(track), self.trackstore.get_value(track, 0)
        # note: new_row is the row which has been changed (that is, the 
        # *target* of the drag&drop action). 
        # track is a treeIter pointing to the track that has been dragged&dropped.

    def launcher(self, widget, button_action):
        # will keep the button_action thingamabob in case there are other buttons in the future
        self.store_settings()

        #prepare for the arrival of event messages
        ev_msg=gtk.TextBuffer(table=None)
        ev_msg.set_text("we've got news for you: \n ===================================================== \n")
        ev_msg_edited = True
        if button_action is "copy":
            # copy crontab and collect generated event messages
            ev_msg.insert_at_cursor(self.copy_ctab(widget))
        elif button_action is "choose_music":
            # let the User choose his music selection and display a list of the tracks 
            self.choose_music(widget)
            ev_msg_edited=False
            # tracks will be displayed in the TreeView Widget:
            for i in range(0,len(self.tracklist)):
                tag = eyeD3.Tag()
                tag.link(self.tracklist[i])
                artist= tag.getArtist()
                title= tag.getTitle()
                if not title :
                    # this is a fallback for titles that aren't tagged properly.
                    # (if somebody didn't tag their artists right- bummer...)
                    # (works because  Python treats empty objects as False values)
                    title=self.tracklist[i]
                    pathlst=title.split("/")
                    title=pathlst[-1]
                tmp=self.trackstore.append()
                self.trackstore.set_value(tmp, 0, title)
                self.trackstore.set_value(tmp, 1, artist)
        elif button_action is "upload_music":
            # copy music to VIP and collect error msgs 
            print "uploading: ", self.tracklist
            ev_msg.insert_at_cursor(self.copy_music( widget))
        
        # pop up collected error messages:
        if ev_msg_edited:
            self.event_popup(ev_msg)

    def store_settings(self):
        """ stores the user's settings to /home/<user>/.config/PyJama/Pyjama.cfg """
        # write times to config file so they will never be forgotten.
        # TODO: unhighlight lines when displayed in freshly started program
        # section which contains weekdays. these can be addressed with their index nr.
        # example: 
        # 1: '13:37, 17, 20:00'
        if not self.config.has_section('days'):
            self.config.add_section('days')
        for i in range(0,7):
            day_str =self.days[i].get_text()
            # TODO: don't store the non-digit chars
            self.config.set('days',str(i),day_str)

        # store ip in config
        if not self.config.has_section('IP'):
            self.config.add_section('IP')
        self.config.set('IP','ip',self.e_ip.get_text())
        
        # doppelt gemoppelt. muesste man mal richtig machen.
        pyjamafile = open(self.pyjamapath+'PyJama.cfg', 'w')
        with pyjamafile as configfile:
           self.config.write(configfile)
        pyjamafile.close()
        
        
    def generate_ctab(self):
        """ generates the crontab (duh!), writes it into the config dir (lazy way
        of implementing the copy operation, will eventually change that) """

        # first of all, we parse the entries so they will fit into a crontab
        times, nondigit_error = self.parse_times()

        # creating local the crontab so it can be scp'd. this is only temporary and
        # yes, this is idiotic. But I really need something to work right now.
        # TODO: fix this mess.

        pyjamatab= open(self.pyjamapath+'crontab', 'w')      
            
        for i in range (0,7):
            weekday=times[i]
            for j in weekday:
                line = "& "+j+" * * "+ str(i+1) +" sh /flash2/alarm-clock \n"
                pyjamatab.write(line)
        pyjamatab.close()
        
        return nondigit_error
        # pipe crontab to buffer (for popup) (deprecated, but just in case..) 
        """if button_action is "show":
            buff = gtk.TextBuffer(table=None)       
            for i in range (0,7):
                weekday=times[i]
                for j in weekday:
                    line = "& "+j+" * * "+ str(i+1) +" sh /flash2/alarm-clock \n"
                    buff.insert(buff.get_end_iter(), line)
            return buff"""

    def copy_ctab(self, widget):
        """ copies the generated ctab (stored @ pyjamapath)
        to the VIP behind the specified IP"""
        nondigit_err = self.generate_ctab()
        
        sys =os.system('scp "%s" "%s:%s"' % (self.pyjamapath+'crontab', 'root@'+self.e_ip.get_text(),'/flash2/crontab') )
        
        # check if the scp was successful and display an error message if not
        # TODO: watch stdin/stderr for password requests etc (for example if somebody set a root pswd)
        err_msg=""
        if nondigit_err:
            err_msg+="\n -* It looks like you had some non-digit characters in your alarm times. You may want to double-check them. \n We still updated all the correct times, though :) \n"
        if sys is not 0:
            #some error occured
            err_msg+="\n -* o noes! It looks like setting the alarm has failed, probably because your Box didn't respond. \n Please check your settings and try again."
        else:
            err_msg+="\n -* wheee! Setting the alarm was successful. Sleep tight!\n"
        return err_msg
    
    def copy_music(self, widget):
        """is given a [str], all of which are absolute paths to music files the user wants
        to be copied to his VIP. go go, get the job done."""
        
        print "copy_music aufgerufen", self.tracklist
        err_check = False
        err_file=""
        
        # MAJOR FUCKING TODO: ensure that the HD is actually mounted at /mnt/music or let
        # the user provide the mount point (fugly)
        for files in self.tracklist:
            print "for-schleife aufgerufen"
            sys = os.system('scp "%s" "%s:%s"' % (files, 'root@'+self.e_ip.get_text(),'/mnt/music') )
            print 'scp "%s" "%s:%s"' % (files, 'root@'+self.e_ip.get_text(),'/mnt/music') 
            if sys is not 0:
                print "err occured"
                err_check = True
                err_file+="\n"+files
        if err_check:
            print "musiccopyfail"
            return "\n -*we had difficulties copying the following files:"+err_file
        #return ""
    
    def ctabpop(self, buff):
        """popup window that shows the crontab. deprecated, but who knows, I might ned it someday.""" 

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # a fixed size may not be the best of ideas, but for now, this will do
        window.resize(1000,500)
        window.set_position(gtk.WIN_POS_CENTER)
        ct_text=gtk.TextView(buff)
        ct_text.set_editable(False)
        window.add(ct_text)
        window.show_all()

    # mach die eintraege crontabkompatibel und gib sie als liste im Format
    # [["mm hh"]] aus.
    def parse_times(self):
        new_days= []
        nondigit=False
        for i in range(0,7):
            #lese jeden wochentagsstring aus und mach ihn passend
            strs = self.days[i].get_text()
            lst = strs.split(",")
            correct_times = []
            #nun habe ich zB ["12:35","13:5"] und muss noch min & h verdrehen
            for j in lst:
                tmp= j.split(":")
                for k in range(0,len(tmp)):
                    tmp[k] = tmp[k].strip()
                    #check for non-digit chars
                    if not tmp[k].isdigit() and tmp[k] != "":
                        print "nondigit: "+str(tmp[k])
                        tmp[k]=""
                        nondigit=True
                if len(tmp)==1: tmp.append("00")
                tmp.reverse()
                tmp = " ".join(tmp)
                correct_times.append(tmp)
            new_days.append(correct_times)
        #if there have been non-digit chars, notify the user
        return new_days, nondigit

    def event_popup(self, msg):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.resize(300,100)
        window.set_position(gtk.WIN_POS_CENTER)
        err_txt=gtk.TextView(msg)
        err_txt.set_editable(False)
        window.add(err_txt)
        window.show_all()

    def choose_music(self,widget):
        # filechooser (no shit)
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("allowed music formats (mp3)")
        filter.add_mime_type("audio/mpeg")
        chooser.add_filter(filter)

        chooser.set_select_multiple(True)
        
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            print chooser.get_filenames(), 'selected'
         # note: The get_filenames() method returns a list containing 
         # all the selected files and subfolders in the current folder 
         # of the chooser. The returned names are full absolute paths. 
         # If files in the current folder cannot be represented as local 
         # filenames they will be ignored. (See the get_uris() method for more information)
            self.tracklist.extend(chooser.get_filenames())
            print "tracklist: ", self.tracklist
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        chooser.destroy()

    def delete_event(self, widget, event, data=None):
        print "somebody tried to quit this."
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()    

    def main(self):
        gtk.main()

if __name__ == "__main__":
    pj = PyJama()
    pj.main()

# todos:
# (callbacks sauber)
# displaying tracks that are already on the VIP
# playlist uploading/editing
# make the GUI less of an eyesore
# finally get some object orientation into this thing!
""" # -- "select music" button, filechooser poppt auf und wenn man ausgewählt hat kommt die liste. 
da kann man dann nochmal entfernen und hinzufügen und danach auf "upload music", 
woraufhin man die möglichkeit hat "schließen" oder "Musikordner anzeigen" zu machen """
