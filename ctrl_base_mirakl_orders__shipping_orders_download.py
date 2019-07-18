from abc import ABC
from YBLEGACY import qsatype

from controllers.base.mirakl.drivers.mirakl import MiraklDriver
from controllers.base.mirakl.orders.controllers.orders_download import OrdersDownload
from controllers.base.mirakl.orders.serializers.ew_ventaseciweb_serializer import VentaseciwebSerializer
from controllers.base.mirakl.orders.serializers.order_serializer import OrderSerializer

from models.flfact_tpv.objects.ew_ventaseciweb_raw import EwVentaseciweb
from models.flfact_tpv.objects.egorder_raw import EgOrder


class ShippingOrdersDownload(OrdersDownload, ABC):

    orders_url = "<host>/api/orders?order_state_codes=SHIPPING&start_update_date={}"
    orders_test_url = "<host>/api/orders?order_state_codes=SHIPPING&start_update_date={}"

    def __init__(self, process_name, params=None):
        super().__init__(process_name, MiraklDriver(), params)

    def get_order_serializer(self):
        return OrderSerializer()

    def get_vtaeci_serializer(self):
        return VentaseciwebSerializer()

    def get_order_model(self, data):
        return EgOrder(data)

    def get_vtaeci_model(self, data):
        return EwVentaseciweb(data)

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

        eciweb_data = self.get_vtaeci_serializer().serialize(data)
        if not eciweb_data:
            return

        order_data = self.get_order_serializer().serialize(data)
        if not order_data:
            return

        order = self.get_order_model(order_data)
        order.save()

        eciweb_data["idtpv_comanda"] = order.cursor.valueBuffer("idtpv_comanda")

        eciweb = self.get_vtaeci_model(eciweb_data)
        eciweb.save()

        return True
