# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration flsyncppal #
class flsyncppal(interna):

    def flsyncppal_get_customer(self):
        return "flsyncppal"

    def flsyncppal_log(self, text, process):
        tmstmp = qsatype.Date().now()
        tsDel = qsatype.FLUtil.addDays(tmstmp, -5)

        customer = self.get_customer()

        qsatype.FLSqlQuery().execSql("DELETE FROM yb_log WHERE timestamp < '{}'".format(tsDel), "yeboyebo")

        qsatype.FLSqlQuery().execSql("INSERT INTO yb_log (texto, cliente, tipo, timestamp) VALUES ('{}', '{}', '{}', '{}')".format(text, customer, process, tmstmp), "yeboyebo")

    def flsyncppal_replace(self, string):
        if string is None or not string or string == "":
            return string
        string = string.replace("'", " ")
        string = string.replace("º", " ")
        string = string.replace("/", " ")
        string = string.replace("\\", " ")
        string = string.replace("\"", " ")
        string = string.replace("\n", " ")
        string = string.replace("\r", " ")
        string = string.replace("\t", " ")
        return string[:255]

    def __init__(self, context=None):
        super().__init__(context)

    def get_customer(self):
        return self.ctx.flsyncppal_get_customer()

    def log(self, text, process):
        return self.ctx.flsyncppal_log(text, process)

    def replace(self, string):
        return self.ctx.flsyncppal_replace(string)


# @class_declaration head #
class head(flsyncppal):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration ifaceCtx #
class ifaceCtx(head):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration FormInternalObj #
class FormInternalObj(qsatype.FormDBWidget):
    def _class_init(self):
        self.iface = ifaceCtx(self)


form = FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
iface = form.iface
