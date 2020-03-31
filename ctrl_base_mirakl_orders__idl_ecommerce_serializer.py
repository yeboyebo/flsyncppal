from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class IdlEcommerceSerializer(DefaultSerializer):

    def get_data(self):

        transIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "transportista", "LOWER(metodoenviomg) = 'MIRAKL' OR UPPER(metodoenviomg) = 'MIRAKL' OR metodoenviomg = 'MIRAKL'")

        if not transIDL:
            transIDL = 'MRW'

        metodoIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "metodoenvioidl", "LOWER(metodoenviomg) = 'MIRAKL' OR UPPER(metodoenviomg) = 'MIRAKL' OR metodoenviomg = 'MIRAKL'")

        if not metodoIDL:
            metodoIDL = '3Urgente 19 Expedición'

        prefijo_codpostal = self.get_init_value("customer//billing_address//zip_code")[:2]

        if str(prefijo_codpostal) == "35" or str(prefijo_codpostal) == "38":
            transIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "transportista", "LOWER(metodoenviomg) = 'MIRAKL_CANARIAS' OR UPPER(metodoenviomg) = 'MIRAKL_CANARIAS' OR metodoenviomg = 'MIRAKL_CANARIAS'")

            if not transIDL:
                transIDL = 'MRW'

            metodoIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "metodoenvioidl", "LOWER(metodoenviomg) = 'MIRAKL_CANARIAS' OR UPPER(metodoenviomg) = 'MIRAKL_CANARIAS' OR metodoenviomg = 'MIRAKL_CANARIAS'")

            if not metodoIDL:
                metodoIDL = '3Ecommerce'

        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)
        self.set_string_value("tipo", "VENTA")
        self.set_string_value("transportista", transIDL)
        self.set_string_value("metodoenvioidl", metodoIDL, skip_replace=True)
        self.set_data_value("imprimiralbaran", False)
        self.set_data_value("imprimirfactura", False)
        self.set_data_value("imprimirdedicatoria", False)
        self.set_data_value("emisor", None)
        self.set_data_value("receptor", None)
        self.set_data_value("mensajededicatoria", None)
        self.set_data_value("esregalo", False)
        self.set_data_value("facturaimpresa", False)
        self.set_data_value("envioidl", False)
        self.set_data_value("eseciweb", True)
        self.set_data_value("numseguimientoinformado", False)
        self.set_string_value("confirmacionenvio", "No")

        return True
