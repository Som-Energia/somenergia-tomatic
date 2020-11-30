from yamlns import namespace as ns
from pathlib2 import Path

srcpath = Path(__file__).absolute().parent

def persons(path=None):
    """
    Cached load of personal information.
    First pathless call loads from default path.
    Explicit path reloads.
    Further pathless calls, just uses cache.
    If modifications are detected for the path, it is reloaded.
    False as path resets the cache.
    """
    if path is False:
        if hasattr(persons,'cache'):
            del persons.cache
        return
    if not hasattr(persons,'cache'):
        persons.path = Path(path) if path else (srcpath / '../persons.yaml').resolve()
        persons.mtime = persons.path.stat().st_mtime
        persons.cache = ns.load(persons.path)
        return persons.cache

    if path:
        persons.path = Path(path)
        persons.mtime = persons.path.stat().st_mtime
        persons.cache = ns.load(persons.path)
        return persons.cache

    if persons.mtime != persons.path.stat().st_mtime:
        persons.mtime = persons.path.stat().st_mtime
        persons.cache = ns.load(persons.path)

    return persons.cache

def byExtension(extension):
    """
    Returns the person key having the extension
    """
    keytoext = dict(
        (e,n) for n,e in persons().extensions.items()
    )
    return keytoext.get(extension,extension)

def name(key):
    """
    Returns the person full name having the person key
    """
    return persons().get('names',{}).get(key,key.title())

def nameByExtension(extension):
    return name(byExtension(extension))




# vim: et ts=4 sw=4
