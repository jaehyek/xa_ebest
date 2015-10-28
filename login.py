import win32com.client
import pythoncom

class XASessionEvents:
    logInState = 0
    def OnLogin(self, code, msg):
        print("OnLogin method is called")
        print(str(code))
        print(str(msg))
        if str(code) == '0000':
            XASessionEvents.logInState = 1

    def OnLogout(self):
        print("OnLogout method is called")

    def OnDisconnect(self):
        print("OnDisconnect method is called")


def login():
    server_addr = "hts.ebestsec.co.kr"
    server_port = 20001
    server_type = 0
    user_id = "testtest"
    user_pass = "password"
    user_certificate_pass = "passwordpass"

    #--------------------------------------------------------------------------
    # Login Session
    #--------------------------------------------------------------------------
    inXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
    inXASession.ConnectServer(server_addr, server_port)
    inXASession.Login(user_id, user_pass, user_certificate_pass, server_type, 0)

    while XASessionEvents.logInState == 0:
        pythoncom.PumpWaitingMessages()

    if XASessionEvents.logInState == 1 :
        return True
    else:
        return False


