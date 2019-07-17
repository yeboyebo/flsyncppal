from abc import ABC
from YBLEGACY import qsatype

from controllers.base.mirakl.drivers.mirakl import MiraklDriver
from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.base.mirakl.orders.serializers.ew_ventaseciweb_serializer import VentaseciwebSerializer

from models.flfact_tpv.objects.ew_ventaseciweb_raw import EwVentaseciweb


class OrdersDownload(DownloadSync, ABC):

    orders_url = "<host>/api/orders?order_state_codes=WAITING_ACCEPTANCE&start_update_date={}"
    orders_test_url = "<host>/api/orders?order_state_codes=WAITING_ACCEPTANCE&start_update_date={}"
    
    fecha_sincro = ""

    def __init__(self, process_name, params=None):
        super().__init__(process_name, MiraklDriver(), params)

    def process_data(self, data):
        if not data:
            self.error_data.append(data)
            return False

        fecha = data["last_updated_date"]
        if self.fecha_sincro != "":
            if fecha > self.fecha_sincro:
                self.fecha_sincro = fecha
        else:
            self.fecha_sincro = fecha

        eciweb_data = VentaseciwebSerializer().serialize(data)
        if not eciweb_data:
            return

        eciweb = EwVentaseciweb(eciweb_data)
        eciweb.save()

        return True

    def get_data(self):
        orders_url = self.orders_url if self.driver.in_production else self.orders_test_url

        fecha = self.dame_fechasincrotienda()
        if fecha and fecha != "None" and fecha != "":
           self.fecha_sincro = fecha
        else:
           self.fecha_sincro = "2000-01-01T00:00:01Z"

        # Tmp. Para pruebas. Quitar en producción
        self.fecha_sincro = "2000-01-01T00:00:01Z"

        result = self.send_request("get", url=orders_url, replace=[self.fecha_sincro])
        return result

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
        if not self.guarda_fechasincrotienda():
            self.log("Error", "Falló al guardar fecha última sincro")
            return False

        return self.small_sleep

    def guarda_fechasincrotienda(self):
        fecha = str(self.fecha_sincro)[:10]
        hora = str(self.fecha_sincro)[11:19]

        idsincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "esquema = 'VENTAS_ECI_WEB'")

        if idsincro:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE id = {}".format(fecha, hora, idsincro))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('AEVV', 'VENTAS_ECI_WEB', '{}', '{}')".format(fecha, hora))

        return True

    def dame_fechasincrotienda(self):
        return qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro || 'T' || horasincro || 'Z'", "esquema = 'VENTAS_ECI_WEB'")
