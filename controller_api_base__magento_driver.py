from controllers.api.sync.base.drivers.web_driver import WebDriver


class MagentoDriver(WebDriver):

    def login(self):
        return True

    def logout(self):
        return True
