from consolemsg import step
import json

class BackChannel(object):
    """
    Encapsulates server initiated communications (websockets)
    """

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
            self.login(sessionId, user)
        else:
            error("Type of message not recognized.")

    def broadCastUserSessions(self, user, type, **kwds):
        """
        Sends the same message to all sessions of the same user.
        """
        message = json.dumps(dict(
            type=type,
            **kwds
        ))
        return [
            self._senders[sessionId](message)
            for sessionId, sessionuser in self._users.items()
            if sessionuser == user
        ]

    def login(self, sessionId, user):
        olduser = self._users.get(sessionId)
        step("WS {} login {} was {}", sessionId, user, olduser)
        self._users[sessionId] = user

    def onDisconnect(self, sessionId):
        step("WS {} disconnect {}", sessionId, self._users.get(sessionId))
        del self._sessions[sessionId]
        del self._senders[sessionId]
        del self._users[sessionId]

    def notifyIncommingCall(self, user, phone, time, call_id):
        return self.broadCastUserSessions(user, "PHONE",
            call_id=call_id,
            phone=phone,
            date=time,
        )

    def notifyCallLogChanged(self, user):
        if user is None: return []
        return self.broadCastUserSessions(user, "REFRESH")



