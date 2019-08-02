# -*- coding: utf-8 -*-

from paramiko import SSHClient,AutoAddPolicy

class Remote(object):
    def __init__(self, username, host):
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(host, username=username)

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

def remoteread(user, host, filename):
    with Remote(user, host) as remote:
        return remote.read(filename)


def remotewrite(user, host, filename, content):
    with Remote(user, host) as remote:
        remote.write(filename, content)

def remoterun(user, host, command):
    with Remote(user, host) as remote:
        return remote.run(command)


# vim: ts=4 sw=4 et
