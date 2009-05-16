#!/usr/bin/env python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 

import gtk
import gtk.glade
import pango
import gobject
import TTDownLoadLyric,LyricKeyWords
class ConfigWindow():
	def __init__(self,lyric):		
		myGlade=gtk.glade.XML("conf/conf.glade")
		conf_win=myGlade.get_widget("conf_win")
		conf_win.hide()
		conf_win.connect("delete-event",self.hide)

		treeview=myGlade.get_widget("treeview")

		column = gtk.TreeViewColumn("Id",gtk.CellRendererText(),text=0)
		column.set_sort_column_id(0)
		treeview.append_column(column)

		column = gtk.TreeViewColumn("Artist",gtk.CellRendererText(),text=1)
		column.set_sort_column_id(1)
		treeview.append_column(column)

		column = gtk.TreeViewColumn("Title",gtk.CellRendererText(),text=2)
		column.set_sort_column_id(2)
		treeview.append_column(column)

		liststore = gtk.ListStore(str,str, str)
		treeview.set_model(liststore)
		myGlade.signal_autoconnect({
		"on_cancel_button_clicked":lambda b:self.hide(),
		"on_ok_button_clicked":self.save_conf,
		"on_searchTAbutton_clicked":(self.search_lyric,'kanglog'),
		'on_notebook_switch_page':self.notebook_switch_page,
		'on_searchKeyWordsbutton_clicked':self.search_lyric_keyWords
		})
		self.conf_win=conf_win
		self.myGlade=myGlade
		self.treeview=treeview
		self.notebook=myGlade.get_widget("notebook")
		self.lyric=lyric
		self.fontbutton=myGlade.get_widget("fontbutton")
		self.fontcolorbutton=myGlade.get_widget("fontcolorbutton")
		self.title_entry=self.myGlade.get_widget("title_entry")
		self.artist_entry=self.myGlade.get_widget("artist_entry")
		self.keyWords_entry=self.myGlade.get_widget("keyWords_entry")
		self.currentSong=None
		self.setLyric=None
		self.setSongProperty=None
	def search_lyric_keyWords(self,w):
		keywords=self.keyWords_entry.get_text()
		result=LyricKeyWords.search(keywords)
		liststore=self.treeview.get_model()
		if result:
			self.artist_entry.set_text(result[0])
			self.title_entry.set_text(result[1])
			self.search_lyric()
	def getPageTextByNum(self,page_num):
		table=self.notebook.get_nth_page(page_num)
		label_text=self.notebook.get_tab_label(table).get_text()
		return label_text
	def notebook_switch_page(self,notebook, page, page_num):
		#print 'initpage',page_num
		label_text=self.getPageTextByNum(page_num)
		if label_text=='Lyric':
			#print 'init lyric page:'
			song=self.currentSong()
			if song:
				self.artist_entry.set_text(song['artist'])
				self.title_entry.set_text(song['title'])
			self.treeview.get_model().clear()
		elif label_text=='Font':
			#print 'init Font page:'
			self.fontbutton.set_font_name(self.lyric.get_font_description().to_string())
			self.fontcolorbutton.set_color(self.lyric.get_data("fgcolor"))
	def save_conf(self,w):
		page_num=self.notebook.get_current_page()
		label_text=self.getPageTextByNum(page_num)
		if label_text=='Lyric':
			#print 'change lyric and save song tags:'
			model,ite= self.treeview.get_selection().get_selected()
			#print model.get_string_from_iter(ite)
			if ite and model:
				Id=model.get_value(ite,0)
				artist=model.get_value(ite,1)
				title=model.get_value(ite,2)
				lyric=TTDownLoadLyric.DownLoadLyric(
					unicode(Id,"utf-8"),
					unicode(artist,"utf-8"),
					unicode(title,"utf-8")
					)
				#print lyric
				if lyric:
					self.setLyric(lyric)
					if self.setSongProperty:
						self.setSongProperty(artist,title)
		elif label_text=='Font':
			#print 'save Font-desc and color:'
			self.lyric.set_font_description(pango.FontDescription(self.fontbutton.get_font_name()))
			gobject.idle_add(self.lyric.emit,"style-set","font_desc")
			self.lyric.set_data("fgcolor",self.fontcolorbutton.get_color())
			gobject.idle_add(self.lyric.emit,"style-set","font_fgcolor")
		self.hide()
	def search_lyric(self,w=None,e=None):
		#print 'search_lyric:',self.artist_entry.get_text(),self.title_entry.get_text()
		artist=unicode(self.artist_entry.get_text(),"utf-8")
		title=unicode(self.title_entry.get_text(),"utf-8")
		result=TTDownLoadLyric.SearchLyric(artist,title)
		liststore=self.treeview.get_model()
		liststore.clear()
		for res in result:
			liststore.append([res[0],res[1],res[2]])
	def hide(self,w=None,e=None):
		self.conf_win.hide()
		return True
	def show(self):
		page=self.notebook.get_current_page()
		self.notebook_switch_page(self.notebook,None,page)
		self.conf_win.show()
if __name__=="__main__":
	win=ConfigWindow()
	win.show()
	gtk.main()

