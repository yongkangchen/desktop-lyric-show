#! /usr/bin/python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 
from kanglogLyric import AbstractLyricServer
import thread,gtk
class LyricGMB(AbstractLyricServer.AbstractLyricServer):
	def isPlaying(self):
		return self.proxy.Playing()
	def getPosition(self):
		return self.proxy.GetPosition()
	def getCurrentSong(self):
		return self.proxy.CurrentSong()
	def __init__(self):
		super(LyricGMB,self).__init__(
			config={'object_name':'org.gmusicbrowser',
				'object_path':'/org/gmusicbrowser',
				'SongChanged':'SongChanged'})
if __name__=="__main__":
	import warnings
	warnings.filterwarnings('ignore')
	lyricServer=LyricGMB()
	lyricServer.start()
	gtk.main()
	thread.exit()
