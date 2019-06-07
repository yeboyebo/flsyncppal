from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class SimpleProductSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("product//name", "sc.descripcion")
        self.set_string_relation("product//weight", "a.peso")
        self.set_string_relation("product//price", "a.pvp")

        self.set_string_value("product//sku", self.get_sku())
        self.set_string_value("product//attribute_set_id", "4")
        self.set_string_value("product//status", "1")
        self.set_string_value("product//visibility", "1")
        self.set_string_value("product//type_id", "simple")

        self.set_string_value("product//extension_attributes//stock_item//qty", self.get_stock())
        self.set_string_value("product//extension_attributes//stock_item//is_in_stock", "True")

        custom_attributes = [
            {"attribute_code": "description", "value": self.get_init_value("sc.descripcion")},
            {"attribute_code": "tax_class_id", "value": "2"},
            {"attribute_code": "barcode", "value": self.get_init_value("aa.barcode")},
            {"attribute_code": "size", "value": self.get_init_value("aa.talla")}
        ]

        self.set_data_value("product//custom_attributes", custom_attributes)

        return True

    def get_sku(self):
        referencia = self.get_init_value("sc.idobjeto")
        talla = self.get_init_value("aa.talla")

        if talla == "TU":
            return referencia

        return "{}-{}".format(referencia, talla)

    def get_stock(self):
        disponible = self.get_init_value("s.disponible")

        if not disponible or isNaN(disponible) or disponible < 0:
            return 0

        return disponible
