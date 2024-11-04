# This file is a temporary hack to load dbconfig
# regardles of the package being installed.

def _init():
    from pathlib import Path
    import types
    from yamlns import ns
    filename =  'dbconfig.py'
    config_file = Path() / filename
    config_module = types.ModuleType('config')
    config_module.__file__ = str(config_file)
    try:
        with config_file.open(mode="rb") as config_file:
            exec(compile(config_file.read(), filename, "exec"), config_module.__dict__)
    except IOError as e:
        return ns()
    return ns((
        (key, val)
        for key, val in config_module.__dict__.items()
        if not key.startswith("_")
    ))

dbconfig = _init()

