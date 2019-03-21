import json
from abc import ABC, abstractmethod

from controllers.api.sync.base.aqsync import AQSync


class AQSyncUpload(AQSync, ABC):

    def __init__(self, process_name, params=None):
        super().__init__(process_name, params)

        self.success_code = 202

    def sync(self):
        data = self.get_data()

        if data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return self.large_sleep

        response_data = self.send_request("post", data=json.dumps(data))
        return self.after_sync(response_data)

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def after_sync(self, response_data=None):
        pass
