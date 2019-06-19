from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class SimpleProductSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("product//name", "lsc.descripcion")
        self.set_string_relation("product//weight", "a.peso")
        self.set_string_relation("product//price", "a.pvp")

        self.set_string_value("product//sku", self.get_sku())
        self.set_string_value("product//attribute_set_id", "4")
        self.set_string_value("product//status", "1")

        is_visibility = "1"
        if  self.get_init_value("aa.talla") == "TU":
            is_visibility = "4"

        self.set_string_value("product//visibility", is_visibility)
        self.set_string_value("product//type_id", "simple")

        cant_stock = self.get_stock()
        is_in_stock = True
        if cant_stock == 0:
            is_in_stock = False

        self.set_string_value("product//extension_attributes//stock_item//qty", cant_stock)
        self.set_string_value("product//extension_attributes//stock_item//is_in_stock", is_in_stock)

        large_description = self.get_init_value("a.mgdescripcion")
        if large_description == False or large_description == "" or large_description == None or str(large_description) == "None":
            large_description = self.get_init_value("lsc.descripcion")

        short_description = self.get_init_value("a.mgdescripcioncorta")

        if short_description == False or short_description == "" or short_description == None or str(short_description) == "None":
            short_description = self.get_init_value("lsc.descripcion")

        custom_attributes = [
            {"attribute_code": "description", "value": large_description},
            {"attribute_code": "short_description", "value": short_description},
            {"attribute_code": "tax_class_id", "value": "2"},
            {"attribute_code": "barcode", "value": self.get_init_value("aa.barcode")},
            {"attribute_code": "size", "value": self.get_init_value("t.indice")}
        ]

        self.set_data_value("product//custom_attributes", custom_attributes)

        return True

    def get_sku(self):
        referencia = self.get_init_value("lsc.idobjeto")
        talla = self.get_init_value("aa.talla")

        if talla == "TU":
            return referencia

        return "{}-{}".format(referencia, talla)

    def get_stock(self):
        disponible = self.get_init_value("s.disponible")

        if not disponible or isNaN(disponible) or disponible < 0:
            return 0

        return disponible
