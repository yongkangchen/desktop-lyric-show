#! /usr/bin/python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 
#
# Copyright 2007 Sevenever
# Copyright (C) 2007 Sevenever
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
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


import sys
import locale
import codecs
import urllib2
import random
from xml.dom.minidom import parse, parseString

def DetectCharset(s):
	if isinstance(s,unicode):
		return s
	#charsets = ('iso-8859-1', 'gbk', 'utf-8', 'utf-16')
	charsets = ('gbk','iso-8859-1', 'utf-8', 'utf-16')
	for charset in charsets:
		try:
			#return unicode(unicode(s, 'utf-8').encode(charset), 'utf-8')
			return unicode(s,charset)
		except:
			continue
	return s

def CodeFunc(Id, data):
	length = len(data)
	
	tmp2=0
	tmp3=0
	
	tmp1 = (Id & 0x0000FF00) >> 8							#右移8位后为0x0000015F
															#tmp1 0x0000005F
	if ( (Id & 0x00FF0000) == 0 ):
		tmp3 = 0x000000FF & ~tmp1							#CL 0x000000E7
	else:
		tmp3 = 0x000000FF & ((Id & 0x00FF0000) >> 16)		#右移16位后为0x00000001
	
	tmp3 = tmp3 | ((0x000000FF & Id) << 8)					#tmp3 0x00001801
	tmp3 = tmp3 << 8										#tmp3 0x00180100
	tmp3 = tmp3 | (0x000000FF & tmp1)						#tmp3 0x0018015F
	tmp3 = tmp3 << 8										#tmp3 0x18015F00
	if ( (Id & 0xFF000000) == 0 ) :
		tmp3 = tmp3 | (0x000000FF & (~Id))					#tmp3 0x18015FE7
	else :
		tmp3 = tmp3 | (0x000000FF & (Id >> 24))			#右移24位后为0x00000000
	
	#tmp3	18015FE7
	
	i=length-1
	while(i >= 0):
		char = ord(data[i])
		if char >= 0x80:
			char = char - 0x100
		tmp1 = (char + tmp2) & 0x00000000FFFFFFFF
		tmp2 = (tmp2 << (i%2 + 4)) & 0x00000000FFFFFFFF
		tmp2 = (tmp1 + tmp2) & 0x00000000FFFFFFFF
		#tmp2 = (ord(data[i])) + tmp2 + ((tmp2 << (i%2 + 4)) & 0x00000000FFFFFFFF)
		i -= 1
	
	#tmp2 88203cc2
	i=0
	tmp1=0
	while(i<=length-1):
		char = ord(data[i])
		if char >= 128:
			char = char - 256
		tmp7 = (char + tmp1) & 0x00000000FFFFFFFF
		tmp1 = (tmp1 << (i%2 + 3)) & 0x00000000FFFFFFFF
		tmp1 = (tmp1 + tmp7) & 0x00000000FFFFFFFF
		#tmp1 = (ord(data[i])) + tmp1 + ((tmp1 << (i%2 + 3)) & 0x00000000FFFFFFFF)
		i += 1
	
	#EBX 5CC0B3BA
	
	#EDX = EBX | Id
	#EBX = EBX | tmp3
	tmp1 = (((((tmp2 ^ tmp3) & 0x00000000FFFFFFFF) + (tmp1 | Id)) & 0x00000000FFFFFFFF) * (tmp1 | tmp3)) & 0x00000000FFFFFFFF
	tmp1 = (tmp1 * (tmp2 ^ Id)) & 0x00000000FFFFFFFF
	
	if tmp1 > 0x80000000:
		tmp1 = tmp1 - 0x100000000
	return tmp1

def EncodeArtTit(str):
	rtn = ''
	str = DetectCharset(str).encode('UTF-16')[2:]
	for i in range(len(str)):
		rtn += '%02x' % ord(str[i])
	
	return rtn

