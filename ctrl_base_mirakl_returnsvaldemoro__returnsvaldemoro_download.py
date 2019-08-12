from abc import ABC
from YBLEGACY import qsatype
import json
import xmltodict

from datetime import datetime, timedelta


# from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.base.mirakl.drivers.mirakl import MiraklDriver
from controllers.base.mirakl.returnsvaldemoro.serializers.ew_devolucioneseciweb_serializer import DevolucioneseciwebSerializer
from controllers.base.mirakl.returns.controllers.returns_download import ReturnsDownload
from models.flfact_tpv.objects.ew_devolucioneseciweb_raw import EwDevolucioneseciweb

class ReturnsValdemoroDownload(ReturnsDownload, ABC):

    esquema = "DEVOLSVAL_ECI_WEB"

    def process_data(self, data):
        print("process_data")
        if not data:
            self.error_data.append(data)
            return False

        if data["subject"] != "Devolución artículo":
            return False

       datosDevol = json.loads(json.dumps(xmltodict.parse(data["body"])))
        tipoMsg = datosDevol["Mensaje"]["tipoMensaje"]

        if tipoMsg != "001":
            return True

        dirRecogida = datosDevol["Mensaje"]["Recogida"]["direccionRecogida"]
        if dirRecogida.find("VALDEMORO") == -1:
            return True

        fecha = data["date_created"]
        if self.fecha_sincro != "":
            if fecha > self.fecha_sincro:
                self.fecha_sincro = fecha
        else:
            self.fecha_sincro = fecha

        eciweb_data = DevolucioneseciwebSerializer().serialize(data)
        if not eciweb_data:
            self.error_data.append(data)
            return False

        if qsatype.FLUtil.sqlSelect("ew_devolucioneseciweb", "idventaweb", "idventaweb = '{}'".format(eciweb_data["idventaweb"])):
            self.log("Error", "La venta {} ya ha sido procesada".format(eciweb_data["idventaweb"]))
            return True

        idComanda = self.masAccionesProcessData(eciweb_data)
        if not idComanda:
            raise NameError("No se pudo crear la devolución")

        eciweb_data["idtpv_comanda"] = idComanda
        eciweb_data["datosdevol"] = data["body"]
        devoleciweb = EwDevolucioneseciweb(eciweb_data)
        devoleciweb.save()

        return True

    def process_all_data(self, all_data):
        print("process_all_data base ")
        data = {
            "archived": False,
            "body": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Mensaje><tipoMensaje>010</tipoMensaje><Devolucion><EAN>008433614152155</EAN><lineaPedido>20190804141302-UATG32727563-A-2</lineaPedido><unidades>0001</unidades></Devolucion><Recogida><codigoRecogida>0365272220190807</codigoRecogida><direccionRecogida>CTRA/ANDALUCIA KM 23,5S/N,(ATT.DVD). CP: 28343. VALDEMORO</direccionRecogida></Recogida><texto>Le informamos que se ha iniciado un proceso de devolución con abono al cliente mediante TPV en Centro Comercial.</texto></Mensaje>",
            "commercial_id": "20190804141302-UATG32727563",
            "date_created": "2019-08-07T14:01:59Z",
            "from_id": "1",
            "from_name": "Operator",
            "from_type": "OPERATOR",
            "id": 1245035,
            "order_id": "20190804141302-UATG32727563-A",
            "read": False,
            "subject": "Devolución artículo",
            "to_shop_archived": False,
            "to_shop_id": 2449,
            "to_shop_name": "EL GANSO"
        }
        print("process all data")
        if self.process_data(data):
            self.success_data.append(data)
        print("fin process all data")
        return True