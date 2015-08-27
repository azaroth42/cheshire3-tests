
import struct
try:
    import bsddb3 as bdb
except:
    import bsddb as bdb

from argparse import ArgumentParser
from cheshire3.utils import SimpleBitfield
import sys

def unpack_proximity(data):
    fmt = '<' + 'l' * (len(data) / args.longStructSize)
    flat = struct.unpack(fmt, data)

    info = {
        'termid': flat[0],
        'recs': flat[1],
        'occs': flat[2],
        'reclist': []
    }

    idx = 3
    while idx < len(flat):
        doc = list(flat[idx:idx + 3])
        nidx = idx + 3 + (doc[2] * args.nProxInts)
        prox = list(flat[idx + 3:nidx])
        idx = nidx
        proxs = []
        for x in range(0,len(prox),args.nProxInts):
            proxs.append('|'.join([str(p) for p in prox[x:x+args.nProxInts]]))
        docstr = "{0}/{1}/{2} ({3})".format(doc[0], doc[1], doc[2], ' '.join(proxs))
        info['reclist'].append(docstr)
    return info


def unpack_simple(data):
    fmt = '<' + 'lll' * (len(data) / (3 * args.longStructSize))
    docs = struct.unpack(fmt, data)
    reclist = []
    for x in range(3, len(docs)/3, 3):
        reclist.append("{0}/{1}/{2}".format(str(docs[x]), str(docs[x+1]), str(docs[x+2])))
    info = {
        'termid': docs[0],
        'recs': docs[1],
        'occs': docs[2],
        'reclist': reclist
    }
    return info


def unpack_bitmap(data):
    lsize = 3 * args.longStructSize
    longs = data[:lsize]
    terms = list(struct.unpack('<lll', longs))
    if len(data) > lsize:
        bf = SimpleBitfield(data[lsize:])
        reclist = ["{0}/0/1".format(x) for x in bf.trueItems()]

    info = {
        'termid': docs[0],
        'recs': docs[1],
        'occs': docs[2],
        'reclist': reclist
    }  
    return info


typeFnHash = {
    'SimpleIndex': unpack_simple,
    'ProximityIndex': unpack_proximity,
    'BitmapIndex': unpack_bitmap
}


ap = ArgumentParser()

ap.add_argument('-t', '--type', type=str, action='store', dest='type', 
    default='SimpleIndex', choices=typeFnHash.keys())
ap.add_argument('-lss', '--longStructSize', type=int, action='store', 
    dest='longStructSize', default=struct.calcsize('<l'))
ap.add_argument('-l', '--limit', type=int, action='store',
    dest='limit', default=1000)
ap.add_argument('-s', '--start', type=str, action='store',
    dest='start', default=None)
ap.add_argument('-n', '--nProxInts', type=int,action='store',
    dest='nProxInts', default=3)
ap.add_argument('-f', '--filename', type=str, action='store', dest='filename')


if sys.argv[0].endswith('catindex.py'):
    argv = sys.argv[1:]
else:
    argv = sys.argv

if sys.argv is None:
    args = ap.parse_args()
else:
    args = ap.parse_args(argv)  


try:
    cxn = bdb.db.DB()
    cxn.open(args.filename)
except:
    print "Could not open '{0}', is it really a Cheshire3 BerkeleyDB index?".format(args.filename)
    sys.exit(1)

try:
    cursor = cxn.cursor()
    if args.start:
        cursor.set_range(args.start)
        (term, val) = cursor.next()
    else:
        (term, val) = cursor.first()
except:
    print "Could not create a cursor into the data at that point"
    cxn.close()
    sys.exit(1)


print "# Index: {0}".format(args.filename)
print ""
if args.type == "SimpleIndex":
    print "Record structure is _recordId/recordStoreId/occurences_\n"
elif args.type == "ProximityIndex":
    print "Record structure is _recordId/recordStoreId/occurences (elementId|wordOffset|byteOffset)_\n"
elif args.type == "BitmapIndex":
    print "Record structure is _recordId_\n"

x = 0
while True:
    fn = typeFnHash.get(args.type, None)
    if not fn:
        print "Unknown Index type. Known types are: {0}".format(repr(typeFnHash.keys()))
        cxn.close()
        sys.exit(1)

    info = fn(val)

    print "## \"{0}\"".format(term)
    print " * termid: {0}\n * total records: {1}\n * total occurences: {2}".format(info['termid'], info['recs'], info['occs'])
    print " * records: %s" % ', '.join(info['reclist'])
    print ""
    x += 1
    if x >= args.limit:
        print "_Stopping after {0} terms_".format(args.limit)
        break
    try:
        (term, val) = cursor.next()
    except:
        print "_Stopping at end of index_"
        break

cxn.close()
