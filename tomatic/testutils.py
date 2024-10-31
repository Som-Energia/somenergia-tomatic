import os
from contextlib import contextmanager
from yamlns.testutils import assertNsEqual
from yamlns import ns
from pydantic import __version__ as pydantic_version
from .config import secrets

pydantic_minor_version = '.'.join(pydantic_version.split('.')[:2])

personaldata = secrets('personaldata')
#try:
#    personaldata = ns.load('testdata/personaldata.yaml')
#except:
#    personaldata = None

@contextmanager
def environ(var, value):
    """
    Context handler to modify environment variables
    while inside the context and restore them on exit.
    Use None as value to unset.

    >>> import os
    >>> os.environ['DEFINED_VAR'] = "Previous value"
    
    Restores old values of defined variables
    >>> with environ('DEFINED_VAR', 'New value'):
    ...    os.environ.get('DEFINED_VAR')
    'New value'
    >>> os.environ.get('DEFINED_VAR')
    'Previous value'

    Clears variable if set to None
    >>> with environ('DEFINED_VAR', None):
    ...    'DEFINED_VAR' in os.environ
    False
    >>> 'DEFINED_VAR' in os.environ
    True

    Restores indefinition on undefined variables
    >>> with environ('UNDEFINED_VAR', 'value'):
    ...    os.environ.get('UNDEFINED_VAR')
    'value'
    >>> os.environ.get('UNDEFINED_VAR') # Nothing

    Behave on exception
    >>> try:
    ...     with environ('DEFINED_VAR', 'New'):
    ...         raise Exception("Error")
    ... except: pass
    >>> os.environ.get('DEFINED_VAR')
    'Previous value'
    """
    def set(value):
        if value is not None:
            os.environ[var]=value
        elif var in os.environ:
            del os.environ[var]
    
    oldvalue = os.environ.get(var)
    set(value)
    try:
        yield value
    finally:
        set(oldvalue)


def assertResponseEqual(self, response, expected, status=200, content_type='application/json'):
    if type(expected) == str:
        data = ns.loads(expected)

    content = ns(text=response.text)
    try: content = ns(yaml=ns.loads(content.text))
    except: pass

    assertNsEqual(
        self,
        ns(
            content,
            status=response.status_code,
            content_type=response.headers['Content-Type'],
        ),
        ns(
            yaml=data,
            status=status,
            content_type=content_type,
        ),
    )

def safe_response_get(r, key, fallback='NOT_FOUND'):
    """
    To be used when an attribute in a response to back2back is variable,
    to use the actual result value in the expectation, but to
    obtain it in a safe way, so that, when the attribute is missing
    or even when the response is not a valid json, we get the fallback.

    Deep attribute access can be expressed with dots: level.level.key

    >>> from httpx import Response
    >>> r = Response(text='{"key1": "value1", "level1": {"level2": {"key2": "value2"}}}', status_code=200)

    >>> # bad json
    >>> badjson = Response(text='bad json content', status_code=200)
    >>> safe_response_get(badjson, 'key1')
    'NOT_FOUND'

    >>> # top level key
    >>> safe_response_get(r, 'key1') # top level key
    'value1'

    >>> # missing top level key
    >>> safe_response_get(r, 'missing')
    'NOT_FOUND'

    >>> # custom fallback
    >>> safe_response_get(r, 'key2', 'CUSTOM_FALLBACK')
    'CUSTOM_FALLBACK'

    >>> # deep value
    >>> safe_response_get(r, 'level1.level2.key2')
    'value2'

    >>> # non leaf value
    >>> safe_response_get(r, 'level1.level2')
    {'key2': 'value2'}

    >>> # bad intermediate step
    >>> safe_response_get(r, 'level1.bad.key2')
    'NOT_FOUND'
    """
    try:
        value = r.json()
    except Exception:
        return fallback
    for level in key.split('.'):
        if not isinstance(value, dict):
            return fallback
        value = value.get(level, fallback)
    return value
