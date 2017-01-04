# -*- coding: utf-8 -*-

from remote import remotewrite
from Asterisk.Manager import Manager

class Pbx(object):

    def __init__(self,pbxconfig):
        self._sshconfig = pbxconfig['scp']
        self._pbx = Manager(**pbxconfig['pbx'])

    def sendConfNow(self, conf):
        remotewrite(
            user = self._sshconfig['username'],
            host = self._sshconfig['pbxhost'],
            filename = self._sshconfig['path'],
            content = conf
            )
        self._pbx.Command('reload')

    def receiveConf(self):
        return self._pbx.Queues()

    def _pause(self, day, turn , sip, paused):
        queue="entrada_cua_{day}_{turn}".format(day=day,turn=turn)
        self._pbx.QueuePause(queue,"SIP/{}".format(sip),paused)

    def pause(self, day, turn, sip):
        self._pause(day,turn,sip,True)

    def resume(self, day, turn, sip):
        self._pause(day,turn,sip,False)

    def parsePause(self, diff):
        for day in diff.keys():
            for turn in diff[day]:
                for ext in diff[day][turn]:
                    if (diff[day][turn][ext]
                        == "added"):
                        self.pause(day,
                            turn,
                            ext)
                    elif (diff[day][turn][name]
                        == "resumed"):
                        self.resume(day,
                            turn,
                            ext)


# vim: ts=4 sw=4 et
