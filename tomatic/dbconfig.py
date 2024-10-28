
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
        e.strerror = "Unable to load configuration file (%s)" % e.strerror
        raise
    return ns((
        (key, val)
        for key, val in config_module.__dict__.items()
        if not key.startswith("_")
    ))

globals().update(_init())

def config(key='', default=Ellipsis):
    keyparts = key.split('.')
    envkey = key.replace('.','_').upper()
    if envkey in os.environ:
        return os.environ[envkey]
    try:
        configuration = ns(globals())
    except ImportError:
        configuration = ns(tomatic=ns())
    if not key:
        return configuration
    for part in keyparts[:-1]:
        configuration = configuration.get(part, ns())
    if default is Ellipsis and keyparts[-1] not in configuration:
        raise KeyError(key)
    return configuration.get(keyparts[-1], default)

