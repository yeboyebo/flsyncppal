from abc import ABC
import os
from YBLEGACY import qsatype

from controllers.base.default.controllers.upload_sync import UploadSync
from controllers.base.mirakl.drivers.mirakl import MiraklDriver


class OffersUpload(UploadSync, ABC):

    offers_url = "<host>/api/offers/imports"
    offers_test_url = "<testhost>/api/offers/imports"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, MiraklDriver(), params)

    def get_data(self):
        data = self.get_db_data()
        if data == []:
            return data

        print("Data:", data)
        with open("students.csv", "w") as csvfile:
            csvfile.write("\"sku\";\"quantity\"\n")
            for r in range(len(data)):
                csvfile.write(str(data[r][0]) + ";" + str(data[r][1]))

        file = open("students.csv", "r")
        print("//FILE: ", file.read())

        return file

    def get_db_data(self):
        body = []
        idlinea = qsatype.FLUtil.sqlSelect("eg_sincrostockweb", "idssw", "NOT sincronizado ORDER BY idssw LIMIT 1")

        if not idlinea:
            return body

        self.idlinea = idlinea

        q = qsatype.FLSqlQuery()
        q.setSelect("s.barcode, s.disponible")
        q.setFrom("eg_sincrostockweb sw INNER JOIN stocks s ON sw.idstock = s.idstock")
        q.setWhere("sw.idssw = {}".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        disponible_restar = self.dameCantidadDisponibleARestar()
        while q.next():
            disponible = int(q.value("s.disponible")) - int(disponible_restar)
            body.append([q.value("s.barcode"), disponible])
        return body

    def send_data(self, data):
        print("SENDATA: ", data.read())
        self.send_request("post", url=self.offers_url, data=data, file="students.csv")
        os.remove("students.csv")

    def dameCantidadDisponibleARestar(self):
        return 2

    def after_sync(self):
        pass
