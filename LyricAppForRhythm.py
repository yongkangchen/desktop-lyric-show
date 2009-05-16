#! /usr/bin/python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 
from kanglogLyric import AbstractLyricServer
import thread,gtk,dbus

#print song['artist']
#print song['title']

#print proxy.getMute()

#playingChanged
#playingUriChanged
#elapsedChanged
#playingSongPropertyChanged
class LyricGMB(AbstractLyricServer.AbstractLyricServer):
	def isPlaying(self):
		return self.proxy.getPlaying()
	def getPosition(self):
		try:
			return self.proxy.getElapsed()
		except:
			print "Error in getPosition"
			return 0
	def getCurrentSong(self):
		uri=self.proxy.getPlayingUri()
		print "@@@uri:",uri
		if not self.shell:
			self.shell=self.bus.get_object('org.gnome.Rhythmbox','/org/gnome/Rhythmbox/Shell')
		try:
			dic=self.shell.getSongProperties(uri)
			#for k in dic.keys():
			#	print k,":",dic[k]
			return {"artist":dic['artist'],"title":dic['title']}
		except:
			print "Error in getCurrentSong:",uri
			return None
	def __init__(self):
		self.shell=None
		super(LyricGMB,self).__init__(
			config={'object_name':'org.gnome.Rhythmbox',
				'object_path':'/org/gnome/Rhythmbox/Player',
				'SongChanged':'playingChanged'})
		self.proxy.connect_to_signal("playingSongPropertyChanged",self.playingSongPropertyChanged)
		self.uri=None
	def playingSongPropertyChanged(self,uri,prop,old,new):
		print "playingSongPropertyChanged:"
		if uri!=self.proxy.getPlayingUri():return
		self.song=None
		self.changed(None)
	def setSongProperty(self,artist,title):
		#shell=self.bus.get_object('org.gnome.Rhythmbox','/org/gnome/Rhythmbox/Shell')
		uri=self.proxy.getPlayingUri()
		self.shell.setSongProperty(uri,'artist',dbus.String(artist, variant_level=1))
		self.shell.setSongProperty(uri,'title',dbus.String(title, variant_level=1))
		#self.shell.setSongProperty(uri,'album',dbus.String(album, variant_level=1))
if __name__=="__main__":
	#import os
	#os.system('rhythmbox')
	lyricServer=LyricGMB()
	lyricServer.start()
	gtk.main()
	thread.exit()