def SearchLyric(artist, title):
	try:
		theurl = 'http://lrcct2.ttplayer.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0' % (EncodeArtTit(artist.replace(' ','').lower()), EncodeArtTit(title.replace(' ','').lower()))
		# print theurl
		txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
		req = urllib2.Request(theurl, None, txheaders)
		# create a request object
		
		handle = urllib2.urlopen(req)
		# and open it to return a handle on the url
	except IOError, e:
		print 'We failed to open "%s".' % theurl
		if hasattr(e, 'code'):
			print 'We failed with error code - %s.' % e.code
		elif hasattr(e, 'reason'):
			print "The error object has the following 'reason' attribute :"
			print e.reason
		return False
	else:
		#return handle.read()
		xmlback=handle.read()
		print xmlback
		dom1=parseString(xmlback)
		list = dom1.getElementsByTagName('lrc')
		#li = []
		#for node in list:
		#	li.append((node.getAttribute('id'),node.getAttribute('artist'),node.getAttribute('title')))
		#print li
		if list.length==0:
			print "There is no lyric for search"
			return False
		node=list[0]
		return node.getAttribute('id'),node.getAttribute('artist'),node.getAttribute('title')
		#szList = ""
		#for i in li:
		#	szList += 'id=%s\tartist=%s\ttitle=%s\n' % (i[0], i[1], i[2])
		
		#return szList

def DownLoadLyric(Id, artist, title):
	try:
		theurl = 'http://lrcct2.ttplayer.com/dll/lyricsvr.dll?dl?Id=%d&Code=%d&uid=01&mac=%012x' % (int(Id),CodeFunc(int(Id), DetectCharset(artist + title).encode('UTF8')), random.randint(0,0xFFFFFFFFFFFF))
		print theurl
		txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
		req = urllib2.Request(theurl, None, txheaders)
		# create a request object
		
		handle = urllib2.urlopen(req)
		# and open it to return a handle on the url
	except IOError, e:
		print 'We failed to open "%s".' % theurl
		if hasattr(e, 'code'):
			print 'We failed with error code - %s.' % e.code
		elif hasattr(e, 'reason'):
			print "The error object has the following 'reason' attribute :"
			print e.reason
		return False
	else:
		return handle.read()
def GetTTLyric(artist,title):
	#artist = artist.decode(locale.getdefaultlocale()[1])
	#title = title.decode(locale.getdefaultlocale()[1])
	artist=DetectCharset(artist)
	title=DetectCharset(title)
	print 'Searching ', artist, title, '...'
	
	result = SearchLyric(artist,title)
	if result:
		print result
		lyr = DownLoadLyric(result[0],result[1],result[2])
		#print lyr
		return lyr
	else :return False
	#f = file('tmp.lyr','w')
	#f.write(lyr)
	#f.close()
def main():
	GetTTLyric(sys.argv[1],sys.argv[2])
def __main():
	artist = sys.argv[1].decode(locale.getdefaultlocale()[1])
	title = sys.argv[2].decode(locale.getdefaultlocale()[1])
	print 'Searching ', artist, title, '...'
	
	id,artist,title = SearchLyric(artist,title)
	
        print id,artist,title
        
	lyr = DownLoadLyric(id,artist,title)
	print lyr
	#f = file('tmp.xml','w')
	#f.write(szList)
	#f.close()
	f = file('tmp.lyr','w')
	f.write(lyr)
	f.close()
	
	"""
	if len(li) > 0:
		print "count=%d" % len(li)
		j = 1
		for i in li:
			print '[%d]\tid=%s\tartist=%s\ttitle=%s' % (j, i[0], i[1], i[2])
			j += 1
			
		try:
			command=raw_input('Choise:')
		except EOFError:
			command=='0'
		
		command = int(command) - 1
		if command>=0 and command<len(li):
			print DownLoadLyric(li[command][0],li[command][1],li[command][2])
	else:
		print 'No lyrics found'
	"""
	
	return 0


if __name__ == '__main__':
	main()

