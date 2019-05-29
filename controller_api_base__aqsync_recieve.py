from abc import ABC, abstractmethod

from controllers.api.sync.base.controllers.aqsync import AQSync


class AQSyncRecieve(AQSync, ABC):

    def sync_flow(self):
        try:
            return self.sync()
        except Exception as e:
            self.log("Error", e)
            return {"data": {"log": self.logs}, "status": 500}

    @abstractmethod
    def sync(self):
        pass
