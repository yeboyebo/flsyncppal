from abc import ABC, abstractmethod

from YBLEGACY import qsatype
from YBUTILS.viewREST import cacheController


class AQSync(ABC):

    table = None
    init_data = None
    data = None
    cursor = None
    children = None
    is_insert = None
    params = None
    skip_record = None

    def __init__(self, table, init_data, params=None):
        self.table = table
        self.init_data = init_data
        self.data = {}
        self.children = []
        self.params = params
        self.skip_record = False

        self.get_data()

        if not self.skip_record:
            self.get_children_data()

    @abstractmethod
    def get_data(self):
        pass

    def get_cursor(self):
        cursor = qsatype.FLSqlCursor(self.table)
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()

        self.is_insert = True

        return cursor

    def dump_to_cursor(self):
        if not self.cursor:
            self.cursor = self.get_cursor()

        for key, value in self.data.items():
            self.cursor.setValueBuffer(key, value)

    def save(self):
        if self.skip_record:
            return

        self.dump_to_cursor()

        pk_name = self.cursor._model._meta.pk.name

        if not self.cursor.commitBuffer():
            error = cacheController.getSessionVariable("ErrorHandler")

            raise NameError("No se pudo guardar el registro {} de la tabla {}. {}".format(self.data[pk_name], self.table, error))

        for child in self.children:
            child.get_parent_data(self.cursor)
            child.save()

    def get_init_value(self, init_key):
        value = self.init_data

        init_keys = init_key.split("//")
        for key in init_keys:
            if key not in value.keys():
                return None
            value = value[key]

        return value

    def set_data_value(self, data_key, value):
        self.data[data_key] = value

    def set_string_value(self, data_key, value, max_characters=255):
        if value is None:
            self.set_data_value(data_key, value)
            return

        self.set_data_value(data_key, self.format_string(value, max_characters=max_characters))

    def set_data_relation(self, data_key, init_key, default=None):
        value = self.get_init_value(init_key)

        if value is None and default is not None:
            value = default

        self.set_data_value(data_key, value)

    def set_string_relation(self, data_key, init_key, max_characters=255, default=None):
        value = self.get_init_value(init_key)

        if (value is None or value == "") and default is not None:
            value = default

        self.set_string_value(data_key, value, max_characters=max_characters)

    def format_string(self, string, max_characters=255):
        if string is None or not string or string == "":
            return string

        string = str(string)
        string = string.replace("'", " ")
        string = string.replace("º", " ")
        string = string.replace("/", " ")
        string = string.replace("\\", " ")
        string = string.replace("\"", " ")
        string = string.replace("\n", " ")
        string = string.replace("\r", " ")
        string = string.replace("\t", " ")

        return string[:max_characters]

    def get_children_data(self):
        return

    def get_parent_data(self, cursor):
        return
