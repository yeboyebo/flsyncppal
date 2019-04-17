import requests
from abc import ABC

from YBLEGACY import qsatype


class DefaultDriver(ABC):

    session = None

    url = None
    test_url = None
    auth = None
    test_auth = None

    def send_request(self, request_type, url=None, data=None, replace=[]):
        url = url if url else self.get_url(replace)
        headers = self.get_headers()

        response = None

        if request_type == "get":
            response = self.session.get(url, headers=headers, data=data)
        elif request_type == "post":
            response = self.session.post(url, headers=headers, data=data)
        elif request_type == "put":
            response = self.session.put(url, headers=headers, data=data)
        elif request_type == "delete":
            response = self.session.delete(url, headers=headers, data=data)
        else:
            raise NameError("No se encuentra el tipo de petición {}".format(request_type))

        return self.proccess_response(response)

    def get_url(self, replace=[]):
        url = self.url if qsatype.FLUtil.isInProd() else self.test_url

        if replace:
            url = url.format(*replace)

        if not url or url == "":
            raise NameError("La url no se indicó o no se hizo correctamente")

        return url

    def proccess_response(self, response):
        if response.status_code == requests.codes.ok:
            try:
                return response.json()
            except Exception as e:
                raise NameError("Mala respuesta del servidor. {}".format(e))
        else:
            raise NameError("Código {}. {}".format(response.status_code, response.text))

    def get_headers(self):
        headers = {
            "Content-Type": "application/json"
        }

        auth = self.auth if qsatype.FLUtil.isInProd() else self.test_auth
        if auth:
            headers.update({"Authorization": auth})

        return headers

    def login(self):
        return True

    def logout(self):
        return True
