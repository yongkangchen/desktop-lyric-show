#! /usr/bin/python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from kanglogLyric import TTDownLoadLyric,LyricParse,lyricApp
import threading
import time
import gobject
import gtk
#DBusGMainLoop(set_as_default=True)
#from dbus.mainloop.glib import DBusGMainLoop
#dbus_loop = DBusGMainLoop()
#bus=dbus.SessionBus(mainloop=loop)
#dbus.set_default_main_loop
#class ShowThread()
class LyricServer(threading.Thread):
	def __init__(self,lyricApp):
		super(LyricServer, self).__init__()
		self.quit = False
		self.tc=threading.Condition(threading.Lock())
		self.lyricApp=lyricApp
		self.song=None
		self.lyric=None
		#self.lyricApp.set_lyric_text(LrcText)

		bus = dbus.SessionBus()

		self.proxy=bus.get_object('org.gmusicbrowser','/org/gmusicbrowser')
		self.proxy.connect_to_signal("SongChanged",self.changed)
		if self.proxy.Playing():
			self.changed(None)
		gobject.threads_init()
	def run(self):
		while not self.quit:
			gtk.gdk.threads_enter()
			if not self.proxy.Playing() or not self.lyric:
				self.tc.acquire()
				self.tc.wait()
				self.tc.release()
			pos=self.proxy.GetPosition()*1000+1000
			print "pos:",pos
			length=len(self.lyric)
			for i in range(0,length):
				if self.lyric[i][0]<pos:
					continue;
				if i==0:
					lyricText=""
				else :lyricText=self.lyric[i-1][1]
				print "area:",self.lyric[i][0]
				sleep_time=(self.lyric[i][0]-pos)/1000+1
				print sleep_time
				break
			self.lyricApp.set_lyric_text(lyricText)
			gtk.gdk.threads_leave()
			if sleep_time<30:
				time.sleep(sleep_time)
				#threading.Timer()
	def changed(self,widget):
		print "song changed"
		song=self.proxy.CurrentSong()
		if self.song!=song:
			self.song=song
			lyricFile=TTDownLoadLyric.GetTTLyric(song['artist'],song['title'])
			if lyricFile:
				self.lyric=LyricParse.lrctolist(lyricFile)
				if not self.lyric:
					return
			else :
				self.lyricApp.set_lyric_text("There is no lyric for search (Kanglog Desktop Lyric show)")
				return
		self.tc.acquire()
		self.tc.notify()
		self.tc.release()
if __name__=="__main__":
	from dbus.mainloop.glib import DBusGMainLoop
	DBusGMainLoop(set_as_default=True)
	lyricApp=lyricApp.LyricApp()
	lyricServer=LyricServer(lyricApp)
	lyricServer.start()
	gtk.main()
	import thread
	thread.exit()
	lyricServer.quit = True
