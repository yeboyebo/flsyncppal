from controllers.api.sync.base.drivers.default_driver import WebDriver


class MagentoDriver(WebDriver):

    def login(self):
        return True

    def logout(self):
        return True
