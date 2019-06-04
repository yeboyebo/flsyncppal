from abc import ABC, abstractmethod

from YBLEGACY import qsatype

from models.flsyncppal import flsyncppal_def as syncppal


class AQSync(ABC):

    start_date = None
    start_time = None
    logs = None

    process_name = None
    params = None

    def __init__(self, process_name, params=None):
        self.process_name = process_name
        self.params = params

        self.logs = []

        now = str(qsatype.Date())
        self.start_date = now[:10]
        self.start_time = now[-(8):]

    def start(self):
        try:
            return self.sync_flow()
        except Exception as e:
            self.log("Error", e)
            return {"countdown": 180, "data": {"log": self.logs}, "status": 500}

    @abstractmethod
    def sync_flow(self):
        pass

    def log(self, msg_type, msg):
        # qsatype.debug("{} {}. {}.".format(msg_type, self.process_name, str(msg).replace("'", "\"")))

        self.logs.append({
            "msg_type": msg_type,
            "msg": str(msg).replace("'", "\""),
            "process_name": self.process_name,
            "customer_name": syncppal.iface.get_customer()
        })
