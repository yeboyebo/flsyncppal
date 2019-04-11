import requests
from abc import ABC, abstractmethod

from YBLEGACY import qsatype


class DefaultDriver(ABC):

    success_code = None
    url = None
    test_url = None

    def __init__(self):
        self.success_code = 200

    def send_request(self, request_type, url=None, data=None, replace=[], success_code=None):
        url = url if url else self.get_url(replace)
        headers = self.get_headers()

        response = None

        if request_type == "get":
            response = requests.get(url, headers=headers, data=data)
        elif request_type == "post":
            response = requests.post(url, headers=headers, data=data)
        elif request_type == "put":
            response = requests.put(url, headers=headers, data=data)
        elif request_type == "delete":
            response = requests.delete(url, headers=headers, data=data)
        else:
            raise NameError("No se encuentra el tipo de petición {}".format(request_type))

        if not success_code:
            success_code = self.success_code

        return self.proccess_response(response, success_code)

    def get_url(self, replace=[]):
        url = self.url if qsatype.FLUtil.isInProd() else self.test_url

        if replace:
            url = url.format(*replace)

        if not url or url == "":
            raise NameError("La url no se indicó o no se hizo correctamente")

        return url

    def proccess_response(self, response, success_code):
        if response.status_code == success_code:
            try:
                return response.json()
            except Exception as e:
                raise NameError("Mala respuesta del servidor. {}".format(e))
        else:
            raise NameError("Código {}. {}".format(response.status_code, response.text))

    @abstractmethod
    def get_headers(self):
        pass

    def login(self):
        return True

    def logout(self):
        return True
