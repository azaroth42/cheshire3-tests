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
db = serv.get_object(session, 'db_test_pgsql')
recStore = db.get_object(session, 'recordStore')
rssStore = db.get_object(session, 'resultSetStore')
qfac = db.get_object(session, 'defaultQueryFactory')

# Prove that we have some records in postgres

rec = recStore.fetch_record(session, 0)
if not rec:
	print "Could not retrieve records, have you run cheshire3-load?"
	sys.exit()

# Make a query, and store results in resultSetStore
try:
	qidx = sys.argv.index('--query')
except:
	qidx = -1
if qidx > -1:
	try:
		term = sys.argv[qidx+1]
	except:
		term = "a"
	q = qfac.get_query(session, "cql.anywhere = \"%s\"" % term)
	rs = db.search(session, q)
	rsid = rssStore.create_resultSet(session, rs)
	print "Searched for: %s" % term
	print "Number of hits stored: %s" % len(rs)
	print "ResultSetId: %s" % rsid

# Retrieve ResultSet from Store
try:
	fidx = sys.argv.index('--fetch')
except:
	fidx = -1
if fidx > -1:
	rssid = sys.argv[fidx+1]
	if rssid.isdigit():
		rssid = int(rssid)
	rs = rssStore.fetch_resultSet(session, rssid)
	print "ResultSet Query Term: %s" % rs.queryTerm
	print "Number of hits from store: %s" % len(rs)


