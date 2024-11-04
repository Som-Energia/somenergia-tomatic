import os
from . import dummy
from . import odoo
from ..config import secrets

available_backends = [
    'dummy',
    'odoo',
]

def configured_backend():
    # TODO: Deprecate TOMATIC_CALL_REGISTRY since secrets
    # already enables TOMATIC_CALLREGISTRY from dbconfig
    backend = os.environ.get('TOMATIC_CALL_REGISTRY')
    if backend: return backend

    return secrets('tomatic.callregistry', 'dummy')


def CallRegistry():
    backend = configured_backend()

    if backend == 'dummy':
        data_path = os.environ.get('TOMATIC_DATA_PATH', 'data')
        return dummy.CallRegistry(data_path)

    if backend == 'odoo':
        return odoo.CallRegistry()

    # TODO: Proper exception
    raise Exception(f"Unsoported Call Registry backend '{backend}'")


