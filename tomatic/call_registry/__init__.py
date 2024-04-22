from . import dummy
from pathlib import Path
import os


# TODO: Use dbconfig to choose type and parameters.
def CallRegistry():
    # TODO: take it from dbconfig if not set in environment
    backend = os.environ.get('TOMATIC_CALL_REGISTRY', 'dummy')

    if backend == 'dummy':
        data_path = os.environ.get('TOMATIC_DATA_PATH', None)
        return dummy.CallRegistry(data_path)

    # TODO: Proper exception
    raise Exception(f"Unsoported Call Registry backend '{backend}'")


