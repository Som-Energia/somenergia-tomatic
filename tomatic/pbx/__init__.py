from ..pbxqueue import PbxQueue

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
        'areavoip'
    )))

    if pbxtype == 'fake':
        from .asteriskfake import AsteriskFake
        return AsteriskFake()

    if pbxtype == 'dbasterisk':
        from .dbasterisk import DbAsterisk
        return DbAsterisk(
            *dbconfig.tomatic.dbasterisk.args,
            **dbconfig.tomatic.dbasterisk.kwds,
        )

    if pbxtype == 'areavoip':
        from .pbxareavoip import AreaVoip
        return AreaVoip()

    if pbxtype == 'irontec':
        from .pbxirontec import Irontec
        return Irontec()

    raise Exception(f"No such pbx backend {pbxtype}")

def pbxqueue(pbxtype=None, queue=None):
    if pbxtype:
        pbxqueue.cache = PbxQueue(
            pbxcreate(pbxtype),
            queue,
        )
    if not hasattr(pbxqueue, 'cache'):
        pbxqueue.cache = pbxqueue('fake', queue)

    return pbxqueue.cache
    







