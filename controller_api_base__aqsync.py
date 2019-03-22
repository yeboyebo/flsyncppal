import requests
from abc import ABC, abstractmethod

from django.db import transaction

from YBLEGACY import qsatype

from models.flsyncppal import flsyncppal_def as syncppal


class AQSync(ABC):

    small_sleep = None
    large_sleep = None
    no_sync_sleep = None

    start_date = None
    start_time = None
    success_code = None

    process_name = None
    params = None
    url = None
    auth = None
    test_url = None
    test_auth = None

    def __init__(self, process_name, params=None):
        self.process_name = process_name
        self.params = params

        self.small_sleep = 10
        self.large_sleep = 180
        self.no_sync_sleep = 300
        self.success_code = 200

        now = str(qsatype.Date())
        self.start_date = now[:10]
        self.start_time = now[-(8):]

    @transaction.atomic
    def start(self):
        try:
            if not self.before_sync():
                self.log("Éxito", "No es momento de sincronizar")
                return self.no_sync_sleep

            return self.sync()
        except Exception as e:
            self.log("Error", e)
            return self.large_sleep

    def before_sync(self):
        return True

    @abstractmethod
    def sync(self):
        pass

    @abstractmethod
    def after_sync(self, response_data=None):
        pass

    def set_sync_params(self, params):
        props = ["success_code", "url", "auth", "test_url", "test_auth"]

        for prop in props:
            if prop in params:
                setattr(self, prop, params[prop])

    def send_request(self, request_type, data=None, replace=[]):
        headers = self.get_headers()
        url = self.get_url(replace)

        response = None

        if request_type == "get":
            response = requests.get(url, headers=headers, data=data)
        elif request_type == "post":
            response = requests.post(url, headers=headers, data=data)
        elif request_type == "put":
            response = requests.put(url, headers=headers, data=data)
        else:
            raise NameError("No se encuentra el tipo de petición {}".format(request_type))

        return self.proccess_response(response)

    def proccess_response(self, response):
        if response.status_code == self.success_code:
            try:
                return response.json()
            except Exception as e:
                raise NameError("Mala respuesta del servidor. {}".format(e))
        else:
            raise NameError("Código {}. {}".format(response.status_code, response.text))

    def get_url(self, replace=[]):
        url = self.url if qsatype.FLUtil.isInProd() else self.test_url

        if replace:
            url = url.format(*replace)

        if not url or url == "":
            raise NameError("La url no se indicó o no se hizo correctamente")

        return url

    def get_headers(self):
        auth = self.auth if qsatype.FLUtil.isInProd() else self.test_auth

        if not auth or auth == "":
            raise NameError("La clave de autenticación no se indicó o no se hizo correctamente")

        return {
            "Content-Type": "application/json",
            "Authorization": auth
        }

    def log(self, msg_type, msg):
        qsatype.debug("{} {}. {}.".format(msg_type, self.process_name, str(msg).replace("'", "\"")))
        syncppal.iface.log("{}. {}".format(msg_type, str(msg).replace("'", "\"")), self.process_name)
