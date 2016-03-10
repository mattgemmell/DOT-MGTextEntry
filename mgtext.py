#! /usr/bin/python

"""
MGText
Text-entry plugin for Pimoroni's menu system for the Raspberry Pi Display-O-Tron.

Code and info: https://github.com/mattgemmell/DOT-MGTextEntry

By: Matt Gemmell
	http://mattgemmell.com/
	http://twitter.com/mattgemmell
"""

from dot3k.menu import MenuOption

_UP = 0
_DOWN = 1
_LEFT = 2
_RIGHT = 3

class MGText(MenuOption):
	def __init__(self):

		self.cols = 16
		self.initialized = False
		
		self.scroll_up_icon = chr(0)
		self.scroll_down_icon = chr(1)
		self.abbreviation_icon = chr(2)
		self.placeholder_icon = chr(3)
		self.caps_on = True
		self.symbols_mode = False
		self.cancel_aborts = False # by default, Cancel button acts as Delete
		self.selection = {'row': 0, 'option': 0}
		self.first_displayed_row = 0
		
		self.uppercase_letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
		self.lowercase_letters = list('abcdefghijklmnopqrstuvwxyz')
		self.space_symbol = 'Spc'
		self.line_break = '\n' # for layout only; can't be entered
		self.numbers = list('0123456789')
		self.quick_punctuation = list('./:@')
		self.symbols = list('./:@\'"~+-=_!?,;()[]<>{}\\^|&*$%#`')
		self.caps_command = "Caps"
		self.symbols_command = "More"
		self.delete_command = "Del"
		self.cancel_command = "Cancel"
		self.commit_command = "Accept"
		self.commands = [self.caps_command, self.symbols_command, self.delete_command, self.cancel_command, self.commit_command]
		
		self.uppercase_set = self.uppercase_letters
		self.uppercase_set.append(self.space_symbol)
		self.uppercase_set.extend(self.numbers)
		self.uppercase_set.extend(self.quick_punctuation)
		self.uppercase_set.extend(self.commands)
		
		self.lowercase_set = self.lowercase_letters
		self.lowercase_set.append(self.space_symbol)
		self.lowercase_set.extend(self.numbers)
		self.lowercase_set.extend(self.quick_punctuation)
		self.lowercase_set.extend(self.commands)
		
		self.symbols_set = self.symbols
		self.symbols_set.append(self.line_break)
		self.symbols_set.extend(self.commands)
		
		self.confirm_accept = "Yes"
		self.confirm_cancel = "No"
		self.confirm_quit = "Quit"
		self.confirm_set = [self.confirm_accept, self.confirm_cancel, self.confirm_quit]
		
		self.display_map = [] # 2D array of options
		self.display_ranges = [] # 2D array of range-arrays with option extents

		self.entered_text = ''
		self.confirming = False

		MenuOption.__init__(self)

		self.is_setup = False

	def set_value(self, value):
		self.entered_text = value

	def get_value(self):
		return self.entered_text

	def begin(self):
		self.initialized = False
		self.confirming = False
		self.symbols_mode = False
		self.selection = {'row': 0, 'option': 0}
		self.first_displayed_row = 0
		self.set_value('')
		self.update_display_map()

	def setup(self, config):
		MenuOption.setup(self, config)

	def cleanup(self):
		self.entered_text = ''
		self.display_map = []
		self.display_ranges = []
	
	def update_display_map(self):
		"""
		Builds two datastructures:
		- display_map is an array of rows of the display, with each entry being an array of that row's options as strings.
		- display_ranges is similar, but each row-array contains dictionaries that are ranges of where the corresponding option renders on the display.
		"""
	
		self.display_map = []
		self.display_ranges = []
		options_set = self.uppercase_set if self.caps_on else self.lowercase_set
		if self.symbols_mode:
			options_set = self.symbols_set
		if self.confirming:
			options_set = self.confirm_set
		
		row_len = 0
		self.display_map.append([])
		self.display_ranges.append([])
		
		for opt in options_set:
			if (opt == self.line_break) or ((len(opt) + row_len + 2) > (self.cols - 1)):
				# Start a new row
				self.display_map.append([])
				self.display_ranges.append([])
				row_len = 0
				if opt == self.line_break:
					# We don't actually include line-breaks as options
					continue
			# Add to latest row
			self.display_map[-1].append(opt)
			opt_len = len(opt) + 1 # to account for the leading space
			self.display_ranges[-1].append({'start': row_len, 'len': opt_len})
			row_len += opt_len
	
	def index_of_range_containing(self, row, col):
		"""
		This allows us to move the cursor spatially when going to a different row. For example, consider moving from a row with only two lengthy options, to a row with seven single-character options. If option 2 of 2 was selected on the former row, we wouldn't just want option 2 to be selected on the latter row after the move, because the cursor would seem to jump way over to the left. What we really want is to "move to whatever option is directly above/below the one I already had selected", which is what this method (and the display_ranges structure) allows.
		"""
		if row >= 0 and row < len(self.display_ranges) and col >= 0 and col < self.cols:
			row_ranges = self.display_ranges[row]
			index = len(row_ranges) - 1
			for range in reversed(row_ranges):
				if col >= range['start']:
					break
				index -= 1
		return index
	
	def move_cursor(self, direction):
		# Move cursor appropriately using ranges
		sel_row = self.selection['row']
		sel_opt = self.selection['option']
		sel_orig_row = sel_row
		sel_orig_col = self.display_ranges[sel_row][sel_opt]['start']
		
		if direction == _UP:
			self.selection['row'] = (sel_row - 1) % len(self.display_map)
			self.selection['option'] = self.index_of_range_containing(self.selection['row'], sel_orig_col)
			
		elif direction == _DOWN:
			self.selection['row'] = (sel_row + 1) % len(self.display_map)
			self.selection['option'] = self.index_of_range_containing(self.selection['row'], sel_orig_col)
			
		elif direction == _LEFT:
			# We wrap back onto the previous row when appropriate
			self.selection['option'] = (sel_opt - 1) % len(self.display_map[sel_row])
			# Check to see if we wrapped around
			if self.selection['option'] > sel_opt or len(self.display_map[sel_row]) == 1:
				# Wrap to previous row
				self.selection['row'] = (sel_row - 1) % len(self.display_map)
				self.selection['option'] = len(self.display_map[self.selection['row']]) - 1
				
		elif direction == _RIGHT:
			# We wrap forward onto the next row when appropriate
			self.selection['option'] = (sel_opt + 1) % len(self.display_map[sel_row])
			# Check to see if we wrapped around
			if self.selection['option'] < sel_opt or len(self.display_map[sel_row]) == 1:
				# Wrap to next row
				self.selection['row'] = (sel_row + 1) % len(self.display_map)
				self.selection['option'] = 0
		
		# Sanitise new selection
		self.selection['option'] = max(0, self.selection['option'])
		self.selection['option'] = min(len(self.display_map[self.selection['row']]) - 1, self.selection['option'])
		
		# Update first_displayed_row appropriately
		sel_row = self.selection['row']
		if sel_row < self.first_displayed_row:
			self.first_displayed_row = sel_row
		elif sel_row > self.first_displayed_row + 1:
			self.first_displayed_row = sel_row - 1
	
	def render_row(self, row):
		# Returns the actual rendered full text of a row, with all annotations
		result = ""
		if row >= 0 and row < len(self.display_map):
			row_opts = self.display_map[row]
			row_selected = (self.selection['row'] == row)
			selected_option = self.selection['option']
			for index, opt in enumerate(row_opts):
				# Selection markers
				if row_selected:
					if selected_option == index:
						result += "["
					elif selected_option == (index - 1):
						result += "]"
					else:
						result += " "
				else:
					result += " "
				
				# Option text
				if opt == self.caps_command:
					if self.caps_on:
						result += "lowr"
					else:
						result += "UPPR"
				elif opt == self.symbols_command:
					if self.symbols_mode:
						if self.caps_on:
							result += "ABC1"
						else:
							result += "abc1"
					else:
						result += "#+=$"
				else:
					result += opt
				
				# Special case for end of row
				if index == len(row_opts) - 1:
					# Selection markers
					if row_selected and selected_option == index:
						result += "]"
					else:
						result += " "
					
					# Add any end-of-row padding required
					result += (" " * (self.cols - (len(result) + 1)))
					
					# Scroll indicators
					if row == self.first_displayed_row and row > 0:
						result += self.scroll_up_icon
					elif row == (self.first_displayed_row + 1) and row < (len(self.display_map) - 1):
						result += self.scroll_down_icon
					else:
						result += " "
		return result
	
	def delete(self):
		# Delete last character entered
		if (not self.confirming) and len(self.entered_text) > 0:
			self.entered_text = self.entered_text[:-1]
		
	def left(self):
		self.move_cursor(_LEFT)
		return True
	
	def right(self):
		self.move_cursor(_RIGHT)
		return True

	def up(self):
		self.move_cursor(_UP)
		return True

	def down(self):
		self.move_cursor(_DOWN)
		return True

	def cancel(self):
		if self.cancel_aborts:
			# Confirm quit if we have text
			if len(self.entered_text > 0):
				self.confirming = True
				self.update_display_map()
				self.selection = {'row': 0, 'option': 1}
				self.first_displayed_row = 0
				return False
			else:
				return True
		
		# Delete last character entered
		self.delete()
		return False

	def select(self):
		# Handle all the selectable options and commands
		opt = self.display_map[self.selection['row']][self.selection['option']]
		
		if opt == self.space_symbol:
			self.entered_text += " "
			
		elif opt == self.caps_command:
			self.caps_on = not (self.caps_on)
			self.symbols_mode = False
			self.update_display_map()
			self.selection = {'row': 0, 'option': 0}
			self.first_displayed_row = 0
			
		elif opt == self.symbols_command:
			self.symbols_mode = not (self.symbols_mode)
			self.update_display_map()
			self.selection = {'row': 0, 'option': 0}
			self.first_displayed_row = 0
			
		elif opt == self.delete_command:
			self.delete()
			
		elif opt == self.cancel_command:
			self.confirming = True
			self.update_display_map()
			self.selection = {'row': 0, 'option': 1}
			self.first_displayed_row = 0
			
		elif opt == self.commit_command:
			self.confirming = True
			self.update_display_map()
			self.selection = {'row': 0, 'option': 1}
			self.first_displayed_row = 0
		
		elif opt == self.confirm_accept:
			self.confirming = False
			self.update_display_map()
			self.selection = {'row': 0, 'option': 0}
			self.first_displayed_row = 0
			return True
		
		elif opt == self.confirm_cancel:
			self.confirming = False
			self.update_display_map()
			self.selection = {'row': 0, 'option': 0}
			self.first_displayed_row = 0
		
		elif opt == self.confirm_quit:
			self.confirming = False
			self.update_display_map()
			self.selection = {'row': 0, 'option': 0}
			self.first_displayed_row = 0
			self.cancel_input = True
			return True

		else:
			self.entered_text += opt
		
		return False

	def redraw(self, menu):
		if not self.initialized:
			menu.lcd.create_char(0, [0, 0, 4, 14, 31, 0, 0, 0])  # scroll up icon
			menu.lcd.create_char(1, [0, 0, 0, 31, 14, 4, 0, 0])  # scroll down icon
			menu.lcd.create_char(2, [0, 0, 0, 0, 0, 0, 21, 0])  # abbreviation icon
			menu.lcd.create_char(3, [0, 0, 0, 0, 0, 0, 0, 28])  # placeholder icon
			self.initialized = True

		if not self.confirming:
			# Output the editing row
			text_len = len(self.entered_text)
			if text_len > self.cols:
				menu.write_row(0, self.abbreviation_icon + self.entered_text[text_len - self.cols + 1:])
			else:
				menu.write_row(0, self.entered_text + (self.placeholder_icon * (self.cols - text_len)))
			
			# Output relevant two rows
			if self.first_displayed_row < len(self.display_map):
				menu.write_row(1, self.render_row(self.first_displayed_row))
			else:
				menu.clear_row(1)
			if self.first_displayed_row + 1 < len(self.display_map):
				menu.write_row(2, self.render_row(self.first_displayed_row + 1))
			else:
				menu.clear_row(2)
			
		else:
			# Handle the confirmation screen
			if len(self.entered_text) > self.cols:
				menu.write_option(0, self.entered_text, scroll=True, scroll_repeat=2000)
			else:
				menu.write_row(0, self.entered_text + (" " * (self.cols - len(self.entered_text))))
			menu.write_row(1, 'Confirm?')
			menu.write_row(2, self.render_row(self.first_displayed_row))
