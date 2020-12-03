from yamlns import namespace as ns
from pathlib2 import Path

srcpath = Path(__file__).absolute().parent

def _load(path):
    loaded = ns.load(path)
    for key in (
        'names',
        'extensions',
        'tables',
        'colors',
        'emails',
        'groups',
    ):
        loaded.setdefault(key, ns())
    return loaded

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
        persons.cache = _load(persons.path)
        return persons.cache

    if path:
        persons.path = Path(path)
        persons.mtime = persons.path.stat().st_mtime
        persons.cache = _load(persons.path)
        return persons.cache

    if persons.mtime != persons.path.stat().st_mtime:
        persons.mtime = persons.path.stat().st_mtime
        persons.cache = _load(persons.path)

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

def extension(key):
    return persons().get('extensions',{}).get(key)

def update(key, data):
    result = persons()
    if 'name' in data:
        result.names[key] = data.name
    if 'extension' in data:
        result.extensions[key] = data.extension
    if 'table' in data:
        result.tables[key] = data.table
    if 'color' in data:
        result.colors[key] = data.color
    if 'email' in data:
        result.emails[key] = data.email
    if 'groups' in data:
        for group in data.groups:
            result.groups.setdefault(group, []).append(key)
        for group, components in result.groups.items():
            if group not in data.groups:
                result.groups[group].remove(key)
                if not result.groups[group]:
                    del result.groups[group]



# vim: et ts=4 sw=4
