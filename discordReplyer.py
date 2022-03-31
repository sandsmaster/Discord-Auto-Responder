import win32gui, win32con
import mouse
import keyboard
import time
import datetime
import random
import threading
import PySimpleGUI as sg
import pytesseract
import cv2
import numpy
from PIL import Image, ImageGrab, ImageTk
from appLayout import layout
from appLayout import createChOptionsWnd, authUsers
from pynput.keyboard import Key, Listener, Controller
import inspect

nputKb = Controller()


	
class Replyer:
	"""Main bot class"""


	def __init__(self):
		""""""

		self.ins = {						# Internal vars
			"procName" : 'Discord',
			"mainRunningFlag" : False,			# Signals that the main window is open already
			"timerThr" : None,   				# The timer thread
			"LinesIntervalThr" : None,			# The line-change watch thread
			"timerStopFlag" : False,			# Stops the timer
			"lookForDiscordFlag" : True,		# Focus Discord flag
			"rndLinesFlag" : False,				# Change line to be written to the chat
			"rndLoopIntervalFlag" : False,		# Random delay between loops
			"rndLinesIntervalFlag" : False,		# Random delay between lines
			"diffChannelFlag" : False,			# Change the current channel	
			"LinesIntervalThrRunning" : False,	# Signals if a line interval thread is running
			"fullList" : False,					# Writes the full list of words
			"searchPhrase" : "- Discord",		# Window name to look for		
			"dateTimer" : False,				# Flag for the date timer thread 
			"findPhraseFlag" : False,			# Flag for the Word Recognition option
			"stopDateFlag" : False,				# Flag to stop the timer on certain date
			"xChanged" : False,					# Flag to show if x changed
			"startKey" : None,					# Key for starting the main thread
			"stopKey" : None,					# Key for stopping the main thread
			"hotkeyChanged" : False				# True if hotkey got changed
		}

		self.chOptions = {					# Options for the channel switching
			"delayFlag" : False,				# Flag for the regular delay (1 argument needed)
			"rndDelayFlag" : False,				# Flag for the random delay (2 argument needed)
			"delayTime" : [],					# Delay(s) for the change
			"chDelayPassedFlag" : False,		# Wheather the wait thread finished waiting before channel switch
			"chTimerThr" : None,				# The thread for delay calculation
			"channels" : [],					# Channel names
			"chNumber" : 0,						# Number of channel in the array
			"chSwitchingNow" : False			# Flag to prevent simultaneous typing, while channel switching
		}

		self.lineNum = 0 						# line change counter
		self.ScreenText = ""					# the text on screen, if findPhraseFlag is set
		self.logoName = "miniMetaempLogo.png"
		self.typingAllowedNow = True			# Flag to prevent simultaneous typing


	def setDateTimer(self, setMoment, checkInterval=0.25):
		"""Sets Timer to break on specific date
		   checks every [checkInterval] seconds"""

		self.ins["dateTimer"] = True
		while (datetime.datetime.now() < setMoment) and not self.ins["timerStopFlag"]:
			time.sleep(checkInterval)
		self.ins["dateTimer"] = False


	def changeLineInterval(self, delayStart, delayEnd=''):
		"""Calculates the next text line to write"""
		
		delay = delayStart
		self.ins["LinesIntervalThrRunning"] = True 	# safety check
		while not self.ins["timerStopFlag"]:
			time.sleep(delay)
			try:
				# if end delay range is set
				delay = int(delayStart) + (random.random()*(int(delayEnd)-int(delayStart)))
			except:
				# if only beginning delay range is set
				delay = int(delayStart)

			self.lineNum += 1
			self.ins["xChanged"] = True
		self.ins["LinesIntervalThrRunning"] = False


	def focusWind(self, hwnd):
		"""Tries to focus Discord
		   Wait 10 seconds in case of fail and try again
		"""
		try:
			win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
			win32gui.SetForegroundWindow(hwnd)
		except:
			time.sleep(10)
			try:
				win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
				win32gui.SetForegroundWindow(hwnd)
			except err as Exception:
				print(err)

	def ScreenToText(self, x, y, w, h):
		"""Extracts the text from the screen in the specified square
		"""
		pytesseract.pytesseract.tesseract_cmd = ".\\tesseract\\tesseract.exe"
		pil_image = ImageGrab.grab(bbox=(x,y,w,h)).convert('RGB') 
		open_cv_image = numpy.array(pil_image) 
		open_cv_image = open_cv_image[:, :, ::-1].copy()
		self.ScreenText = pytesseract.image_to_string(open_cv_image)


	def typeText(self, text):
		"""Types text and prevents thread race errors"""
		self.typingAllowedNow = False
		nputKb.type(text)
		self.typingAllowedNow = True		


	def getWindowDimensions(self, hwnd):
		"""Returns position and size of the windown [hwnd] points to"""
		rect = win32gui.GetWindowRect(hwnd)
		rect = list(rect)
		rect[2] -= rect[0]	# rect[0] = x position;	rect[2] = width 
		rect[3] -= rect[1]	# rect[1] = y position;	rect[3] = height
		return rect


	def WriteToDiscord(self, hwnd, spamPhrase):
		"""Focuses and sends text to Discord (callback)"""

		if not self.ins["timerStopFlag"]:	# if stop is pressed
			if self.ins["lookForDiscordFlag"] or self.ins["findPhraseFlag"]: # if Discord needs focus 
				windowTitle = win32gui.GetWindowText(hwnd)
				if (self.ins["searchPhrase"] in windowTitle) and (windowTitle != "Discord Auto-Replyer"): # if hwnd points to Discord

					self.ins["searchPhrase"] = windowTitle
					self.focusWind(hwnd)

					x, y, w, h = self.getWindowDimensions(hwnd)
					
					if self.ins["findPhraseFlag"]:
						self.ScreenToText(x+400, y, w+100, h) # read from chat
					mouse.move(x+400, y+h-50, True, 0)	# move cursor on text field for typing
					
					mouse.click()
					if spamPhrase:
						while self.chOptions["chSwitchingNow"]:
							time.sleep(0.2)
						self.typeText(spamPhrase)
						keyboard.send('Enter')
			else:
				while self.chOptions["chSwitchingNow"]:
					time.sleep(0.2)
				self.typeText(spamPhrase)
				keyboard.send('Enter')


	def pickWordFromList(self, wordsCount, loopIter, lineIntervalStart, lineIntervalEnd):
		"""Chooses a word from the list and returns it's index
		   doesn't require the list
		"""
		try:
			lineIntervalStart = int(lineIntervalStart)
			try:
				lineIntervalEnd = int(lineIntervalEnd)
			except:
				lineIntervalEnd = 0
		except:
			lineIntervalStart = 0

		try:
			if lineIntervalStart > 0:
				if self.ins["rndLinesIntervalFlag"]:

					if not self.ins["LinesIntervalThrRunning"]:
						self.ins["LinesIntervalThr"] = threading.Thread(target=self.changeLineInterval, args=([lineIntervalStart, lineIntervalEnd]), daemon=True)
						self.ins["LinesIntervalThr"].start()	
					if self.ins["xChanged"]:
						if self.ins["rndLinesFlag"]:
							spamIndex = int(random.random()*(wordsCount-1))
						else:
							spamIndex = self.lineNum - (int(self.lineNum / wordsCount)*wordsCount)	
						self.ins["xChanged"] = False
				else:
					if not self.ins["LinesIntervalThrRunning"]:
						self.ins["LinesIntervalThr"] = threading.Thread(target=self.changeLineInterval, args=([lineIntervalStart]), daemon=True)
						self.ins["LinesIntervalThr"].start()
					if self.ins["rndLinesFlag"]:
						spamIndex = int(random.random()*(wordsCount-1))
					else:
						spamIndex = self.lineNum - (int(self.lineNum / wordsCount)*wordsCount)	
			else:
				if self.ins["rndLinesFlag"]:
					spamIndex = int(random.random()*(wordsCount-1))
				else:
					spamIndex = loopIter - (int(loopIter / wordsCount)*wordsCount)				
		except Exception as e:
			if self.ins["rndLinesFlag"]:
				spamIndex = int(random.random()*(wordsCount-1))
			else:
				spamIndex = loopIter - (int(loopIter / wordsCount)*wordsCount)

		return int(spamIndex)


	def checkForCriteria(self, criteria, wordsList, wordsCount):
		spamPhrase = ""
		criterias = [x for x in criteria.split("\n") if ":" in x]
		if self.ScreenText:
			for x in criterias:
				if x[x.find(":")+1:].strip() in self.ScreenText:	# if the part after ":" in criteria is found on screen
					spamIndex = int(x[:x.find(":")].strip())-1		# get index of the correstponding line in words list
					if spamIndex < 0 or spamIndex > wordsCount-1:
						print("spamIndex out of range")
					else:
						spamPhrase += "\n %s" % (wordsList[spamIndex])
		return spamPhrase


	def runSpammer(self, window, values):
		"""Runs the spam bot"""

		while self.ins["dateTimer"] == True:							# check if custom start date is set
			window["loopStatus"].update("Waiting for start date")
			time.sleep(0.4)
																		# init interanals
		self.ins["lookForDiscordFlag"] = values["DiscordCheck"]
		self.ins["rndLinesFlag"] = values["rndLine"]
		self.ins["rndLoopIntervalFlag"] = values["rndLoopCount"]
		self.ins["rndLinesIntervalFlag"] = values["rndLineInterval"]
		self.ins["diffChannelFlag"] = values["diffChannel"]
		self.ins["fullList"] = values["fullList"]
		self.ins["findPhraseFlag"] = values["findPhraseCheck"]

		wordsList = values['words'].split("\n")
		spamPhrase = '-'	# 1 item from wordsList
		spamIndex = 0		# index to not go out of range for wordsList

		try:
			loopCount = int(values['loops'])	# get number of loops
		except:
			loopCount = 864000
			window["loops"].update("10 days")

		try:
			waitTime = int(values['LoopIntervalStart']) # get time between loops
		except:
			waitTime = 0

		self.lineNum = 0
		loopIter = 0
		if self.ins["findPhraseFlag"]:
			self.lineNum -= 1
			loopIter -= 1

		if self.ins["diffChannelFlag"]:
				self.ins["chTimerThr"] = threading.Thread(target=self.UpdateChDelay, args=([]), daemon=True)
				self.ins["chTimerThr"].start()


		while loopIter < loopCount and not self.ins["timerStopFlag"]:	# start looping and typing

			try:
				if self.ins["stopDateFlag"]:	# if date to stop is set
					stopDate = datetime.datetime.strptime(values["stopDate"]+" "+values["stopTime"], '%d/%m/%y %H:%M:%S')
					print(stopDate)
					if datetime.datetime.now() > stopDate:
						# Stop date reached. Stopping timer
						break
			except Exception as e:
				print("No stop date set")

			start = time.time()

			while self.checkForFocus(): # safety check - pauses bot if it's focused
				window["loopStatus"].update("Paused - Switch to chat window")
				time.sleep(0.5)
				if self.ins["timerStopFlag"]:
					return False

			wordsCount = len(wordsList)
			spamIndex = self.pickWordFromList(wordsCount, loopIter, values["lineIntervalStart"], values["lineIntervalEnd"])
			spamPhrase = wordsList[spamIndex]						# get list from the GUI

			if self.ins["fullList"]:	# option to send all words together
				spamPhrase = "\n".join(wordsList)

			if self.ins["findPhraseFlag"]: # option to find text on screen
				spamPhrase = self.checkForCriteria(values["criteria"], wordsList, wordsCount)

			for j in range(waitTime):								# loop wait time
				while self.checkForFocus():
					window["loopStatus"].update("Paused - Switch to chat window")
					time.sleep(0.3)
					if self.ins["timerStopFlag"]:
						return False

				window["loopStatus"].update("%d seconds" % (waitTime-j))
				time.sleep(1)
				if self.ins["timerStopFlag"]:
					window["loopStatus"].update("Stopped")
					return

			while self.checkForFocus():
				window["loopStatus"].update("Paused - Switch to chat window")
				time.sleep(0.5)
				if self.ins["timerStopFlag"]:
					return False
			
			if self.ins["rndLoopIntervalFlag"]:
				try:
					waitTime = int(values['LoopIntervalStart']) + int(random.random() * (int(values['LoopIntervalStop']) - int(values['LoopIntervalStart'])))
					if waitTime < 0:
						waitTime = 0
				except:
					pass
			loopIter += 1

			if self.ins["lookForDiscordFlag"] or self.ins["findPhraseFlag"]:
				self.ins["searchPhrase"] = "- Discord"
				win32gui.EnumWindows(self.WriteToDiscord, spamPhrase)	# Run the function to write to the chat (callback)
			else:
				self.WriteToDiscord(None,spamPhrase)


			self.ins["diffChannelFlag"] = values["diffChannel"]									# change channel if needed

			if self.ins["diffChannelFlag"]:
				if self.chOptions["chDelayPassedFlag"]:
					self.changeChannel()


			window["loopWatch"].update("loops %d/%d" % (loopIter, loopCount))	# write loops on screen

		window["loopStatus"].update("Stopped")
		window["loopWatch"].update("loops 0/0")
		self.ins["timerThr"] = None
		self.ins["timerStopFlag"] = True


	def UpdateChDelay(self):
		"""Calculates the delay between channel change"""

		while True:
			if self.ins["diffChannelFlag"]:
				if self.chOptions["rndDelayFlag"]:
					try:
						startDelay = int(self.chOptions["delayTime"][0])
						stopDelay = int(self.chOptions["delayTime"][1])
						delay = startDelay + int(random.random()*(stopDelay - startDelay))
					except:
						try:
							delay = startDelay + int(random.random()*10)
						except:
							delay = int(random.random()*30)
				elif self.chOptions["delayFlag"]:
					try:
						startDelay = int(self.chOptions["delayTime"][0])
						delay = startDelay
					except:
						delay = 1
				else:
					delay = 1

				for i in range(delay):
					time.sleep(1)
					if self.ins["timerStopFlag"]:
						self.chOptions["chTimerThr"] = None
						return

				self.chOptions["chDelayPassedFlag"] = True



	def changeChannel(self):
		"""Changes the channel"""
		self.chSwitchingNow = True
		keyboard.send("Control+K")														# open "switch channel" menu
		try:																			# try to write the channel
			self.typeText(self.chOptions["channels"][self.chOptions["chNumber"]])
		except:
			self.typeText(self.chOptions["channels"][0])
			self.chOptions["chNumber"] = 0
		time.sleep(0.3)
		keyboard.send("Enter")
		keyboard.send("Escape")
		self.chSwitchingNow = False
		self.chOptions["chDelayPassedFlag"] = False										# signal that channel changed


		if self.chOptions["chNumber"] < len(self.chOptions["channels"]):				# check and change channels arr index 
			self.chOptions["chNumber"] += 1
		else:
			self.chOptions["chNumber"] = 0


	def checkForFocus(self):
		"""Checks if the bot is in focus"""
		wndHasFocus = False
		wndName = win32gui.GetWindowText(win32gui.GetForegroundWindow())
		if wndName == "Discord Auto-Replyer":
			wndHasFocus = True
		return wndHasFocus


	def convToReadableKey(self, keyName):
		"""Makes key names readable"""
		if "Key." in keyName:
			keyName = keyName[4:]

		if keyName == "'_'" or keyName == "'''":
			if "_" in keyName:
				keyName = "_"
			else:
				keyName = "'"
		else:
			if "_" in keyName:
				keyName = keyName.replace("_", " ")

			if "'" in keyName :
				keyName = keyName.replace("'", "")

		if "[" in keyName and "]" in keyName:
			keyName = keyName.replace("[","")
			keyName = keyName.replace("]","")

		if any(specKey in keyName for specKey in ["alt", "ctrl", "shift"]):
			keyName = keyName.replace("alt l","Left Alt")
			keyName = keyName.replace("alt gr","Right Alt")
			keyName = keyName.replace("ctrl l","Left Control")
			keyName = keyName.replace("ctrl r","Right Control")
			if keyName == "shift r":
				keyName = keyName.replace("shift r","Right Shift")
			else:
				keyName = keyName.replace("shift","Left Shift")


		return keyName.title()


	def hotkeyUpdate(self, window):
		"""Runs the release key hook"""
		
		try:
			def on_release(key):
				"""Checks if event was release of the specified keys in a new thread"""
				if self.typingAllowedNow:
					if key == self.ins["startKey"]:
						window.write_event_value("startKey", None)
					if key == self.ins["stopKey"]:
						window.write_event_value("stopKey", None)
			with Listener(on_release=on_release) as listener:
				listener.join()
		except:
			pass

	def windowObj(self):
		"""Main GUI update loop"""
		window = sg.Window('Discord Auto-Replyer', layout) # creating the GUI

		hotkeyChecker = threading.Thread(target=self.hotkeyUpdate, args=([window]), daemon=True)
		hotkeyChecker.start()

		# run thread for hotkey Start here.
		# read window inside and pass values

		while True:
			event, values = window.read()   # Read the event that happened and the values dictionary

			self.ins["rndLinesFlag"] = False
			self.ins["lookForDiscordFlag"] = False
			self.ins["rndLoopIntervalFlag"] = False

			if event == sg.WIN_CLOSED or event == 'Exit':	 # If user closed window with X or if user clicked "Exit" button then exit
				break

			if event in ['Start','startKey']:
				self.ins["timerStopFlag"] = False
				if not self.ins["mainRunningFlag"]:
					self.ins["mainRunningFlag"] = True
					self.ins["timerThr"] = threading.Thread(target=self.runSpammer, args=([window, values]), daemon=True)
					self.ins["timerThr"].start()
					self.ins["mainRunningFlag"] = False


			if event in ['Stop','stopKey']:
				self.ins["timerStopFlag"] = True
				window["loopStatus"].update("Stopped")

			if event == 'getFile':	# read from a text file
				filename = sg.PopupGetFile('Select the text list', no_window=True)
				if filename:
					content = []
					with open(filename,"rt") as file:
						for line in file:
							if line[-1] == "\n":
								content.append(line[:-1])
							else:
								content.append(line)
				window['words'].update("\n".join(content))

			if event == "setDateTime":
				if values["startTimeLabel"] == "True":
					setDate = datetime.datetime.strptime(values["startDate"]+" "+values["startTime"], '%d/%m/%y %H:%M:%S')
					if self.ins["dateTimer"]:
						self.ins["timerStopFlag"] = True
						time.sleep(0.4)
						self.ins["timerStopFlag"] = False
					else:
						self.ins["timerStopFlag"] = False
					self.ins["timerThr"] = threading.Thread(target=self.setDateTimer, args=([setDate]), daemon=True)
					self.ins["timerThr"].start()
				else:
					self.ins["timerStopFlag"] = True

			if event == "setStopDateTime":
				if values["stopTimeLabel"] == False:
					self.ins["stopDateFlag"] = False
				else:
					self.ins["stopDateFlag"] = True					

			
			if event == "startShortcut":					# set start shorcut func
				def on_release(key):
					self.ins["startKey"] = key
					self.ins["hotkeyChanged"] = True

				with Listener(on_release=on_release) as ls:
				
					self.ins["hotkeyChanged"] = False
					def time_out():
						while not self.ins["hotkeyChanged"]:
							time.sleep(0.2)  # Listen to keyboard for period_sec seconds
						ls.stop()

					threading.Thread(target=time_out, args=(), daemon=True).start()
					ls.join()

				keyVisual = self.convToReadableKey(str(self.ins["startKey"]))

				window["startShortcut"].update('Start Key - {0}'.format(keyVisual))

			
			if event == "stopShortcut":						# set stop shorcut func
				def on_release(key):
					self.ins["stopKey"] = key
					self.ins["hotkeyChanged"] = True

				with Listener(on_release=on_release) as ls:
				
					self.ins["hotkeyChanged"] = False
					def time_out():
						while not self.ins["hotkeyChanged"]:
							time.sleep(0.2)  
						ls.stop()

					threading.Thread(target=time_out, args=(), daemon=True).start()
					ls.join()

				keyVisual = self.convToReadableKey(str(self.ins["stopKey"]))

				window["stopShortcut"].update('Stop Key - {0}'.format(keyVisual))

			if event == "chooseChannels":
				ch_window = createChOptionsWnd("\n".join(self.chOptions["channels"]))
				while True:
					ch_event, ch_values = ch_window.read()
					if ch_event == "Exit" or ch_event == sg.WIN_CLOSED:
						break

					if ch_event == "setChannelSettings":
						self.chOptions["channels"] = ch_values["channels"].split("\n")
						self.chOptions["chNumber"] = 0
						self.chOptions["delayFlag"] = ch_values["channelDelayFlag"]
						self.chOptions["rndDelayFlag"] = ch_values["randomChDelayFlag"]
						try:
							self.chOptions["delayTime"] = [int(ch_values["minChDelay"])]
							self.chOptions["delayTime"].append(int(ch_values["maxChDelay"]))
						except:
							print("Some delay value isn't a whole number")
							try:
								pass
							except Exception as e:
								self.chOptions["delayTime"] = [10]

						break

				ch_window.close()

def runApp():
	x = Replyer()
	x.windowObj()

def main_menu():
	authUsers(runApp) # main auth window

if __name__ == "__main__":
	main_menu()