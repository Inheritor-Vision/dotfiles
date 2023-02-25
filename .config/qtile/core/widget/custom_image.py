from libqtile import bar, hook
from qtile_extras import widget

class CustomImage(widget.Image):

	defaults = [
		("inactive_background", None, "Color when the widget is not on the current focused screen.")
	]

	def __init__(self, length=bar.CALCULATED, **config):
		widget.Image.__init__(self,length, **config)
		self.add_defaults(CustomImage.defaults)
		self.active_background = self.background

	def _configure(self, qtile, bar):
		widget.Image._configure(self,qtile, bar)
		if self.inactive_background:
			hook.subscribe.current_screen_change(self._update_background)
	
	def _update_background(self):
		if self.qtile.current_screen == self.bar.screen:
			self.background = self.active_background
		else:
			self.background = self.inactive_background

		self.draw()