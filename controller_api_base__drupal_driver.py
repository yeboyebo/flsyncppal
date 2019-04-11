from YBLEGACY import qsatype

from controllers.api.sync.base.drivers.default_driver import DefaultDriver


class DrupalDriver(DefaultDriver):

    session_id = None
    user_token = None

    login_user = None
    test_login_user = None
    login_password = None
    test_login_password = None

    login_url = None
    test_login_url = None
    logout_url = None
    test_logout_url = None

    def get_headers(self):
        headers = {"Content-Type": "application/json"}

        if self.session_id and self.user_token:
            headers["Cookie"] = self.session_id
            headers["X-CSRF-Token"] = self.user_token

        return headers

    def login(self):
        url = self.login_url if qsatype.FLUtil.isInProd() else self.test_login_url
        user = self.login_user if qsatype.FLUtil.isInProd() else self.test_login_user
        password = self.login_password if qsatype.FLUtil.isInProd() else self.test_login_password

        body = {
            "username": user,
            "password": password
        }

        response = self.send_request("post", url, data=body, success_code=200)
        if response:
            self.session_id = response["sessid"]
            self.user_token = response["token"]

        return True

    def logout(self):
        url = self.logout_url if qsatype.FLUtil.isInProd() else self.test_logout_url

        self.send_request("post", url, data={}, success_code=200)

        return True
