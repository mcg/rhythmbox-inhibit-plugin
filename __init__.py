# Copyright (C) 2010 - Matthew Gregg
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

import rb
import gobject
import dbus
import logging

class InhibitPlugin (rb.Plugin):
#Initialisation 
	def __init__ (self):
		rb.Plugin.__init__ (self)
        def bind_session_bus(self):
                try:
                        self.session_bus = dbus.SessionBus()
                        self.screensaver = self.session_bus.get_object("org.gnome.ScreenSaver","/org/gnome/ScreenSaver")
                        print "bus connected"
                        return True
                except dbus.DBusException:
                        return False
                
	def activate (self, shell):
		self.shell = shell
		self.rb = shell.get_player ()
                self.bind_session_bus() or logging.error("Could not bind session bus")
                self.state_callback_handle = self.rb.connect("playing-changed", self.play_state_changed)
	
	def deactivate (self, shell):
                self.uninhibit_screensaver()# or logging.error("Could not unhibit screensaver")
                self.rb.disconnect(self.state_callback_handle)
                self.session_bus = None
        
        def inhibit_screensaver(self):
                try:
                        self.cookie = self.screensaver.Inhibit('Rhythmbox', 'Disabled by Rhythmbox')
                        print "Inhibiting screensaver"
                        return True
                except dbus.DBusException:
                        return False

        def uninhibit_screensaver(self):
                try:
                        if hasattr(self, 'cookie'):
                                print str(self.cookie)
                                print "Uninhibiting screensaver"
                                self.screensaver.UnInhibit(self.cookie)
                        return True
                except dbus.DBusException:
                        return False

        def play_state_changed(self, rb, playing):
                """ inhibit screensaver on play, uninhibit on pause """
                print "play state: "+str(playing)
                if playing:
                        if hasattr(self, 'cookie'):
                                if self.cookie != None:
                                        self.uninhibit_screensaver() or logging.error("Could not unhibit screensaver")
                        self.inhibit_screensaver() or logging.error("Could not connect events")
                if not playing:
                        self.uninhibit_screensaver() or logging.error("Could not unhibit screensaver")
                        self.cookie = None


