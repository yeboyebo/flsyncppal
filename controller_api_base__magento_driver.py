from YBLEGACY import qsatype

from controllers.api.sync.base.drivers.default_driver import DefaultDriver


class MagentoDriver(DefaultDriver):

    auth = None
    test_auth = None

    def get_headers(self):
        auth = self.auth if qsatype.FLUtil.isInProd() else self.test_auth

        if not auth or auth == "":
            raise NameError("La clave de autenticación no se indicó o no se hizo correctamente")

        return {
            "Content-Type": "application/json",
            "Authorization": auth
        }
