from Jumpscale import j
#GENERATED CODE CAN CHANGE

SCHEMA="""

@url = threefold.grid.node

node_zos_id* = ""               #zero os id of the host
node_zerotier_id* = ""          #zerotier id
node_public_ip = ""             #node public ip address

description = ""

macaddresses = [] (LS)          #list of macaddresses found of this node

noderobot* = (B)                #could access the node robot (did answer)
noderobot_up_last* = (D)        #last time that the noderobot was up (last check)
noderobot_ipaddr* = ""          #ipaddress where to contact the noderobot

sysadmin* = (B)                 #is accessible over sysadmin network for support?
sysadmin_up_ping* = (B)         #ping worked over sysadmin zerotier
sysadmin_up_zos* = (B)          #zeroos was reachable (over redis for support = sysadmin
sysadmin_up_last* = (D)         #last time that this node was up on sysadmin network
sysadmin_ipaddr* = ""           #ipaddress on sysadmin network

tfdir_found* = (B)              #have found the reservation in the threefold dir
tfdir_up_last* = (D)            #date of last time the node was updated in the threefold dir

tfgrid_up_ping* = (B)           #ping worked on zerotier public network for the TF Grid
tfgrid_up_last* = 0 (D)         #last date that we saw this node to be up (accessible over ping on pub zerotier net)

state* = ""                     #OK, ERROR, INIT

error = ""                      #there is an error on this node

farmer_id* = (I)
farmer* = false (B)
update* = (D)

capacity_reserved = (O) !threefold.grid.capacity.reserved
capacity_used = (O) !threefold.grid.capacity.used
capacity_total = (O) !threefold.grid.capacity.total
location = (O) !threefold.grid.capacity.location


@url = threefold.grid.capacity.reserved
mru = 0 (F)            #nr of units reserved
cru = 0 (F)
hru = 0 (F)
sru = 0 (F)

@url = threefold.grid.capacity.used
mru = 0 (F)            #nr of units used in the box
cru = 0 (F)
hru = 0 (F)
sru = 0 (F)

@url = threefold.grid.capacity.total
mru = 0 (F)            #nr of units total in the box
cru = 0 (F)
hru = 0 (F)
sru = 0 (F)


@url = threefold.grid.capacity.location
country = ""
city = ""
continent = ""
latitude = (F)
longitude = (F)


"""


bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)
Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema,__file__)
MODEL_CLASS = bcdb._BCDBModelClass_get()


class threefold_grid_node(Index_CLASS,MODEL_CLASS):
    def __init__(self):
        MODEL_CLASS.__init__(self, bcdb=bcdb,schema=schema)
        self.write_once = False
        self._init()