import RPi.GPIO as GPIO
import time

# This class will send commands to MPD client from buttons
class buttons():
	# Class constructor
	# Buttons pins is a dictionary with button_name=>pin_number format
	def __init__(self, button_pins, bounce_time):
		# Set bounce time
		self.bounce_time = bounce_time
		
		# Set buttons
		self.buttons = button_pins
	
		# Set GPIO numbering mode
		GPIO.setmode(GPIO.BOARD)
		
		# We don't need warnings from GPIO
		GPIO.setwarnings(False)
		
		# Set button GPIO pins as inputs and enable interrupts
		for button in button_pins:
			if (button_pins[button] != False):
				GPIO.setup(button_pins[button], GPIO.IN, pull_up_down = GPIO.PUD_UP)
				GPIO.add_event_detect(button_pins[button], GPIO.FALLING, callback=self.button_pressed, bouncetime=self.bounce_time)
			
		# Initalize MPD
		self.mpd = False
			
	# Register MPD client to send it commands
	def register(self, mpd):
		self.mpd = mpd
			
	def button_pressed(self, channel):
		# Debouncing
		time.sleep(0.05)
		button = False
		# Find out which button was pressed
		if (self.buttons['NEXT_BUTTON'] != False and (GPIO.input(self.buttons['NEXT_BUTTON']) == 0)):
			button = 'NEXT'
		elif ((self.buttons['PREV_BUTTON'] != False) and (GPIO.input(self.buttons['PREV_BUTTON']) == 0)):
			button = 'PREV'
		elif ((self.buttons['VDN_BUTTON'] != False) and (GPIO.input(self.buttons['VDN_BUTTON']) == 0)):
			button = 'VDN'
		elif ((self.buttons['VUP_BUTTON'] != False) and (GPIO.input(self.buttons['VUP_BUTTON']) == 0)):
			button = 'VUP'
		elif ((self.buttons['PLAY_BUTTON'] != False) and (GPIO.input(self.buttons['PLAY_BUTTON']) == 0)):
			button = 'PLAY'
		elif ((self.buttons['STOP_BUTTON'] != False) and (GPIO.input(self.buttons['STOP_BUTTON']) == 0)):
			button = 'STOP'
		if(button != False):
			self.mpd.commands(button)
