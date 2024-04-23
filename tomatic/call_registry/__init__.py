import os
from . import dummy
from . import odoo


def configured_backend():
    backend = os.environ.get('TOMATIC_CALL_REGISTRY')
    if backend: return backend

    import dbconfig
    backend = dbconfig.tomatic.get('callregistry')
    if backend: return backend

    default_backend = 'dummy'
    return default_backend


# TODO: Use dbconfig to choose type and parameters.
def CallRegistry():
    backend = configured_backend()

    if backend == 'dummy':
        data_path = os.environ.get('TOMATIC_DATA_PATH', 'data')
        return dummy.CallRegistry(data_path)

    if backend == 'odoo':
        return odoo.CallRegistry()

    # TODO: Proper exception
    raise Exception(f"Unsoported Call Registry backend '{backend}'")


