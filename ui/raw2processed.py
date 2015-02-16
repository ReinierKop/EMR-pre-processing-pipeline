from Tkinter import *
from ttk import *

class Raw2Processed:

	def __init__(self):
		self.buttons = dict()
		self.values = dict()

	def make_frame(self, parent, child):
		'''abstract interface to be implemented by the user
		returns the context-dependent frame to be shown to the user'''

	def make_checkbutton(self, f, s, r, c):
		v = BooleanVar()
		ch = Checkbutton(f, text=s, variable=v)
		ch.grid(row=r, column=c, columnspan=2, sticky=W)
		return v, ch

	def make_label(self, f, s, r, c):
		v = StringVar()
		label = Label(f, text=s)
		label.grid(row=r, column=c, sticky=W)
		Entry(f,textvariable=v).grid(row=r, column=c+1, sticky=W+E)	
		return v, label

	def get_values(self):
		'''yields the dictionary of the values of this object.
			these are generated by calling self.get_frame()'''
		return self.values

	def knowledge_only(self):
		enabled = self.values['knowledge-driven'].get()

		for key in self.buttons:
			if key != 'knowledge-driven':
				if not enabled:
					self.buttons[key].config(state=NORMAL)
				if enabled:
					self.values[key].set(False)
					self.buttons[key].config(state=DISABLED)

	def toggle_other_buttons(self, button_key):
		enabled = self.values[button_key].get()

		for key in self.buttons:
			if key != button_key and key not in ['lab_results', 'knowledge-driven']:
				if not enabled:
					self.buttons[key].config(state=NORMAL)
				if enabled:
					self.values[key].set(False)
					self.buttons[key].config(state=DISABLED)
