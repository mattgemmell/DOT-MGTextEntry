#!/usr/bin/env python

print("""
This is a demo of the MGText text-entry Menu plugin.

Press CTRL+C to exit.
""")

import dothat.touch as touch
import dothat.lcd as lcd
import dothat.backlight as backlight
from dot3k.menu import Menu, MenuOption
from mgtext import MGText
import time

def reset():
	lcd.clear()
	backlight.graph_off()
	backlight.off()

mgtext = MGText()

menu = Menu(
	structure = {
		'MGText Test': mgtext,
	},
	lcd = lcd,
	input_handler = mgtext)

try:
	touch.bind_defaults(menu)
	
	# Trap the Cancel button for our own purposes (to use as a Delete key).
	@touch.on(touch.CANCEL)
	def handle_cancel(ch, evt):
		mgtext.cancel()
	
	backlight.rgb(192, 124, 234)
	menu.right() # Go straight to text-editing
	
	while 1:
		menu.redraw()
		time.sleep(0.05)

except (KeyboardInterrupt, SystemExit):
	reset()
except:
	reset()
	raise
