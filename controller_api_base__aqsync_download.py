from abc import ABC, abstractmethod

from controllers.api.sync.base.controllers.aqsync import AQSync


class AQSyncDownload(AQSync, ABC):

    success_data = None
    error_data = None

    def __init__(self, process_name, driver, params=None):
        super().__init__(process_name, driver, params)

        self.success_data = []
        self.error_data = []

        self.origin_field = "entity_id"

    def sync(self):
        response_data = self.send_request("get")
        if not self.process_all_data(response_data):
            return self.large_sleep

        return self.after_sync()

    def process_all_data(self, all_data):
        if all_data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        for data in all_data:
            try:
                self.process_data(data)
                self.success_data.append(data)
            except Exception as e:
                self.error_data.append(data)
                self.sync_error(data, e)

        return True

    @abstractmethod
    def process_data(self, data):
        pass

    @abstractmethod
    def after_sync(self, response_data=None):
        pass

    def sync_error(self, data, exc):
        self.log("Error", "Ocurrió un error al sincronizar el registro {}. {}".format(data[self.origin_field], exc))

    def after_sync_error(self, data, exc):
        self.log("Error", "Ocurrió un error al marcar como sincronizado el registro {}. {}".format(data[self.origin_field], exc))
