#! /usr/bin/env python
# -*- coding: utf-8 
import pygtk
pygtk.require('2.0')
import gtk

class PyJama:
     # warning: I never said it was going to be pretty.
     # this little script provides a klickibunti Environment that lets you create
     # crontabs für viirus' DIY alarm clock: http://f.pherth.net/vip/

     # todo? callbacks, sicherstellen dass nur zahlen "," und ":" eingegeben werden, 

     def __init__(self):
          #create window
          self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
          
          # create actual containers
          self.daybox= gtk.VBox()
          labelbox = gtk.VBox()
          self.allbox = gtk.HBox()

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
          #self.window.connect("delete_event". self.delete_event)
          
          # add & show geraffel
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
          self.allbox.add(labelbox)
          self.allbox.add(self.daybox)
          self.window.add(self.allbox)
          self.window.show_all()


     #popup window with finished crontab
     def ctabpop(self, widget):
          buff = gtk.TextBuffer(table=None)
          times = self.parse_times()
     # aus irgendeinem Grund erzeugt das 6 statt 7 zeilen.. wtf
          for i in range (0,7):
               weekday=times[i]
               for j in weekday:
                    buff.insert(buff.get_end_iter(), "& "+j+" * * "+ str(i+1) +" sh /flash2/alarm-clock \n")
          window = gtk.Window(gtk.WINDOW_TOPLEVEL)
          # a fixed size may not be the best of ideas, but for now, this will do.
          window.resize(1000,500)

          ct_text=gtk.TextView(buff)
          ct_text.set_editable(False)
          window.add(ct_text)
          window.show_all()
          print "tadaa"
     
     # mach die eintraege crontabkompatibel und gib sie als liste im Format
     # [["mm hh"]] aus.
     def parse_times(self):
          new_days= []
          for i in range(0,7):
               #lese jeden wochentagsstring aus und mach ihn passend
               strs = self.days[i].get_text()
               lst = strs.split(",")
               #print(lst)
               correct_times = []
               #nun habe ich zB ["12:35","13:5"] und muss noch min & h verdrehen
               for j in lst:
                    tmp= j.split(":")
                    #klappt noch nicht so recht
                    for k in range(0,len(tmp)):
                         tmp[k] = tmp[k].strip()
                    if len(tmp)==1: tmp.append("00")
                    tmp.reverse()
                    tmp = " ".join(tmp)
                    correct_times.append(tmp)
               new_days.append(correct_times)
               print("ct" +str(correct_times) +"ct")
          return new_days

     #whatever this actually does (or doesn't, according to the interpreter)...
     # evtl wenn ctrl-d gedrueckt?
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


     
