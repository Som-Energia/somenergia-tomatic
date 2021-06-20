from consolemsg import step

class BackChannel(object):

    def __init__(self):
        self._sessions = {}
        self._users = {}
        self._senders = {}

    def addSession(self, sessionId, session, sender):
        step("WS {} addSession", sessionId)
        self._sessions[sessionId] = session
        self._senders[sessionId] = sender
        self._users[sessionId] = None

    def receiveMessage(self, sessionId, message):
        step("WS {} receiveMessage {}", sessionId, message)
        args = message.split(":")
        type_of_message = args[0]
        if type_of_message == "IDEN":
            user = args[1]
            self.onLoggedIn(sessionId, user)
        else:
            error("Type of message not recognized.")

    def onLoggedIn(self, sessionId, user):
        step("WS {} onLoggedIn {}",sessionId, user)
        olduser = self._users.get(sessionId)
        self._users[sessionId] = user

    def onDisconnect(self, sessionId):
        del self._sessions[sessionId]
        del self._senders[sessionId]
        del self._users[sessionId]

    def notifyIncommingCall(self, user, callerid, time):
        return [
            self._senders[sessionId](f"PHONE:{callerid}:{time}")
            for sessionId, sessionuser in self._users.items()
            if user == sessionuser
        ]

    def notifyCallLogChanged(self, user):
        if user is None: return
        return [
            self._senders[sessionId](f"REFRESH:whatever")
            for sessionId, sessionuser in self._users.items()
            if user == sessionuser
        ]



