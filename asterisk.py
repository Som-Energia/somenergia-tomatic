# -*- coding: utf-8 -*-
from Asterisk.Manager import Manager
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from tempfile import NamedTemporaryFile as mktmpfile

class Pbx(object):

    def __init__(self,pbx,sshconfig):
        #self._pbx = Manager(**config['pbx'])
        self._pbx = pbx
        #self._sshconfig = config['scp']
        self._sshconfig = sshconfig

    def sendConfNow(self, conf):
        with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(self._sshconfig['pbxhost'],
                username=self._sshconfig['username'],
                password=self._sshconfig['password'])
            scp = SCPClient(ssh.get_transport())
            with mktmpfile(delete=False) as f:
                f.write(conf)
                tmpConfFile = f.name
            scp.put(tmpConfFile,self._sshconfig['path'])
        self._pbx.Command('reload')
