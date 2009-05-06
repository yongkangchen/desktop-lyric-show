#! /usr/bin/python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 
from socket import *
from time import ctime
import urllib2
import gobject
import urllib
import threading
import gtk
from kanglogLyric import TTDownLoadLyric,lyricApp
gobject.threads_init()
class LyricServer(threading.Thread):
	def __init__(self,lyricApp):
		super(LyricServer, self).__init__()
		self.quit = False
		self.lyricApp=lyricApp
	def run(self):
		HOST='localhost'
		PORT=8080
		BUFSIZ=4096
		ADDR=(HOST,PORT)
		tcpSerSock = socket(AF_INET, SOCK_STREAM)
		tcpSerSock.bind(ADDR)
		tcpSerSock.listen(100)
		while not self.quit:
			gtk.gdk.threads_enter()
			tcpCliSock,addr = tcpSerSock.accept()
			gtk.gdk.threads_leave()
			data = tcpCliSock.recv(BUFSIZ)
			if not data:
				tcpCliSock.close()
				continue
			#print data
			begin=data.find("GET /")+1
			end=data.find("?")
			begin2=data.find('=')+1
			end2=data.find('HTTP/1.1')
			action=data[(end+1):(begin2-1)].strip()
			value=data[begin2:end2]
			#print 'action('+action+')\n'
			if action=='setLyric':
				LrcText=urllib.unquote(value)
				LrcText=LrcText.strip()
				self.lyricApp.set_lyric_text(LrcText)
			elif action=="getLyric":
				print value
				value=value.split("+")
				artist=urllib.unquote(value[0])
				if len(value)>1:				
					title=urllib.unquote(value[1])
				else:
					title=""
				lyric=TTDownLoadLyric.GetTTLyric(artist,title)
				if lyric:
					tcpCliSock.send(lyric)
				#self.quit = True
			tcpCliSock.close()
		print "socket close"
		tcpSerSock.close()
if __name__ == '__main__':
	lyricApp=lyricApp.LyricApp()
	lyricServer=LyricServer(lyricApp)
	lyricServer.start()
	gtk.main()
	lyricServer.quit = True	
