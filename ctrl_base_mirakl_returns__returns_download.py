from abc import ABC
from YBLEGACY import qsatype

from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.base.mirakl.drivers.mirakl import MiraklDriver
from controllers.base.mirakl.returns.serializers.ew_devolucioneseciweb_serializer import DevolucioneseciwebSerializer
from models.flfact_tpv.objects.ew_devolucioneseciweb_raw import EwDevolucioneseciweb

class ReturnsDownload(DownloadSync, ABC):

    # returns_url = "<host>/api/messages?start_date={}"
    # returns_test_url = "<testhost>/api/messages?start_date={}"

    # Tmp. Para pruebas. Quitar en producción y activar las de arrriba
    returns_url = "https://marketplace.elcorteingles.es/api/messages"
    returns_test_url = "https://marketplace.elcorteingles.es/api/messages"
    
    fecha_sincro = ""
    esquema = "DEVOLS_ECI_WEB"
    codtienda = "AEVV"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, MiraklDriver(), params)

    def process_data(self, data):
        if not data:
            self.error_data.append(data)
            return False

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

        devoleciweb = EwDevolucioneseciweb(eciweb_data)
        devoleciweb.save()

        if not self.masAccionesProcessData(eciweb_data):
        	return False

        return True

    def masAccionesProcessData(self, eciweb_data):
    	return True

    def get_data(self):
        returns_url = self.returns_url if self.driver.in_production else self.returns_test_url

        fecha = self.dame_fechasincrotienda(self.esquema, self.codtienda)
        if fecha and fecha != "None" and fecha != "":
           self.fecha_sincro = fecha
        else:
           self.fecha_sincro = "2000-01-01T00:00:01Z"

        # Tmp. Para pruebas. Quitar en producción
        self.fecha_sincro = "2000-01-01T00:00:01Z"
        result = self.send_request("get", url=returns_url, replace=[self.fecha_sincro])

        return result

    def process_all_data(self, all_data):
        if all_data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        try:
            if self.process_data(all_data):
                self.success_data.append(all_data)
        except Exception as e:
            print("exception " + str(e))
            self.sync_error(all_data, e)

        return True

    def after_sync(self):
        if not self.guarda_fechasincrotienda(self.esquema, self.codtienda):
            self.log("Error", "Falló al guardar fecha última sincro")
            return self.small_sleep

        return self.small_sleep

    def guarda_fechasincrotienda(self, esquema, codtienda):
        fecha = str(self.fecha_sincro)[:10]
        hora = str(self.fecha_sincro)[11:19]

        idsincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))

        if idsincro:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE id = {}".format(fecha, hora, idsincro))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('{}', '{}', '{}', '{}')".format(codtienda, esquema, fecha, hora))

        return True

    def dame_fechasincrotienda(self, esquema, codtienda):
        return qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro || 'T' || horasincro || 'Z'", "esquema = '{}' AND codtienda = '{}'".format(esquema, codtienda))
