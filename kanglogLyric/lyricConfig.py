#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
class LyricConfig():
	def __init__(self,file_name="conf/config.ini"):
		self.config = ConfigParser.ConfigParser()
		self.config.read(file_name)
		self.file_name=file_name
	def setValue(self,key,value):
		print "set:",key,"->",value
		self.config.set("info", key, value)
	def save(self):
		self.config.write(open(self.file_name, "w"))
	def getValue(self,key):
		return self.config.get("info",key)
	def save_window_position(self,pos_x,pos_y):
		self.setValue("window_pos_x",pos_x)
		self.setValue("window_pos_y",pos_y)
		self.save()
	def get_window_position(self):
		return self.getValue("window_pos_x"),self.getValue("window_pos_y")
	def save_font_desc(self,font_desc):
		self.setValue("font_desc",font_desc)
		self.save()
	def get_font_desc(self):
		return self.getValue("font_desc")
	def get_font_fgcolor(self):
		return self.getValue("font_fgcolor")
	def save_font_fgcolor(self,color):
		self.setValue("font_fgcolor",color)
		self.save()
if __name__=="__main__":
	config=LyricConfig()
	print config.getValue("window_pos_x")
	print config.getValue("window_pos_y")
	print config.getValue("font_desc")
	print config.getValue("font_fgcolor")
	print config.getValue("font_bgcolor")
