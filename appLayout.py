import PySimpleGUI as sg
from AuthGG import *
from auth import AuthGG_api
import datetime

sg.theme('Black')

layout_l = [ 
			[sg.Button('Start'), sg.Button('Stop'), sg.Text("Hello",key="loopStatus")],
			[sg.Multiline(['Multiline', 'Multiline 2'], key='words',  s=(34,16))],
			[sg.Text('loops 0/0', key="loopWatch"), sg.Button('Load File',key="getFile"), sg.Checkbox('Send Full List',key='fullList')]]

layout_r_all = [
				[
					[sg.Col([[sg.Text('Loops'),sg.Text('Interval')],  
					[sg.Input(s=(7,2),key='loops'),sg.Input(s=(7,2),key='LoopIntervalStart'),sg.Input(s=(7,2),key='LoopIntervalStop')],  
					[sg.Checkbox('Random interval',key='rndLoopCount')],
					[sg.Text('Line change Interval')],
					[sg.Input(s=(5,2),key='lineIntervalStart'),sg.Input(s=(5,2),key='lineIntervalEnd')],
					[sg.Checkbox('Random line change delay',key='rndLineInterval')],
					]),

					sg.Col([[sg.Text('Random Lines')],
					[sg.Checkbox('Enabled',key='rndLine')],
					[sg.Text('Channel Switch')],
					[sg.Checkbox('Enabled',key='diffChannel')],
					[sg.Button('Set Channels',key="chooseChannels")],
					[sg.Text('Look for Discord')],
					[sg.Checkbox('Enabled',key='DiscordCheck')],
					])],
					[sg.Multiline('This is where you can specify the phrases to look for in the chat\n Example:\n 2: Cake\n This means: print the second line, if you find the word "cake" or "Cake"',s=(34,10),key='criteria')]
					],
					
					[[sg.Text('Time To Start')],
					[sg.Checkbox('Enabled',key='startTimeLabel'), sg.Button('Set Timer',key="setDateTime")],
					[sg.Text('Date Format:(DD/MM/YY)')],
					[sg.Input((datetime.datetime.now().strftime('%d/%m/%y')),s=(15,2),key='startDate')],
					[sg.Text('Time Format:(HH:MM:SS)')],
					[sg.Input((datetime.datetime.now().strftime('%H:%M:%S')),s=(15,2),key='startTime')],
					[sg.Text('Time To Stop')],
					[sg.Checkbox('Enabled',key='stopTimeLabel'), sg.Button('Set Timer',key="setStopDateTime")],
					[sg.Text('Date')],
					[sg.Input(s=(15,2),key='stopDate')],
					[sg.Text('Time')],
					[sg.Input(s=(15,2),key='stopTime')]]
			]

layout_r = [[sg.Col(layout_r_all[0]),sg.Col(layout_r_all[1])],
			[sg.Button('Start Key - ', key='startShortcut', font='_ 10'), sg.Button('Stop Key: ', key='stopShortcut', font='_ 10'), sg.Checkbox('Text Recognition',key='findPhraseCheck')]]

layout = [[sg.MenubarCustom([['File', ['Exit', 'made by sandsmaster']]], p=0)],
		  [sg.Text('Greater Discord Auto-Replyer', font='_ 18', justification='c')],
		  [sg.Col(layout_l), sg.Col(layout_r)]]



def createChOptionsWnd(mlText='Enter channels here'):
	if mlText == []:
		mlText = 'Enter channels here'
	ch_layout = [[sg.Checkbox('Enable Delay', key="channelDelayFlag"), sg.Checkbox('Random Delay', key="randomChDelayFlag")],
			[sg.Input('Main / Min Delay', s=(15,2), key="minChDelay"), sg.Input('Maximum Delay', s=(15,2), key="maxChDelay")],
			[sg.Multiline(mlText, key='channels',  s=(34,16))],
			[sg.Button('Apply', key="setChannelSettings")]
			]

	ch_window = sg.Window("Channels window", ch_layout, element_justification='center')
	print("- Window created")
	return ch_window

