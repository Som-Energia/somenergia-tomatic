# -*- coding: utf-8 -*-

from remote import remotewrite
from Asterisk.Manager import Manager
from htmlgen import HtmlGen

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

class HtmlGenFromAsterisk(HtmlGen):
    # Only linear queues are implemented at the moment
    def __init__(self, yaml, asteriskConf):
        return
        asteriskQueues = {
            (k.split('_')[-2], 
                int(k.split('_')[-1])
            ): [ (ext,asteriskConf[k]
                    ['members'][ext]
                    ['Penalty']
                 )  for ext 
                    in asteriskConf[k][
                        'members'].keys()
               ]
            for k in asteriskConf.keys() 
                if 'dinamica' not in k
        }
        asteriskPaused = {
            (k.split('_')[-2], 
                int(k.split('_')[-1])
            ): [asterisk_sip for asterisk_sip in
                asteriskConf[k]['members'].keys()
                if asteriskConf[k]['members'][asterisk_sip]['Paused']=='1']
            for k in asteriskConf.keys()
                if 'dinamica' not in k
        }
        asteriskDynamic = [ext
            for ext 
            in asteriskConf['entrada_dinamica']['members'].keys()
        ] if 'entrada_dinamica' in asteriskConf else []

        extensions_inv = { extension : name for name, extension in yaml.extensions.items()}
        solution_asterisk = {}
        solution_paused = {}
        for q in asteriskQueues:
            asteriskQueue = [
                extensions_inv[
                    int(ext_sip.split('/')[1])]
                for ext_sip,_ in sorted(
                    asteriskQueues[q],
                    key=lambda ext:ext[1])]
            for nTel, name in enumerate(asteriskQueue):
                solution_asterisk[(q[0],q[1],nTel)]=name
        for q in asteriskPaused:
            asteriskPausedSingle = [extensions_inv[int(ext_sip.split('/')[1])] 
                for ext_sip in asteriskPaused[q]]
            for nTel, name in enumerate(asteriskPausedSingle):
                solution_paused[(q[0],q[1],nTel)]=name
        tt_yaml = yaml.timetable
        paused = ns()
        tt_asterisk = ns()
        for day in { k[0] for k in solution_asterisk}:
            tt_asterisk[day] = ns()
            paused[day] = ns()
            for time in {k[1] for k in solution_asterisk if k[0]==day}:
                tt_asterisk[day][time] = []
                paused[day][time] = []
                for tel in {k[2] for k in solution_asterisk if k[0]==day and k[1]==time}:
                    tt_asterisk[day][time].append(
                        solution_asterisk.get(
                            (day,
                            time,
                            tel),'Error')
                    )
                    if (day,time,tel) in solution_paused:
                        paused[day][time].append(
                            solution_paused[
                                (day,
                                time,
                                tel)])
        dynamic = [
            extensions_inv[
                int(ext_sip.split('/')[1])]
            for ext_sip 
            in asteriskDynamic
        ]
        y = ns()
        y.dynamic = dynamic
        y.timetable = tt_asterisk
        y.paused = paused
        y.names = yaml.get('names',{})
        y.hours = yaml.hours
        y.turns = yaml.turns
        y.colors = yaml.get('colors',{})
        y.extensions = yaml.extensions
        y.week = yaml.week
        self.yaml=y


# vim: ts=4 sw=4 et
