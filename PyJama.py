#! /usr/bin/env python
# -*- coding: utf-8 

import ConfigParser
import os
import pygtk
pygtk.require('2.0')
import gtk
import string

class PyJama:
    # warning: I never said it was going to be pretty.
    # this little script provides a klickibunti Environment that lets you create
    # crontabs für viirus' DIY alarm clock: http://f.pherth.net/vip/
    
    # this will only work if you've got your VIP's sshd up&running and 
    # didn't set a root password. 
    # (yess, will fix the latter.)

    def __init__(self):
        self.create_window()
        self.load_config()
        self.show_window()

    def create_window(self):
        #create window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        
        # create actual containers
        self.ipbox= gtk.HBox()
        self.daybox= gtk.VBox()
        labelbox = gtk.VBox()
        buttonbox = gtk.HBox()
        self.timebox = gtk.HBox()
        self.allbox = gtk.VBox()

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
        l_space = gtk.Label(None)

        #creating the buttons (duh)
        #button_show = gtk.Button("show crontab")
        button_scp = gtk.Button("Set Alarm")
        # !! idee: "launcher" methode, die das vospiel fuer beide macht und je nach uebergebenem parameter 
        # dann koper- oder anzeigemethode aufruft. -> TODO: connections neu
        # & klaeren: muss das self. sein?
        #button_show.connect("clicked", self.launcher,"show")
        button_scp.connect("clicked",self.launcher, "copy")
        
        #killswitch
        self.window.connect("destroy", self.destroy)
        #self.window.connect("delete_event". self.delete_event)'
        
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
        labelbox.add(l_space)
        #buttonbox.add(button_show)
        buttonbox.add(button_scp)
        self.timebox.add(labelbox)
        self.timebox.add(self.daybox)
        self.allbox.add(self.ipbox)
        self.allbox.add(self.timebox)
        self.allbox.add(buttonbox)
        self.window.add(self.allbox)

    def show_window(self):
        self.window.show_all()
    
    def load_config(self):
        #loading the configs to the window's panels
        self.config=ConfigParser.ConfigParser()
        self.pyjamapath = os.path.expanduser('~')+'/.config/PyJama/'
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


    def launcher(self, widget, button_action):
        # will keep the button_action thingamabob in case there are other buttons in the future
        self.store_settings()
        
        #prepare for the arrival of event messages
        ev_msg=gtk.TextBuffer(table=None)
        ev_msg.set_text("we've got news for you: \n ===================================================== \n")
        if button_action is "copy":
            # copy crontab and collect generated event messages
            ev_msg.insert_at_cursor(self.copy_ctab(widget))
        # pop up collected error messages:
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
            
        # hier noch wecklied etc speichern.
        
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
        
        # doppelt gemoppelt, weiss aber nicht wie ich das sonst abfragensparsamer 
        # implementieren soll.
            
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
        
        #check if the scp was successful and display an error message if not
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
        
    def ctabpop(self, buff):
        """popup window that shows the crontab""" 

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

# todo? (callbacks), sicherstellen dass nur zahlen "," und ":" eingegeben werden,
    
