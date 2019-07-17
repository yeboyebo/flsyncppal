from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer

from controllers.base.mirakl.orders.serializers.order_line_serializer import OrderLineSerializer
from controllers.base.mirakl.orders.serializers.order_shippingline_serializer import OrderShippingLineSerializer
from controllers.base.mirakl.orders.serializers.order_expensesline_serializer import OrderExpensesLineSerializer
from controllers.base.mirakl.orders.serializers.cashcount_serializer import CashCountSerializer
from controllers.base.mirakl.orders.serializers.order_payment_serializer import OrderPaymentSerializer
from controllers.base.mirakl.orders.serializers.idl_ecommerce_serializer import IdlEcommerceSerializer


class EgOrderSerializer(DefaultSerializer):

    def get_data(self):
        # TMP. Comprobacion de si ya existe??

        codigo = self.get_codigo()
        self.set_string_value("codigo", codigo, max_characters=15)

        codtienda = self.get_codtienda()
        self.set_string_value("codtpv_puntoventa", codtienda)
        self.set_string_value("codalmacen", codtienda)
        self.set_string_value("codtienda", codtienda)

        # TMP. Codigo agente
        self.set_string_value("codtpv_agente", "0350")

        self.set_string_relation("coddivisa", "currency_iso_code")
        self.set_string_value("estado", "Cerrada")

        self.set_data_value("editable", True)
        self.set_data_value("tasaconv", 1)
        self.set_data_value("ptesincrofactura", True)

        # iva = self.init_data["items"][-1]["iva"]
        # neto = round(parseFloat(self.init_data["grand_total"] / ((100 + iva) / 100)), 2)
        # total_iva = self.init_data["grand_total"] - neto

        self.set_data_relation("total", "total_price")
        self.set_data_relation("pagado", "total_price")
        self.set_data_relation("neto", "price")
        self.set_data_relation("totaliva", "total_commission")

        # self.set_string_relation("email", "email", max_characters=100)
        # self.set_string_relation("codtarjetapuntos", "card_points", max_characters=15)
        # self.set_string_relation("cifnif", "cif", max_characters=20, default="-")
        self.set_string_relation("fecha", "created_date", max_characters=10)

        self.set_string_relation("codpostal", "customer//billing_address//zip_code", max_characters=10)
        self.set_string_relation("ciudad", "customer//billing_address//city", max_characters=100)
        # self.set_string_relation("provincia", "customer//billing_address//region", max_characters=100)
        self.set_string_relation("codpais", "customer//billing_address//country_iso_code", max_characters=100)
        self.set_string_relation("telefono1", "customer//billing_address//phone", max_characters=30)

        nombrecliente = "{} {}".format(self.get_init_value("customer//billing_address//firstname"), self.get_init_value("customer//billing_address//lastname"))
        self.set_string_value("nombrecliente", nombrecliente, max_characters=100)

        # street = self.get_init_value("customer//billing_address//street_1").split("\n")
        # dirtipovia = street[0] if len(street) >= 1 else ""
        # direccion = street[1] if len(street) >= 2 else ""
        # dirnum = street[2] if len(street) >= 3 else ""
        # dirotros = street[3] if len(street) >= 4 else ""

        self.set_string_relation("direccion", "customer//billing_address//street_1", max_characters=100)
        # self.set_string_value("dirtipovia", dirtipovia, max_characters=100)
        # self.set_string_value("dirnum", dirnum, max_characters=100)
        # self.set_string_value("dirotros", dirotros, max_characters=100)

        self.set_string_value("codserie", self.get_codserie())
        self.set_string_value("codejercicio", self.get_codejercicio())
        self.set_string_value("hora", self.get_hora())
        self.set_string_value("codpago", self.get_codpago(), max_characters=10)
        self.set_string_value("egcodfactura", codigo, max_characters=12)

        iva = self.init_data["items"][-1]["commission_rate_vat"]

        if "lines" not in self.data["children"]:
            self.data["children"]["lines"] = []

        if "payments" not in self.data["children"]:
            self.data["children"]["payments"] = []

        for item in self.init_data["items"]:
            item.update({
                "codcomanda": self.data["codigo"]
            })

            line_data = OrderLineSerializer().serialize(item)
            self.data["children"]["lines"].append(line_data)

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "fecha": self.data["fecha"],
            "iva": iva
        })

        linea_envio = OrderShippingLineSerializer().serialize(new_init_data)
        # linea_descuento = EgOrderDiscountLineSerializer().serialize(new_init_data)
        # linea_vale = EgOrderVoucherLineSerializer().serialize(new_init_data)
        linea_gastos = OrderExpensesLineSerializer().serialize(new_init_data)
        arqueo_web = CashCountSerializer().serialize(self.data)
        new_data = self.data.copy()
        new_data.update({"idarqueo": arqueo_web["idtpv_arqueo"]})
        pago_web = OrderPaymentSerializer().serialize(new_data)
        idl_ecommerce = IdlEcommerceSerializer().serialize(new_init_data)

        self.data["children"]["lines"].append(linea_gastos)
        self.data["children"]["payments"].append(pago_web)
        self.data["children"]["shippingline"] = linea_envio
        self.data["children"]["idl_ecommerce"] = idl_ecommerce
        # self.data["children"]["lines"].append(linea_descuento)
        # self.data["children"]["lines"].append(linea_vale)

        if "skip" in arqueo_web and arqueo_web["skip"]:
            arqueo_web = False
        self.data["children"]["cashcount"] = arqueo_web

        return True

    def get_codtienda(self):
        return "AEVV"

    def get_codserie(self):
        pais = self.data["codpais"]
        codpostal = self.data["codpostal"]

        codpais = None
        codserie = "A"
        codpostal2 = None

        if not pais or pais == "":
            return codserie

        codpais = qsatype.FLUtil.quickSqlSelect("paises", "codpais", "UPPER(codpais) = '{}'".format(pais.upper()))
        if not codpais or codpais == "":
            return codserie

        if codpais != "ES":
            codserie = "X"
        elif codpostal and codpostal != "":
            codpostal2 = codpostal[:2]
            if codpostal2 == "35" or codpostal2 == "38" or codpostal2 == "51" or codpostal2 == "52":
                codserie = "X"

        return codserie

    def get_codejercicio(self):
        date = self.data["fecha"][:10]
        splitted_date = date.split("-")

        return splitted_date[0]

    def get_hora(self):
        hour = self.get_init_value("created_date")[-9:-1]
        hour = "23:59:59" if hour == "00:00:00" else hour

        return hour

    def get_codpago(self):
        return "TARJ"

    def get_codigo(self):
        prefix = "AEVV"
        ultima_vta = None

        id_ultima = qsatype.FLUtil.sqlSelect("tpv_comandas", "codigo", "codigo LIKE '{}%' ORDER BY codigo DESC LIMIT 1".format(prefix))

        if id_ultima:
            ultima_vta = parseInt(str(id_ultima)[-(12 - len(prefix)):])
        else:
            ultima_vta = 0

        ultima_vta = ultima_vta + 1

        return "{}{}".format(prefix, qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(ultima_vta), 12 - len(prefix)))
