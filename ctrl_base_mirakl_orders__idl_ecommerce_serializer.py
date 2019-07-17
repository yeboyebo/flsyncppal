from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class IdlEcommerce(DefaultSerializer):

    def get_data(self):
        shipping_method = self.get_init_value("shipping_type_label")

        trans_idl = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "transportista", "LOWER(metodoenviomg) = '{}' OR UPPER(metodoenviomg) = '{}' OR metodoenviomg = '{}'".format(shipping_method, shipping_method, shipping_method))

        if not trans_idl:
            return True

        idl_method = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "metodoenvioidl", "LOWER(metodoenviomg) = '{}' OR UPPER(metodoenviomg) = '{}' OR metodoenviomg = '{}'".format(shipping_method, shipping_method, shipping_method))

        imprimir_factura = False

        codpais = self.get_init_value("customer//billing_address//country_iso_code")

        if codpais:
            if codpais == "ES":
                # TMP. Aqui deberia haber una comprobacion por provincia, pero no tenemos
                imprimir_factura = True
            else:
                imprimirFacturaPais = qsatype.FLUtil.sqlSelect("paises", "imprimirfactura", "codiso = '{}'".format(codpais))
                if imprimirFacturaPais:
                    imprimir_factura = True

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)
        self.set_string_value("tipo", "VENTA")
        self.set_string_value("transportista", str(trans_idl))
        self.set_string_value("metodoenvioidl", str(idl_method))
        self.set_data_value("imprimiralbaran", True)
        self.set_data_value("imprimirfactura", imprimir_factura)
        self.set_data_value("imprimirdedicatoria", False)
        self.set_data_value("emisor", None)
        self.set_data_value("receptor", None)
        self.set_data_value("mensajededicatoria", None)
        self.set_data_value("esregalo", False)
        self.set_data_value("facturaimpresa", False)
        self.set_data_value("envioidl", False)
        self.set_data_value("numseguimientoinformado", False)
        self.set_string_value("confirmacionenvio", 'No')

        return True
