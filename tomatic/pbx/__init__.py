from ..pbxqueue import PbxQueue
import dbconfig

pbxtypes = [
    'fake',
    'dbasterisk',
    'areavoip',
    'irontec',
]

def pbxcreate(pbxtype):
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

def defaultQueue(pbxtype):
    return dict(
        fake = AsteriskFake.defaultQueue,
        dbasterisk = DbAsterisk.defaultQueue,
        areavoip = AreaVoip.defaultQueue,
        irontec = Irontec.defaultQueue,
    ).get(pbxtype, None)

def pbxqueue(pbxtype=None, queue=None):
    if pbxtype:
        pbxqueue.cache = PbxQueue(
            pbxcreate(pbxtype),
            queue or defaultQueue(pbxtype),
        )
    if not hasattr(pbxqueue, 'cache'):
        pbxqueue.cache = pbxtype('fake', queue)

    return pbxqueue.cache
    







