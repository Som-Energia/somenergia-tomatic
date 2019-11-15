# -*- coding: utf-8 -*-

from paramiko import SSHClient,AutoAddPolicy

class Remote(object):
    def __init__(self, username, host, **kwds):
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(host, username=username, **kwds)

    def __enter__(self):
        return self

    def __exit__(self, *excl):
        return self.ssh.__exit__(*excl)

    def read(self, filename):
        sftp = self.ssh.open_sftp()
        with sftp.open(filename, 'r') as f:
            return f.read()

    def write(self, filename, content):
        sftp = self.ssh.open_sftp()
        with sftp.open(filename, 'w') as f:
            f.write(content)

    def run(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdin.close()
        return stdout.read()

def remoteread(username, host, filename, **kwds):
    with Remote(username, host, **kwds) as remote:
        return remote.read(filename)


def remotewrite(username, host, filename, content, **kwds):
    with Remote(username, host, **kwds) as remote:
        remote.write(filename, content)

def remoterun(username, host, command, **kwds):
    with Remote(username, host, **kwds) as remote:
        return remote.run(command)


# vim: ts=4 sw=4 et