def createAuthWnd():
	login_layout = [[sg.Text("", key="errLog")],
					[sg.Text("Username")],
					[sg.Input("", key="log_nickname")],
					[sg.Text("Password")],
					[sg.Input("", key="log_passwd", password_char='*')],
					[],
					[],
					[sg.Button("Log in", pad=((10,0),(10,0)), key="log"), sg.Button("Register", pad=((10,0),(10,0)), key="go_reg"), sg.Button("Forgot Password", pad=((10,0),(10,0)), key="go_forg")]
					]

	register_layout = [	[sg.Text("", key="errReg")],
						[sg.Text("Username")],
						[sg.Input("", key="reg_nickname")],
						[sg.Text("License")],
						[sg.Input("", key="reg_license")],
						[sg.Text("E-mail")],
						[sg.Input("", key="reg_email")],
						[sg.Text("Password")],
						[sg.Input("", key="reg_passwd", password_char='*')],
						[sg.Text("Password")],
						[sg.Input("", key="reg_passwd", password_char='*')],
						[sg.Button("Register", pad=((10,0),(15,0)), key="reg"), sg.Button("Back", pad=((10,0),(15,0)), key="go_log")]
						]

	forgot_pwd_layout = [[sg.Text("Username")],
						[sg.Input("", key="forg_nickname")],
						[sg.Text("We will send you an email with link to reset your password.\n The link will expire in 24 hours", pad=((0,0),(15,40)), key="forg_txt")],
						[sg.Button("Send E-mail", key="forg"), sg.Button("Back", key="go_log")]]	

	auth_layout = [[sg.Text("Discord Auto-Replyer", font="_ 20")],
					[sg.Col(login_layout, visible=True, key="log_gui"), sg.Col(register_layout, visible=False, key="reg_gui"), sg.Col(forgot_pwd_layout, visible=False, key="forg_gui")]]

	auth_window = sg.Window("Log-in Window", auth_layout, element_justification='center')
	print("- Window created")
	return auth_window

def changeLayout(wnd,num):
	gui_names = ["log_gui", "reg_gui", "forg_gui"]	# list of gui keys

	for x in gui_names:
		wnd[x].update(visible=False)				# hide everything

	wnd[gui_names[num]].update(visible=True)		# show the wanted one
	print(gui_names[num])

	return wnd

def failPopup(message):
	err_layout = [
					[sg.Text(message, pad=(50,30))],
					[sg.Button("Ok")]
					]
	err_wnd = sg.Window("Warning Window", err_layout)

	while True:
		err_values, err_events = err_wnd.read()
		if err_events in ("ok", "Exit", sg.WIN_CLOSED):
			break

def authUsers(runApp):
	auth_window = createAuthWnd()
	print("before init")


	AID = "329121"
	SECRET = "dobXWTEVx6DXcczdzmNGbLivAVKWhN0zyP6"
	API_KEY = "5632887281174293663979986"
	AuthGG.Initialize(AID, SECRET, API_KEY, "0.9")

	auth_event, auth_values = auth_window.read()
	#auth_window.bind("<Enter>", "log")
	while True:
		auth_event, auth_values = auth_window.read()
		print("after init")
		if auth_event == "Exit" or auth_event == sg.WIN_CLOSED:
			break

		if "go_log" in auth_event:
			auth_window = changeLayout(auth_window, 0)

		if auth_event == "go_reg":
			auth_window = changeLayout(auth_window, 1)
			auth_window["errLog"].update("")
			auth_window["errReg"].update("")	

		if auth_event == "go_forg":
			auth_window = changeLayout(auth_window, 2)
			auth_window["errLog"].update("")
			auth_window["forg_txt"].update("")

		if auth_event == "log":
			if not AuthGG.can_login:
				os._exit(0)
			else:
				username = auth_values["log_nickname"]
				password = auth_values["log_passwd"]
				print("nickname and password recieved")
				loginFlag = AuthGG.Login(username, password)
				if loginFlag == True and type(loginFlag) == bool:
					print("this is ok")
					auth_window.close()
					runApp()
					os._exit(0)
				else:
					print("Log-in unsuccessful")
					auth_window["errLog"].update("Mistake in nickname/password")

		if auth_event == "reg":
			if not AuthGG.can_register:
				print("[!] Register is not enabled, please try again later!")
				auth_window["errReg"].update("Register is not enabled, please try again later!")
			else:
				username = auth_values["reg_nickname"]
				password = auth_values["reg_passwd"]
				email = auth_values["reg_email"]
				license = auth_values["reg_license"]
				if password != auth_values["reg_passwd0"]:
					auth_window["errReg"].update("Passwords don't match. Please try again")
					continue

				for field in [username,password,email,license]:
					if field.strip() == "":
						auth_window["errReg"].update("Please fill in all fields")
						continue

				registerFlag = AuthGG.Register(username, password, email, license)
				if registerFlag and type(registerFlag) == bool:
					print("[!] You have successfully registered!")
					auth_window = changeLayout(auth_window, 0)
					auth_window["errLog"].update("You have successfully registered!")
					auth_window["errReg"].update("")
				else:
					auth_window["errReg"].update(registerFlag)
					print(registerFlag)

		if auth_event == "forg":
			AuthGG_api.__init__(
			    aid=AID,
			    apikey=API_KEY,
			    secret=SECRET
			)

			# Returns the output of the request
			response: str = AuthGG_api.Action(
			    _type="forgotpw",
			    username=auth_values["forg_nickname"],
			)

			auth_window["forg_txt"].update("Successfully sent E-mail reset reques!\n check your mail inbox")

			if "Server error" in response:
				auth_window["forg_txt"].update("The user can't be found")
			else:
				auth_window["forg_txt"].update(response)