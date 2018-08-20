from jumpscale import j

schema = """
@url = despiegk.test
@name = TestObj
llist2 = "" (LS) #L means = list, S=String        
nr = 4
date_start = 0 (D)
description = ""
token_price = "10 USD" (N)
cost_estimate:hw_cost = 0.0 #this is a comment
llist = []
llist3 = "1,2,3" (LF)
llist4 = "1,2,3" (L)
llist5 = "1,2,3" (LI)
U = 0.0
#pool_type = "managed,unmanaged" (E)  #NOT DONE FOR NOW
"""

s = j.data.schema.schema_from_text(schema)
print(s)

o = s.get()

o.llist.append(1)
o.llist2.append("yes")
o.llist2.append("no")
o.llist3.append(1.2)
o.llist4.append(1)
o.llist5.append(1)
o.llist5.append(2)
o.U = 1.1
o.nr = 1
o.token_price = "10 EUR"
o.description = "something"


import bpython;bpython.embed(locals(), banner='test1')