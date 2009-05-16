#! /usr/bin/python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import threading
import thread
import time
import gobject
import gtk

#DBusGMainLoop(set_as_default=True)
#bus = dbus.SessionBus()
import TTDownLoadLyric,lyricApp,LyricParse
class AbstractLyricServer(threading.Thread):
	def isPlaying(self):pass
	def getPosition(self):pass
	def getCurrentSong(self):pass
	def setSongProperty(self,title,artist):pass
	def __init__(self,config={'object_name':None,'object_path':None,'SongChanged':None}):
		super(AbstractLyricServer, self).__init__()

		self.quit = False
		self.tc=threading.Condition(threading.Lock())

		menu_items = (
			("/AdjustLyric",None,   self.adjustLyric ,0,None),
		)
		self.song=None
		self.lyric=None
		self.delay=0

		self.lyricApp=lyricApp.LyricApp(menu_items)
		self.lyricApp.confWin.currentSong=self.getSong
		self.lyricApp.confWin.setLyric=self.setLyric
		self.lyricApp.confWin.setSongProperty=self.setSongProperty
		DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus()

		self.proxy=self.bus.get_object(config['object_name'],config['object_path'])
		self.proxy.connect_to_signal(config["SongChanged"],self.changed)
		if self.isPlaying():
			self.changed(None)
		gobject.threads_init()
	def getSong(self):
		return self.song
	def setLyric(self,lyric):
		if lyric:
			self.delay=0
			self.lyric=LyricParse.lrctolist(lyric)
		self.tc.acquire()
		self.tc.notify()
		self.tc.release()
	def run(self):
		while True:
			gtk.gdk.threads_enter()
			if not self.isPlaying() or not self.lyric:
				self.tc.acquire()
				self.tc.wait()
				self.tc.release()
			pos=self.getPosition()*1000+1000+self.delay
			#print "pos:",pos
			try:
				length=len(self.lyric)
			except:
				print self.lyric
				length=0
			lyricText=""
			sleep_time=0
			for i in range(0,length):
				if self.lyric[i][0]<pos:
					continue;
				if i!=0:
					lyricText=self.lyric[i-1][1]
				#print "area:",self.lyric[i][0]
				sleep_time=(self.lyric[i][0]-pos)/1000+1
				#print sleep_time
				break
			self.lyricApp.set_lyric_text(lyricText)
			gtk.gdk.threads_leave()
			print sleep_time
			if sleep_time>30 or sleep_time<1:
				sleep_time=10
			time.sleep(sleep_time)
			#threading.Timer()
	def changed(self,widget):
		print "song changed"
		if not self.isPlaying():return
		song=self.getCurrentSong()
		lyricFile=None
		if song and self.song!=song:
			self.song=song
			artist=song['artist']
			title=song['title']
			self.lyricApp.set_lyric_text("%s - %s"%(title,artist))
			lyricFile=TTDownLoadLyric.GetTTLyric(artist,title)
			if not lyricFile:
				self.lyric=None
		self.setLyric(lyricFile)
	def adjustLyric(self,w,e):
		#global lyricServer
		dialog = gtk.Dialog(None,None,
				     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				     (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
				      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		label =gtk.Label("please input the delay times:")
		label.show()
		dialog.vbox.pack_start(label, True, True, 0)
		entry = gtk.Entry()
		entry.set_text(str(self.delay))
		dialog.vbox.pack_start(entry, True, True, 0)
		entry.show()
		def close_action(d,button):
			if gtk.RESPONSE_ACCEPT==button:
				self.delay=int(entry.get_text())
			d.destroy()
		dialog.connect("response",close_action)
		dialog.run()
