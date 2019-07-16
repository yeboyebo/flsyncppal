from YBLEGACY import qsatype
from abc import ABC

from controllers.base.mirakl.drivers.mirakl import MiraklDriver
from controllers.base.default.controllers.download_sync import DownloadSync
import time
import string
import json

class ShippingDownload(DownloadSync, ABC):

    shipping_url = "<host>/api/orders?order_state_codes=SHIPPING"
    shipping_test_url = "<testhost>/api/orders?order_state_codes=SHIPPING"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, MiraklDriver(), params)

    def process_data(self, data):
        if not data:
            self.error_data.append(data)
            return False

        orderId = str(data["order_id"])
        print("order id " + orderId)        
        formatData = str(data).replace("'", "\"")

        resul = qsatype.FLSqlQuery().execSql("SELECT idweb FROM ew_ventaseciweb WHERE idweb = '" + orderId + "' AND envioinformado")
        if result:
            idweb = resul[0][0]
            if idweb and idweb != "None":
                return True

        if not qsatype.FLUtil.execSql("UPDATE ew_ventaseciweb SET datosenvio = '" + formatData + "' AND envioinformado = true WHERE idweb = '" + orderId + "'"):
            return False

        return True

    def get_data(self):
        shipping_url = self.shipping_url if self.driver.in_production else self. shipping_test_url
        return self.send_request("get", url=shipping_url)

    def process_all_data(self, all_data):
        if all_data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        for data in all_data["orders"]:
            try:
                if self.process_data(data):
                    self.success_data.append(data)
            except Exception as e:
                self.sync_error(data, e)

        return True

    def after_sync(self):
        return self.small_sleep
