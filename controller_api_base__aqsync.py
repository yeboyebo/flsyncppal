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
    log = None

    process_name = None
    params = None

    def __init__(self, process_name, driver, params=None):
        self.process_name = process_name
        self.driver = driver
        self.params = params

        self.small_sleep = 10
        self.large_sleep = 180
        self.no_sync_sleep = 300
        self.logs = []

        now = str(qsatype.Date())
        self.start_date = now[:10]
        self.start_time = now[-(8):]

    @transaction.atomic
    def start(self):
        try:
            if not self.before_sync():
                self.log("Éxito", "No es momento de sincronizar")
                return {"countdown": self.no_sync_sleep, "data": {"log": self.logs}, "status": 200}

            self.driver.session = requests.Session()
            self.driver.in_production = self.params["production"] if "production" in self.params else False

            self.driver.login()
            sync_result = self.sync()
            self.driver.logout()

            return {"countdown": sync_result, "data": {"log": self.logs}, "status": 200}

        except Exception as e:
            self.log("Error", e)
            return {"countdown": self.large_sleep, "data": {"log": self.logs}, "status": 500}

    def before_sync(self):
        return True

    @abstractmethod
    def sync(self):
        pass

    @abstractmethod
    def after_sync(self, response_data=None):
        pass

    def set_sync_params(self, params):
        for prop in params:
            setattr(self.driver, prop, params[prop])

    def send_request(self, request_type, data=None, replace=[]):
        return self.driver.send_request(request_type, data=data, replace=replace)

    def log(self, msg_type, msg):
        qsatype.debug("{} {}. {}.".format(msg_type, self.process_name, str(msg).replace("'", "\"")))

        self.logs.append({
            "msg_type": msg_type,
            "msg": msg,
            "process_name": self.process_name,
            "customer_name": syncppal.iface.get_customer()
        })
