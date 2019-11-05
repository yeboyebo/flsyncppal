from abc import ABC
import os
from YBLEGACY import qsatype

from controllers.base.default.controllers.upload_sync import UploadSync
from controllers.base.mirakl.drivers.mirakl import MiraklDriver


class OffersDateUpload(UploadSync, ABC):

    _ewid = None
    file_name = None

    offers_url = "<host>/api/offers/imports"
    offers_test_url = "<testhost>/api/offers/imports"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, MiraklDriver(), params)

        self.file_name = "offers_{}T{}.csv".format(self.start_date, self.start_time)

    def get_data(self):
        data = self.get_db_data()
        if data == []:
            return data

        with open(self.file_name, "w") as csvfile:
            csvfile.write("\"sku\";\"available-start-date\";\"available-end-date\"\n")
            for reg in data:
                csvfile.write("{};{};{}\n".format(reg[0], reg[1], reg[2]))

        file = open(self.file_name, "r")

        return file

    def get_db_data(self):
        body = []

        q = qsatype.FLSqlQuery()
        q.setSelect("ew.id, s.barcode, ew.fechaini, ew.fechafin")
        q.setFrom("ew_articuloseciweb ew INNER JOIN stocks s ON ew.idstock = s.idstock")
        q.setWhere("NOT ew.sincronizado")

        q.exec_()

        if not q.size():
            return body

        while q.next():
            if not self._ewid:
                self._ewid = ""
            else:
                self._ewid += ","
            self._ewid += str(q.value("ew.id"))

            fecha_fin = q.value("ew.fechafin")
            if str(fecha_fin) == "None":
                fecha_fin = ""

            body.append([q.value("s.barcode"), q.value("ew.fechaini"), fecha_fin])

        return body

    def send_data(self, data):
        data = {"import_mode": "PARTIAL_UPDATE"}
        resul = self.send_request("post", url=self.offers_url, data=data, file=self.file_name, success_code=201)
        os.remove(self.file_name)
        return resul

    def after_sync(self, response_data=None):
        if response_data and "import_id" in response_data:
            qsatype.FLSqlQuery().execSql("UPDATE ew_articuloseciweb SET sincronizado = TRUE WHERE id IN ({})".format(self._ewid))

            self.log("Éxito", "Oferta sincronizada correctamente: {}".format(response_data["import_id"]))
        else:
            self.log("Error", "No hubo una respuesta correcta del servidor")

        return self.small_sleep
