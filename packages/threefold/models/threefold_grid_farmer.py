from Jumpscale import j
#GENERATED CODE CAN CHANGE

SCHEMA="""

@url = threefold.grid.farmer
name* = ""
description = ""
error = ""
iyo_org* = ""
wallets = (LS)
emailaddr = (LS)
mobile = (LS)
pubkeys = "" (S)


"""


bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)
Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema,__file__)
MODEL_CLASS = bcdb._BCDBModelClass_get()


class threefold_grid_farmer(Index_CLASS,MODEL_CLASS):
    def __init__(self):
        MODEL_CLASS.__init__(self, bcdb=bcdb,schema=schema)
        self.write_once = False
        self._init()