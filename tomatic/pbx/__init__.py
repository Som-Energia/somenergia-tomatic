from ..pbxqueue import PbxQueue
import dbconfig

def pbxcreate(pbxtype):

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
        fake = 'somenergia',
        dbasterisk = 'somenergia',
        areavoip = dbconfig.tomatic.areavoip.queue,
        irontec = dbconfig.tomatic.irontec.queue,
    ).get(pbxtype, 'somenergia')

def pbxqueue(pbxtype=None, queue=None):
    if pbxtype:
        pbxqueue.cache = PbxQueue(
            pbxcreate(pbxtype),
            queue or defaultQueue(pbxtype),
        )
    if not hasattr(pbxqueue, 'cache'):
        pbxqueue.cache = pbxtype('fake', queue)

    return pbxqueue.cache
    







