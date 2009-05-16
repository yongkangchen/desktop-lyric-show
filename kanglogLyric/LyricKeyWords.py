#! /usr/bin/python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 
from urllib2 import Request, urlopen, URLError
import urllib2
import re
def decode(html):
	#print "@@@@@@@@",html
	codeReg=re.compile('&#[\d]+;')
	ite=codeReg.finditer(html)
	res=""
	n=0
	for e in ite:
		#print e.groupreplace("<[/]*b>","")(),e.span()
		res+=html[n:e.start()]
		n=e.end()
		words=e.group()
		res+=unichr(int(words[2:len(words)-1]))
		#print int(e.group()[2:7])
	res+=html[n:]
	return res
def parse(html):
	html=re.sub('<[/]*b>', '', html)
	reg='<td class=\"%s[ BottomBorder]*\">[\n]*<a[^>]*>[^<]*';
	titleReg=re.compile(reg%'Title')
	artistReg=re.compile(reg%'Artist')
	titles=titleReg.findall(html)
	artists=artistReg.findall(html)
	#print len(titles)
	if len(titles)>0:
		#print titles[0]
		return decode(artists[0].split(">")[2]),decode(titles[0].split(">")[2])
	else:
		return None
	'''
	li=[]
	for i in range(0,len(titles)):
		title=decode(titles[i].split(">")[2])
		artist=decode(artists[i].split(">")[2])
		li.append((title,artist))
	return li
	'''
def search(key):
	req = Request("http://www.google.cn/music/search?q=%s"%urllib2.quote(key))
	#print "http://www.google.cn/music/search?q=%s"%urllib2.quote(key)
	try:
		response = urlopen(req)
	except URLError, e:
		if hasattr(e, 'reason'):
			print 'We failed to reach a server.'
			print 'Reason: ', e.reason
		elif hasattr(e, 'code'):
			print 'The server couldn\'t fulfill the request.'
			print 'Error code: ', e.code
	else:
		html=response.read()
		#print html
		res=parse(html)
		#print res[0]
		#print res[1]
		return res
if __name__=="__main__":
	search('if i can see it')
