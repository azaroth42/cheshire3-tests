#!/bin/env python

import os
import sys

import cheshire3
from cheshire3.baseObjects import Session
from cheshire3.server import SimpleServer
from cheshire3.internal import cheshire3Root

# Launch a Cheshire session
session = Session()
serverConfig = os.path.join(cheshire3Root, 'configs', 'serverConfig.xml')
serv = SimpleServer(session, serverConfig)


# Grab our objects
db = serv.get_object(session, 'db_test_query_highlight')
recStore = db.get_object(session, 'recordStore')
qfac = db.get_object(session, 'defaultQueryFactory')

q = qfac.get_query(session, "cql.anywhere = \"e f g\"")
rs = db.search(session, q)

# rs[0].proxInfo = [[[1, 4, 8, 7], [1, 5, 10, 8], [1, 6, 12, 9]]]
# being element 1,1,1 /  wordoffset 4,5,6  / byteoffset 8,10,12 / termid 7,8,9

rec = rs[0].fetch_record(session)

loqth = db.get_object(session, 'LOQTHTransformer')
doc = loqth.process_record(session, rec)
print doc.get_raw(session)

pt = db.get_object(session, 'PlusTransformer')
doc = pt.process_record(session, rec)