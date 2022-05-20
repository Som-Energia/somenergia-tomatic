from .pbxqueue import PbxQueue

# TODO: Make this dynamic by inspecting the pbx module

pbxtypes = [
    'fake',
    'dbasterisk',
    'areavoip',
    'irontec',
]

def pbxcreate(pbxtype):
    import dbconfig
    pbxtype = (
        pbxtype or (
        dbconfig.tomatic.get('pbx', None) or (
        'irontec'
    )))

    if pbxtype == 'fake':
        from .asteriskfake import AsteriskFake
        return AsteriskFake()

    if pbxtype == 'dbasterisk':
        from .dbasterisk import DbAsterisk
        return DbAsterisk()

    if pbxtype == 'areavoip':
        from .pbxareavoip import AreaVoip
        return AreaVoip()

    if pbxtype == 'irontec':
        from .pbxirontec import Irontec
        return Irontec()

    raise Exception(f"No such pbx backend {pbxtype}")

def pbxqueue(pbxtype=None, queue=None):
    if pbxtype or not hasattr(pbxqueue, 'cache'):
        pbxqueue.cache = PbxQueue(
            pbxcreate(pbxtype),
            queue,
        )

    return pbxqueue.cache
    







