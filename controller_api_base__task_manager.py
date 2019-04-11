from AQNEXT.celery import app

from YBLEGACY import qsatype
from YBUTILS import globalValues
from YBUTILS import DbRouter

from models.flsyncppal import flsyncppal_def as syncppal


class TaskManager():

    sync_object_dict = None

    def __init__(self, sync_object_dict):
        self.sync_object_dict = sync_object_dict

        globalValues.registrarmodulos()
        self.register_tasks()

    def register_tasks(self):
        for sync_object_name in self.sync_object_dict:
            @app.task(name=sync_object_name)
            def decorated(*args):
                self.sync_task(*args)

    def sync_object_factory(self, sync_object_name):
        if sync_object_name not in self.sync_object_dict:
            return None

        sync_object_dict = self.sync_object_dict[sync_object_name]
        return sync_object_dict["sync_object"], sync_object_dict["driver"]

    def task_executer(self, request, sync_object_name, params={}, countdown=0):
        app.tasks[sync_object_name].apply_async((request, sync_object_name, params,), countdown=countdown)

    def sync_task(self, request, sync_object_name, params={}):
        DbRouter.ThreadLocalMiddleware.process_request_celery(None, request)

        sync_object_class, sync_driver = self.sync_object_factory(sync_object_name)
        sync_object = sync_object_class(sync_driver(), params)

        activo = self.get_activo(sync_object.process_name)
        if activo and ("continuous" not in params or not params["continuous"]):
            syncppal.iface.log("Info. El proceso ya se está ejecutando en segundo plano", sync_object.process_name)
            return

        countdown_time = sync_object.start()

        if "continuous" not in params or not params["continuous"]:
            return

        activo = self.get_activo(sync_object.process_name)
        if activo:
            if "first" in params and params["first"]:
                params["first"] = False

            self.task_executer(request, sync_object_name, params=params, countdown=countdown_time)
        else:
            syncppal.iface.log("Info. Proceso detenido", sync_object.process_name)

    def get_activo(self, process_name):
        try:
            resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = '{}'".format(process_name), "yeboyebo")
            return resul[0][0]
        except Exception:
            return False

    def get_activity(self):
        i = app.control.inspect()
        active = i.active()
        scheduled = i.scheduled()
        reserved = i.reserved()

        aActive = {}
        for w in active:
            for t in active[w]:
                aActive[t['id']] = {}
                aActive[t['id']]['worker'] = w
                aActive[t['id']]['id'] = t['id']
                aActive[t['id']]['name'] = t['name']
                aActive[t['id']]['args'] = t['args']
        aScheduled = {}
        for w in scheduled:
            for t in scheduled[w]:
                aScheduled[t['request']['id']] = {}
                aScheduled[t['request']['id']]['worker'] = w
                aScheduled[t['request']['id']]['eta'] = t['eta'][:19]
                aScheduled[t['request']['id']]['id'] = t['request']['id']
                aScheduled[t['request']['id']]['name'] = t['request']['name']
                aScheduled[t['request']['id']]['args'] = t['request']['args']
        aReserved = {}
        for w in reserved:
            for t in reserved[w]:
                aReserved[t['id']] = {}
                aReserved[t['id']]['worker'] = w
                aReserved[t['id']]['id'] = t['id']
                aReserved[t['id']]['name'] = t['name']
                aReserved[t['id']]['args'] = t['args']

        return {'active': aActive, 'scheduled': aScheduled, 'reserved': aReserved}

    def revoke(self, id):
        app.control.revoke(id, terminate=True)
        return True
