import json

from django.http import HttpResponse

from sync.tasks import task_manager


# @class_declaration interna_getactivity #
class interna_getactivity():
    pass


# @class_declaration flsyncppal_getactivity #
class flsyncppal_getactivity(interna_getactivity):

    @staticmethod
    def start(pk, data):
        data = task_manager.get_activity()

        return HttpResponse(json.dumps(data), content_type="application/json")


# @class_declaration getactivity #
class getactivity(flsyncppal_getactivity):
    pass
