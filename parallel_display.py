# WARNING: For all overrided methods see display.py for documentation

import RPi.GPIO as GPIO
import time

# Define GPIO to LCD mapping
LCD_RS = 16
LCD_E  = 18
LCD_D4 = 15
LCD_D5 = 17
LCD_D6 = 19
LCD_D7 = 21
 
''' COMMANDS FOR LCD DISPLAY '''
# Commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# Flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# Flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# Flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00
 
# Define some device constants
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 2nd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 2nd line
 
# Flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

class parallel_display(display.display):
	# Method for LCD initialization
	''' OVERRIDED FROM DISPLAY '''
	def lcd_initialize(self):		
		# Initialize GPIO
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BOARD)     # Use BOARD CN8 numbers
		GPIO.setup(LCD_E, GPIO.OUT)  # E
		GPIO.setup(LCD_RS, GPIO.OUT) # RS
		GPIO.setup(LCD_D4, GPIO.OUT) # DB4
		GPIO.setup(LCD_D5, GPIO.OUT) # DB5
		GPIO.setup(LCD_D6, GPIO.OUT) # DB6
		GPIO.setup(LCD_D7, GPIO.OUT) # DB7
		
		self.lcd_byte(0x33, LCD_CMD) # 110011 Initialise
		self.lcd_byte(0x32, LCD_CMD) # 110010 Initialise
		self.lcd_byte(LCD_ENTRYMODESET | LCD_ENTRYLEFT, LCD_CMD) # Cursor move direction
		self.lcd_byte(LCD_DISPLAYCONTROL | LCD_DISPLAYON, LCD_CMD) # Display On,Cursor Off, Blink Off
		self.lcd_byte(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE, LCD_CMD) # Data length, number of lines, font size
		self.lcd_byte(LCD_CLEARDISPLAY, LCD_CMD) # 000001 Clear display
		time.sleep(E_DELAY)
  
	# Toggle backlight on/off, it uses a variable with stored data
	''' OVERRIDED FROM DISPLAY '''
	def lcd_backlight(self, state):
		if state == True:
			self.lcd_byte(LCD_BACKLIGHT, LCD_CMD)
		elif state == False:
			self.lcd_byte(LCD_NOBACKLIGHT, LCD_CMD)
		
	# Toggle enable
	def lcd_toggle_enable(self):
		time.sleep(E_DELAY)
		GPIO.output(LCD_E, True)
		time.sleep(E_PULSE)
		GPIO.output(LCD_E, False)
		time.sleep(E_DELAY)

	# Send byte to data pins
	# bits = data
	# mode = True  for character
	#        False for command
	def lcd_byte(self, bits, mode):
		GPIO.output(LCD_RS, mode) # RS

		# High bits
		GPIO.output(LCD_D4, False)
		GPIO.output(LCD_D5, False)
		GPIO.output(LCD_D6, False)
		GPIO.output(LCD_D7, False)
		if bits&0x10==0x10:
			GPIO.output(LCD_D4, True)
		if bits&0x20==0x20:
			GPIO.output(LCD_D5, True)
		if bits&0x40==0x40:
			GPIO.output(LCD_D6, True)
		if bits&0x80==0x80:
			GPIO.output(LCD_D7, True)

		# Toggle 'Enable' pin
		self.lcd_toggle_enable()

		# Low bits
		GPIO.output(LCD_D4, False)
		GPIO.output(LCD_D5, False)
		GPIO.output(LCD_D6, False)
		GPIO.output(LCD_D7, False)
		if bits&0x01==0x01:
			GPIO.output(LCD_D4, True)
		if bits&0x02==0x02:
			GPIO.output(LCD_D5, True)
		if bits&0x04==0x04:
			GPIO.output(LCD_D6, True)
		if bits&0x08==0x08:
			GPIO.output(LCD_D7, True)

		# Toggle 'Enable' pin
		self.lcd_toggle_enable()
  
	
	# Write whole message to LCD - uses \n as new line !!
	''' OVERRIDED FROM DISPLAY '''
	def lcd_message(self, text):
		count = 1
		self.lcd_byte(LCD_LINE_1, LCD_CMD)
		
		# Iterate through all chars in message
		for char in text:
			# Check if char is \n -> go to new line
			if char == '\n':
				if (count == 1 and self.rows >= 2):
					self.lcd_byte(LCD_LINE_2, LCD_CMD)
				elif (count == 2 and self.rows >= 3):
					self.lcd_byte(LCD_LINE_3, LCD_CMD)
				elif (count == 3 and self.rows >= 4):
					self.lcd_byte(LCD_LINE_4, LCD_CMD)
				count = count + 1
			else:
				self.lcd_byte(ord(char), LCD_CHR)
				
	# Load custom characters into display CGRAM (0 - 7)
	''' OVERRIDED FROM DISPLAY '''
	def lcd_load_custom_chars(self, fontdata):
		self.lcd_byte(0x40, LCD_CMD)
		for char in fontdata:
			for line in char:
				self.lcd_byte(line, LCD_CHR)
