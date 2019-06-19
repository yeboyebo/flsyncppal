from controllers.base.default.serializers.default_serializer import DefaultSerializer


class ConfigurableProductSerializer(DefaultSerializer):

    def get_data(self):
        if self.get_init_value("aa.talla") == "TU":
            return False

        self.set_string_relation("product//name", "lsc.descripcion")
        self.set_string_relation("product//weight", "a.peso")
        self.set_string_relation("product//sku", "lsc.idobjeto")

        self.set_string_value("product//attribute_set_id", "4")
        self.set_string_value("product//status", "1")
        self.set_string_value("product//visibility", "4")
        self.set_string_value("product//type_id", "configurable")

        large_description = self.get_init_value("a.mgdescripcion")
        if large_description == False or large_description == "" or large_description == None or str(large_description) == "None":
            large_description = self.get_init_value("lsc.descripcion")

        short_description = self.get_init_value("a.mgdescripcioncorta")

        if short_description == False or short_description == "" or short_description == None or str(short_description) == "None":
            short_description = self.get_init_value("lsc.descripcion")

        custom_attributes = [
            {"attribute_code": "description", "value": large_description},
            {"attribute_code": "short_description", "value": short_description},
            {"attribute_code": "tax_class_id", "value": "2"}
        ]

        size_values = [{"value_index": size} for size in self.get_init_value("indice_tallas")]
        extension_attributes = {
            "configurable_product_options": [{
                "attribute__id": 139,
                "label": "Size",
                "values": size_values
            }],
            "stock_item": {"is_in_stock": self.get_init_value("stock_disponible")}
        }

        self.set_data_value("product//custom_attributes", custom_attributes)
        self.set_data_value("product//extension_attributes", extension_attributes)

        return True
