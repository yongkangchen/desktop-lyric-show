#!/usr/bin/python
# coding: utf-8
import math
import gtk
import gtk.gdk as gdk
import cairo
import pango
import pangocairo
import gobject
import threading
import lyricConfig
class TransLayout(pango.Layout):
	def __init__(self,text,transpWin):
		pango.layout.__init__(self,text)
		self.transpWin=transpWin
class TranspWindow(gtk.Window):
	def __init__(self,type=gtk.WINDOW_TOPLEVEL):
		gtk.Window.__init__(self,type)
		self.set_keep_above(True)
		
		self.config=lyricConfig.LyricConfig()
		
		pos_x,pos_y=self.config.get_window_position()
		if pos_x!="None" and pos_y!="None":
			self.move(int(pos_x),int(pos_y))
		
		darea = gtk.DrawingArea()
		self.add(darea)
		darea.show()
		
		layout = self.create_pango_layout("kanglog lyric")
		layout.set_justify(False)
		
		fontdesc=pango.FontDescription(self.config.get_font_desc());
		layout.set_font_description(fontdesc)
		layout.set_data("bgcolor", gtk.gdk.color_parse("#000000"))
		layout.set_data("fgcolor",gtk.gdk.color_parse(self.config.get_font_fgcolor()))
		
		alignment=pango.ALIGN_CENTER
		layout.set_alignment(alignment)
		
		ellipsize=pango.ELLIPSIZE_NONE
		if ellipsize != pango.ELLIPSIZE_NONE:
			layout.set_wrap(pango.WRAP_WORD)
		try:
			layout.set_ellipsize(ellipsize)
		except AttributeError:
			print "ellipsize attribute not supported, ignored"
			
		max_width=None
		if max_width is None:
			MAX_WIDTH = gdk.screen_width() - 8
		else:
			MAX_WIDTH = max_width - 8
		layout.set_width(pango.SCALE*MAX_WIDTH)

		self.drop_shadow=True
		
		self.darea=darea
		self.layout=layout
		self.MAX_WIDTH=MAX_WIDTH

		
		gobject.signal_new("style-set", pango.Layout,
			gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE,
			(gobject.TYPE_PYOBJECT,))
			
		layout.connect("style-set",self.osd)
		layout.set_text("kanglog lyric")
		layout.emit("style-set",None)
	def osd(self,w,e):
		if e:
			if e=="font_desc":
				self.config.save_font_desc(self.layout.get_font_description().to_string())
				print "save desc@@@@@@@@@@@@"
			elif e=="font_fgcolor":
				self.config.save_font_fgcolor(self.layout.get_data("fgcolor").to_string())
				print "save color@@@@@@@@@@@@"
			pos_x,pos_y=self.get_position()
			self.hide()
		
		darea=self.darea
		MAX_WIDTH=self.MAX_WIDTH
		
		layout=self.layout
		
		BORDER_WIDTH=1
		off_x = BORDER_WIDTH*2
		off_y = BORDER_WIDTH*2
		
		width, height = layout.get_pixel_size()
		
		if layout.get_alignment() == pango.ALIGN_CENTER:
			off_x -= MAX_WIDTH/2 - width/2
		elif layout.get_alignment() == pango.ALIGN_RIGHT:
			off_x -= MAX_WIDTH - width
		width += BORDER_WIDTH*4
		height += BORDER_WIDTH*4
		
		
		if self.drop_shadow:
			self.drop_shadow_distance = max(2, int(\
			layout.get_font_description().get_size()/pango.SCALE*0.1))
			width += self.drop_shadow_distance
			height += self.drop_shadow_distance
		darea.set_size_request(width, height)
		darea.realize()

		pixmap = gtk.gdk.Pixmap(darea.window, width, height)
		bitmap = gtk.gdk.Pixmap(darea.window, width, height, 1)
		darea.window.set_back_pixmap(pixmap, False)
		
		fg_gc = gdk.GC(pixmap); fg_gc.copy(darea.style.fg_gc[gtk.STATE_NORMAL])
		bg_gc = gdk.GC(pixmap); bg_gc.copy(darea.style.fg_gc[gtk.STATE_NORMAL])
		fg_gc.set_foreground(darea.get_colormap().alloc_color(\
			layout.get_data("fgcolor")))
		bg_gc.set_background(darea.get_colormap().alloc_color(\
			layout.get_data("bgcolor")))


		pixmap.draw_rectangle(bg_gc, True, 0, 0, width, height)
		pixmap.draw_layout(fg_gc, off_x, off_y, layout)
		#if debug_frame:
		#    pixmap.draw_rectangle(fg_gc, False, 0, 0, width - 1, height - 1)

		#bitmap.set_colormap(darea.window.get_colormap())

		fg_gc = gdk.GC(bitmap)
		bg_gc = gdk.GC(bitmap)
		fg_gc.set_foreground(gdk.Color(pixel=-1))
		bg_gc.set_background(gdk.Color(pixel=0))

		bitmap.draw_rectangle(bg_gc, True, 0, 0, width, height)

		bitmap.draw_layout(fg_gc, off_x, off_y, layout)
		bitmap.draw_layout(fg_gc, off_x + BORDER_WIDTH, off_y, layout)
		bitmap.draw_layout(fg_gc, off_x + BORDER_WIDTH, off_y + BORDER_WIDTH, layout)
		bitmap.draw_layout(fg_gc, off_x, off_y + BORDER_WIDTH, layout)
		bitmap.draw_layout(fg_gc, off_x - BORDER_WIDTH, off_y + BORDER_WIDTH, layout)
		bitmap.draw_layout(fg_gc, off_x - BORDER_WIDTH, off_y, layout)
		bitmap.draw_layout(fg_gc, off_x - BORDER_WIDTH, off_y - BORDER_WIDTH, layout)
		bitmap.draw_layout(fg_gc, off_x, off_y - BORDER_WIDTH, layout)
		bitmap.draw_layout(fg_gc, off_x + BORDER_WIDTH, off_y - BORDER_WIDTH, layout)

		if self.drop_shadow:
			bitmap.draw_layout(fg_gc, off_x + self.drop_shadow_distance,
					off_y + self.drop_shadow_distance, layout)
		#if debug_frame:
		#    bitmap.draw_rectangle(fg_gc, False, 0, 0, width - 1, height - 1)
		self.window.shape_combine_mask(bitmap, 0, 0)
		if e:
			self.move(pos_x,pos_y)
			self.show()
