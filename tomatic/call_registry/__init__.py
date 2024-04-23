from . import dummy
from . import odoo
from pathlib import Path
import os
import dbconfig


# TODO: Use dbconfig to choose type and parameters.
def CallRegistry():
    # TODO: take it from dbconfig if not set in environment
    default_backend = 'dummy'
    config_backend = dbconfig.tomatic.get('callregistry')
    env_backend = os.environ.get('TOMATIC_CALL_REGISTRY')
    backend = env_backend or config_backend or default_backend

    if backend == 'dummy':
        data_path = os.environ.get('TOMATIC_DATA_PATH', 'data')
        return dummy.CallRegistry(data_path)

    if backend == 'odoo':
        return odoo.CallRegistry()

    # TODO: Proper exception
    raise Exception(f"Unsoported Call Registry backend '{backend}'")


