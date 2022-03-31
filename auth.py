import requests; from typing import Dict
constants: Dict = {
    "secrets": {"aid": "AID","apikey": "APIKEY","secret": "SECRET"},
    "routes": {
        "api": "https://api.auth.gg/v1/",
        "headers": {"Content-Type": "application/x-www-form-urlencoded","Host": "api.auth.gg"}
    }
}
responses: Dict  = {
    "login": {"success": "Successful!","invalid_details": "Invalid login.","invalid_hwid": "Invalid hwid.","hwid_updated": "Hwid updated.","subscription_expired": "Subscribtion expired."},
    "register": {"success": "Successful!","invalid_license": "Invalid license.","email_used": "Email has been used already.","invalid_username": "Username has been used already."},
    "extend": {"success": "Successful!","invalid_license": "Invalid license.","invalid_details": "Invalid login."},
    "forgotpw": {"success": "Successful!","failed": "Failed to send password reset request."},
    "changepw": {"successful": "Successful!","invalid_login": "Invalid login."}
}
needs: Dict = {
    "login": ["username", "password", "hwid"],
    "register": ["username", "password", "hwid", "license", "email"],
    "extend": ["username", "password", "license"],
    "forgotpw": ["username"],
    "changepw": ["username", "password", "new_password"]
}

class AuthGG_api:
    def __init__(aid: str, apikey: str,
                secret: str):
                    constants["secrets"]["aid"] = aid
                    constants["secrets"]["apikey"] = apikey
                    constants["secrets"]["secret"] = secret
    def Action(_type: str, username: str=None,
                email: str=None, password: str=None,
                new_password: str=None, hwid: str=None,
                license: str=None) -> str:
            vars: dict = locals()
            payload: str = f"type={_type}&aid={constants['secrets']['aid']}&apikey={constants['secrets']['apikey']}&secret={constants['secrets']['secret']}"
            for each in vars:
                if vars[each] is not None and each != '_type': payload+=f"&{each}={vars[each]}"
            for each in needs[_type]:
                if each not in payload: return "Missing Args"
            session = requests.Session()
            session.headers= constants["routes"]["headers"]
            requestText: str = session.post(constants["routes"]["api"], data=payload).text
            for each in responses[_type]:
                if each in requestText: return responses[_type][each]
            return "Server error."