class LyricApp():
	WINDOW_TYPE_HINT_LOCK=gtk.gdk.WINDOW_TYPE_HINT_SPLASHSCREEN
	WINDOW_TYPE_HINT_UNLOCK=gtk.gdk.WINDOW_TYPE_HINT_TOOLBAR
	def __init__(self):
		self.window=TranspWindow()
		self.window.connect("delete-event",self.lock_action)
		self.window.hide()
		self.window.set_type_hint(self.WINDOW_TYPE_HINT_UNLOCK)
		#self.window.set_position(gtk.WIN_POS_CENTER)
		
		self.window.connect("enter-notify-event", self.move_action)
		
		self.lyric=self.window.layout

		self.window.show_all()
		
		sIcon=gtk.status_icon_new_from_file("images/32.png")
		sIcon.set_tooltip("Desktop lyric")
		#sIcon.set_blinking(True);
		
		menu_items = (
			( "/Font",None,         lambda a,b:FontDialog(self.lyric), 0, None ),
			( "/Color",None,        lambda a,b:ColorDialog(self.lyric), 0, None ),
			( "/Lock",  None,       self.winLock, 0, None),
			( "/Quit",  None,       gtk.main_quit, 0, None ),
		)
		accel_group = gtk.AccelGroup()
		item_factory=gtk.ItemFactory(gtk.Menu,"<main>",accel_group)
		item_factory.create_items(menu_items)

		sIcon.connect("activate",self.lock_action)
		sIcon.connect("popup-menu",self.menu_action)
		self.item_factory=item_factory
		self.menu=item_factory.get_widget("<main>")
	def move_action(self,widget, event):
		window=widget.window
		if window.get_type_hint()==self.WINDOW_TYPE_HINT_UNLOCK:
			window.begin_move_drag(1,int(event.x_root),int(event.y_root), event.time)
	def winLock(self,data,item):
		label=item.child
		if label.get_text()=='Lock':
			lock=True
			label.set_text('Unlock')
		else:
			lock=False
			label.set_text('Lock')
		self.lock(lock)
	def menu_action(self,icon,button,times):
		x,y,z=gtk.status_icon_position_menu(self.menu,icon)
		self.item_factory.popup(x, y,button, times)
	def lock_action(self,widget,event=None):
		self.item_factory.get_item("/Lock").activate()
		return True
	def lock(self,key):
		pos_x,pos_y=self.window.get_position()
		self.window.hide()
		if key:	
			hint=self.WINDOW_TYPE_HINT_LOCK
			self.window.config.save_window_position(pos_x,pos_y)
		else:
			hint=self.WINDOW_TYPE_HINT_UNLOCK
		self.window.set_type_hint(hint)
		self.window.move(pos_x,pos_y)
		self.window.show()
	def set_lyric_text(self,LrcText):
		if LrcText and LrcText!=self.lyric.get_text():
			self.lyric.set_text(LrcText)
			gobject.idle_add(self.lyric.emit,"style-set",None)
			print LrcText
class FontDialog():
	def __init__(self,target):
		fontseldlg = gtk.FontSelectionDialog("Font select")
		
		fontseldlg.set_font_name(target.get_font_description().to_string())
		fontseldlg.show()
		cancel_button=fontseldlg.get_cancel_button()
		fontseldlg.connect("response",self.close_action)
		self.target=target
	def close_action(self,dialog,button):
		if gtk.RESPONSE_OK==button:
			self.target.set_font_description(pango.FontDescription(dialog.get_font_name()))
			gobject.idle_add(self.target.emit,"style-set","font_desc")
		dialog.destroy()
class ColorDialog():
	def __init__(self,target):
		colorseldlg = gtk.ColorSelectionDialog("")
		colorseldlg.connect("response",self.close_action)
		colorsel = colorseldlg.get_color_selection()
		colorsel.set_current_color(target.get_data("fgcolor"))
		colorsel.set_has_opacity_control(True)
		colorsel.set_has_palette(True)
		colorseldlg.show()
		self.target=target
	def close_action(self,dialog,button):
		if gtk.RESPONSE_OK==button:
			self.target.set_data("fgcolor",dialog.get_color_selection().get_current_color())
			gobject.idle_add(self.target.emit,"style-set","font_fgcolor")
		dialog.destroy()
import os
def fop():
	pid = os.fork()
	if pid != 0:
		os._exit(0)
	os.system('python py_transparent_window.py')
if __name__=="__main__":
	lyricApp=LyricApp()
	gtk.main()
