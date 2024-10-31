from yamlns import ns
import os

from .dbconfig import dbconfig

def secrets(key='', default=Ellipsis):
    keyparts = key.split('.')
    envkey = key.replace('.','_').upper()
    if envkey in os.environ:
        return os.environ[envkey]
    configuration = dbconfig or ns(tomatic=ns())
    if not key:
        return configuration
    for part in keyparts[:-1]:
        configuration = configuration.get(part, ns())
    if default is Ellipsis and keyparts[-1] not in configuration:
        raise KeyError(key)
    return configuration.get(keyparts[-1], default)


def params():
    return ns.load('config.yaml')

