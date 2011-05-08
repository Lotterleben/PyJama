#! /usr/bin/env python
# -*- coding: utf-8 

import ConfigParser
import os
import pygtk
pygtk.require('2.0')
import gtk

class PyJama:
    # warning: I never said it was going to be pretty.
    # this little script provides a klickibunti Environment that lets you create
    # crontabs für viirus' DIY alarm clock: http://f.pherth.net/vip/
    
    # this will only work if you've got your VIP's sshd up&running and 
    # didn't set a root password. 
    # (yess, will fix the latter.)

    def __init__(self):

        #create window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        
        # create actual containers
        self.ipbox= gtk.HBox()
        self.daybox= gtk.VBox()
        labelbox = gtk.VBox()
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

        #creating the button (duh)
        self.button = gtk.Button("create crontab")
        self.button.connect("clicked", self.ctabpop)
        
        #killswitch
        self.window.connect("destroy", self.destroy)
        #self.window.connect("delete_event". self.delete_event)'
        
        #loading the configs
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
            
        
        # add & show geraffel
        self.ipbox.add(l_ip)
        self.ipbox.add(self.e_ip)
        for i in range(0,7):
            self.daybox.add(self.days[i])
        self.daybox.add(self.button)
        labelbox.add(l_mon)
        labelbox.add(l_tue)
        labelbox.add(l_wed)
        labelbox.add(l_thu)
        labelbox.add(l_fri)
        labelbox.add(l_sat)
        labelbox.add(l_sun)
        labelbox.add(l_space)
        self.timebox.add(labelbox)
        self.timebox.add(self.daybox)
        self.allbox.add(self.ipbox)
        self.allbox.add(self.timebox)
        self.window.add(self.allbox)
        self.window.show_all()


    # popup window with finished crontab. When this is generated, the User's settings
    # will be stored to /home/<user>/.config/PyJama/Pyjama.cfg .
    def ctabpop(self, widget): 
        # MAJOR TODO: scp-operationen und eigentliche crontabesrellung hier
        # raustrieseln und in eigene methoden packen. dann evtl 2 buttons anlegen:
        # "show crontab" und "copy crontab to Box" oder so
       
        # write times to config file so they will never be forgotten.
        #TODO: unhighlight lines when displayed in freshly started program
        #section which contains weekdays. these can be addressed with their index nr.
        # example: 
        # 1: '13:37, 17, 20:00'
        if not self.config.has_section('days'):
            self.config.add_section('days')
        for i in range(0,7):
            self.config.set('days',str(i),self.days[i].get_text())

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

        #and nao: parsing & creating the crontab.
        buff = gtk.TextBuffer(table=None)
        times = self.parse_times()
        
        # creating local the crontab so it can be scp'd. this is only temporary and
        # yes, this is idiotic (see below.). But I really need something to work right now.
        # TODO: fix this mess.

        pyjamatab= open(self.pyjamapath+'crontab', 'w')


        # print crontab to popup & store it in pyjamatab:        
        for i in range (0,7):
            weekday=times[i]
            for j in weekday:
                line = "& "+j+" * * "+ str(i+1) +" sh /flash2/alarm-clock \n"
                buff.insert(buff.get_end_iter(), line)
                pyjamatab.write(line)
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # a fixed size may not be the best of ideas, but for now, this will do.

        pyjamatab.close()

        window.resize(1000,500)

        ct_text=gtk.TextView(buff)
        ct_text.set_editable(False)
        window.add(ct_text)
        window.show_all()
        print "tadaa"
        
        # scp crontab to box:
        # es ist iwie unsinnig, fuer den vorgang die crontab nochmal zwischenzuspeichern.
        # TODO: mal gucken ob ich den buff auch ruebergeschleust bekomm...
        os.system('scp "%s" "%s:%s"' % (self.pyjamapath+'crontab', 'root@'+self.e_ip.get_text(),'/flash2/crontab') )


    # mach die eintraege crontabkompatibel und gib sie als liste im Format
    # [["mm hh"]] aus.
    def parse_times(self):
        new_days= []
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
                if len(tmp)==1: tmp.append("00")
                tmp.reverse()
                tmp = " ".join(tmp)
                correct_times.append(tmp)
            new_days.append(correct_times)
            print("ct" +str(correct_times) +"ct")
        
        return new_days

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

# todo? callbacks, sicherstellen dass nur zahlen "," und ":" eingegeben werden,
    
