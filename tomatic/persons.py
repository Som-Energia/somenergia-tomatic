from yamlns import namespace as ns
from pathlib import Path

srcpath = Path(__file__).absolute().parent

def _load(path=None):
    loaded = ns.load(path) if path else ns()
    for key in (
        'names',
        'extensions',
        'tables',
        'colors',
        'emails',
        'groups',
        'erpusers',
        'idealloads',
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
        # False means clear cache
        if hasattr(persons,'cache'):
            del persons.cache
        return

    def reload():
        if not persons.path.exists():
            persons.mtime = 0
            persons.cache = _load()
            return persons.cache
        persons.mtime = persons.path.stat().st_mtime
        persons.cache = _load(persons.path)
        return persons.cache


    if not hasattr(persons,'cache'):
        persons.path = Path(path) if path else (srcpath / '../persons.yaml').resolve()
        return reload()

    if path:
        persons.path = Path(path)
        return reload()

    if not persons.path.exists():
        return reload()

    if persons.mtime != persons.path.stat().st_mtime:
        return reload()

    return persons.cache

def byExtension(extension):
    """
    Returns the person key having the extension or the extension
    """
    keytoext = dict(
        (e,n) for n,e in persons().extensions.items()
    )
    return keytoext.get(extension, extension)

def byEmail(email):
    """
    Returns the person key having the email or none
    """
    keytoext = dict(
        (e,n) for n,e in persons().emails.items()
    )
    return keytoext.get(email, None)

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
    if 'erpuser' in data:
        result.erpusers[key] = data.erpuser
    if 'idealload' in data.keys():
        idealloads = result.setdefault('idealloads', {})
        if data.get('idealload') is None:
            if key in idealloads:
                del idealloads[key]
        else:
            idealloads[key] = int(data.idealload)
    if 'groups' in data:
        for group in data.groups:
            members = result.groups.setdefault(group, [])
            if key not in members:
                members.append(key)
        for group, components in result.groups.items():
            if group in data.groups:
                continue
            if key in result.groups[group]:
                result.groups[group].remove(key)
        result.groups = {
            group: members
            for group, members in result.groups.items()
            if members
        }
    result.dump(persons.path)

def delete(key):
    result = persons()
    'Deletes key from person'
    simpleAttributes = [
        'names',
        'extensions',
        'tables',
        'colors',
        'emails',
        'erpusers',
        'idealloads',
    ]
    for attribute in simpleAttributes:
        if key in result[attribute]:
            del result[attribute][key]
    groups = list(result.groups)
    for group in groups:
        if key not in result.groups[group]: continue
        result.groups[group].remove(key)
        if result.groups[group]: continue
        del result.groups[group]

    result.dump(persons.path)

# vim: et ts=4 sw=4
