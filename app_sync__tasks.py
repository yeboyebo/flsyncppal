from AQNEXT.celery import app
from YBLEGACY import qsatype
from YBUTILS import globalValues
from YBUTILS import DbRouter

from models.flsyncppal import flsyncppal_def as syncppal

globalValues.registrarmodulos()
cdDef = 10


@app.task
def sample(r):
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = sampleScript.iface.sampleCall() or cdDef
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", "sampleprocess")
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = 'sampleprocess'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        sampleScript.apply_async((r,), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", "sampleprocess")
