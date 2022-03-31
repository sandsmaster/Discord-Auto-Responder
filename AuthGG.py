import requests
import json
import os
import time
import uuid
import sys
import hashlib

class AuthGG:

    def __init__(self):
        self.aid = ""
        self.secret = ""
        self.api_key = ""
        self.version = ""
        self.hash = ""
        self.hwid = ""
        self.is_initialized = False
        self.can_login = False
        self.can_register = False
        self.freemode = ""

    def WriteIntegrity(self):
        with open("integrity.txt", "w", errors="ignore") as m:
            m.write("{}".format(self.hash))

    def Get_Hash(self) -> str:
        hash = ""
        BUF_SIZE = 65536
        md5 = hashlib.md5()
        try:
            with open(sys.argv[0], "rb") as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    md5.update(data)
            return (md5.hexdigest())
        except Exception as e:
            return 
            (print("[!] Hash Calculating Failed!"), 
            time.sleep(3), 
            os._exit(0)
            )

    def Get_Hwid(self) -> str:
        return str(uuid.getnode())

    def Initialize(self, aid: str=None, secret: str=None, api_key: str=None, version: str=None):
        if aid is None or secret is None or api_key is None or version is None:
            return (
                print("[!] Invalid application information!"), 
                time.sleep(3), 
                os._exit(0)
                )
        self.aid += aid
        self.secret += secret
        self.api_key += api_key
        self.version += version
        self.hash +=  AuthGG.Get_Hash()
        self.hwid += AuthGG.Get_Hwid()
        try:
            with requests.Session() as sess:
                sess.proxies = None
                data = {
                    "type": "info",
                    "aid": self.aid,
                    "secret": self.secret,
                    "apikey": self.api_key
                }
                resp_1 = sess.post("https://api.auth.gg/v1/", data=data, proxies=None)
                with resp_1:
                    resp_json1 = json.loads(resp_1.text)
                    if not "{\"status\":\"" in resp_1.text:
                        if resp_json1["result"] == "failed":
                            return (
                                print("[!] {}!".format(resp_json1["message"])), 
                                time.sleep(3),
                                os._exit(0)
                                )
                    else:
                        if resp_json1["status"] == "Enabled":
                            self.is_initialized = True
                            self.freemode += resp_json1["freemode"]
                            if resp_json1["developermode"] == "Enabled":
                                self.can_login = True    
                                self.can_register = True
                                return (
                                    print("[!] Application is in Developer Mode, bypassing integrity and update check!"),
                                    print("[!] Your applications hash has been saved to integrity.txt, please refer to this when your application is ready for release!"),
                                    AuthGG.WriteIntegrity(),
                                    time.sleep(3)
                                    )
                            else:
                                if self.version != resp_json1["version"]:
                                    return (
                                        print("Update {} available, redirecting to update!".format(resp_json1["version"])),
                                        os.system("start {}".format(resp_json1["downloadlink"])),
                                        time.sleep(3),
                                        os._exit(0)
                                    )
                                if self.freemode == "Disabled":
                                    if resp_json1["hash"] != self.hash:
                                        return (
                                            print("[!] File has been tampered with, couldn't verify integrity!!"),
                                            time.sleep(3),
                                            os._exit(0)
                                        )
                                if resp_json1["login"] == "Enabled":
                                    self.can_login = True
                                if resp_json1["register"] == "Enabled":
                                    self.can_register = True
                        else:
                            return (
                                print("[!] Looks like this application is disabled, please try again later!"),
                                time.sleep(3),
                                os._exit(0)
                            )
        except:
            return (
                print("[!] Something went wrong, contact administrator!"), 
                time.sleep(3), 
                os._exit(0)
                )
    
    def Register(self, username: str=None, password: str=None, email: str=None, license: str=None):
        if not AuthGG.is_initialized:
            return (
                print("Please initialize your application first!"),
                time.sleep(3),
                os._exit(0)
            )
        if not AuthGG.can_register:
            return (
                print("Register is not enabled, please try again later!"),
                time.sleep(3),
                os._exit(0)
            )
        if username is None or password is None or email is None or license is None:
            return (
                print("Invalid registrar information!")
            )
        try:
            with requests.Session() as sess:
                sess.proxies = None
                data = {
                    "type": "register",
                    "hwid": self.hwid,
                    "email": email,
                    "license": license,
                    "password": password,
                    "username": username,
                    "aid": self.aid,
                    "secret": self.secret,
                    "apikey": self.api_key,
                    
                }
                resp_2 = sess.post("https://api.auth.gg/v1/", data=data, proxies=None)
                with resp_2:
                    resp_json2 = json.loads(resp_2.text)
                    if resp_json2["result"] == "success":
                        return True
                    elif resp_json2["result"] == "invalid_license":
                        return (
                            "[!] License does not exist!"
                            
                        )
                    elif resp_json2["result"] == "email_used":
                        return (
                           "[!] Email has already been used!"
                             
                        )
                    elif resp_json2["result"] == "invalid_username":
                        return (
                            "[!] You entered an invalid/used username!"
                            
                        )
                    else:
                        return (
                            "[!] Something went wrong, contact administrator!"
                            
                        )
                    
        except:
            return (
                print("[!] Something went wrong, contact administrator!"), 
                time.sleep(3), 
                os._exit(0)
                )

    def Login(self, username: str=None, password: str=None):
        if not AuthGG.is_initialized:
            return (
                print("[!] Please initialize your application first!"),
                time.sleep(3),
                os._exit(0)
            )
        if not AuthGG.can_login:
            return (
                print("[!] Register is not enabled, please try again later!"),
                time.sleep(3),
                os._exit(0)
            )
        if username is None or password is None:
            return (
                print("[!] Missing user login information!"),
                time.sleep(3),
                os._exit(0)
            )
        try:
            with requests.Session() as sess:
                sess.proxies = None
                data = {
                    "type": "login",
                    "hwid": self.hwid,
                    "password": password,
                    "username": username,
                    "aid": self.aid,
                    "secret": self.secret,
                    "apikey": self.api_key,
                    
                }
                resp_3 = sess.post("https://api.auth.gg/v1/", data=data, proxies=None)
                with resp_3:
                    resp_json3 = json.loads(resp_3.text)
                    if resp_json3["result"] == "success":
                        return True
                    elif  resp_json3["result"] == "invalid_details":
                        return "[!] Sorry, your username/password does not match!"

                    elif  resp_json3["result"] == "time_expired":
                        return "[!] Your subscription has expired!"

                    elif  resp_json3["result"] == "hwid_updated":
                        return "[!] New machine has been binded, re-open the application!"

                    elif  resp_json3["result"] == "invalid_hwid":
                        return "[!] This user is binded to another computer, please contact support!"

                    else:
                        return "[!] Something went wrong, contact administrator!"

        except:
            return "[!] Something went wrong, contact administrator!"


    def AIOLogin(self, key):
        if not AuthGG.is_initialized:
            return "[!] Please initialize your application first!"

        try:
            with requests.Session() as sess:
                sess.proxies = None
                data = {
                    "type": "login",
                    "hwid": self.hwid,
                    "password": key,
                    "username": key,
                    "aid": self.aid,
                    "secret": self.secret,
                    "apikey": self.api_key,
                    
                }
                resp_4 = sess.post("https://api.auth.gg/v1/", data=data, proxies=None)
                with resp_4:
                    resp_json4 = json.loads(resp_4.text)
                    if resp_json4["result"] == "success":
                        return True
                    elif  resp_json4["result"] == "invalid_details":
                        return False
                    elif  resp_json4["result"] == "time_expired":
                        return (
                            "[!] Your subscription has expired!"
                             
                        )
                    elif  resp_json4["result"] == "hwid_updated":
                        return (
                            "[!] New machine has been binded, re-open the application!"
                             
                        )
                    elif  resp_json4["result"] == "invalid_hwid":
                        return (
                            "[!] This user is binded to another computer, please contact support!"
                             
                        )
                    else:
                        return (
                            "[!] Something went wrong, contact administrator!"
                            
                        )
                    
        except:
            return (
                print("[!] Something went wrong, contact administrator!"), 
                time.sleep(3), 
                os._exit(0)
                )
    def AIORegister(self, key):
        if not AuthGG.is_initialized:
            return (
                print("[!] Please initialize your application first!"),
                time.sleep(3),
                os._exit(0)
            )
        try:
            with requests.Session() as sess:
                sess.proxies = None
                data = {
                    "type": "register",
                    "hwid": self.hwid,
                    "email": key,
                    "license": key,
                    "password": key,
                    "username": key,
                    "aid": self.aid,
                    "secret": self.secret,
                    "apikey": self.api_key,
                    
                }
                resp_5 = sess.post("https://api.auth.gg/v1/", data=data, proxies=None)
                with resp_5:
                    resp_json5 = json.loads(resp_5.text)
                    if resp_json5["result"] == "success":
                        return True
                    else:
                        return False
        except:
            return (
                print("[!] Something went wrong, contact administrator!"), 
                time.sleep(3), 
                os._exit(0)
                )
    def AIO(self, key: str=None):
        if not AuthGG.is_initialized:
            return (
                print("[!] Please initialize your application first!"),
                time.sleep(3),
                os._exit(0)
            )
        if key is None:
            return (
                print("[!] Invalid Key!"),
                time.sleep(3),
                os._exit(0)
            )
        if AuthGG.AIOLogin(key):
            return True
        else:
            if AuthGG.AIORegister(key):
                return True
            else:
                return False

    def ExtendSubscription(self, username, password, license):
        if not AuthGG.is_initialized:
            return (
                print("[!] Please initialize your application first!"),
                time.sleep(3),
                os._exit(0)
            )
        if username is None or password is None or license is None:
            return (
                print("[!] Invalid informations!"),
                time.sleep(3),
                os._exit(0)
            )
        try:
            with requests.Session() as sess:
                sess.proxies = None
                data = {
                    "type": "extend",
                    "license": license,
                    "password": password,
                    "username": username,
                    "aid": self.aid,
                    "secret": self.secret,
                    "apikey": self.api_key,
                    
                }
                resp_6 = sess.post("https://api.auth.gg/v1/", data=data, proxies=None)
                with resp_6:
                    resp_json6 = json.loads(resp_6.text)
                    if resp_json6["result"] == "success":
                        return True
                    elif resp_json6["result"] == "invalid_license":
                        return (
                            "[!] License does not exist!"
                            
                        )
                    elif resp_json6["result"] == "invalid_details":
                        return (
                            "[!] Your user details are invalid!"
                            
                        )
                    else:
                        return (
                            "[!] Something went wrong, contact administrator!"
                            
                            )
        except:
            return (
                print("[!] Something went wrong, contact administrator!"), 
                time.sleep(3), 
                os._exit(0)
                )

AuthGG = AuthGG()
