
from cheshire3.transformer import LxmlOffsetQueryTermHighlightingTransformer
from cheshire3.document import StringDocument
from lxml import etree

class PlusTransformer(LxmlOffsetQueryTermHighlightingTransformer):

    _possibleSettings = {
        'extraWords': {
        	'type': int,
            'docs': ("A string representing the template for the output "
                     "Document with place-holders for selected data items.")
        }
    }

    def process_record(self, session, rec):
        recDom = rec.get_dom(session)
        if (
            (rec.resultSetItem is not None) and
            (rec.resultSetItem.proxInfo is not None) and
            (len(rec.resultSetItem.proxInfo) > 0)
        ):


            # Grab ProxInfo
            proxInfo = rec.resultSetItem.proxInfo
            proxInfo.reverse()

            # Walk the record tree and make xpaths for each element
            xps = {}
            tree = recDom.getroottree()
            walker = recDom.getiterator()
            for x, n in enumerate(walker):
                if n.tag in self.breakElements:
                    break
                if x in nodeIdxs:
                    xps[x] = tree.getpath(n)
            xpathfn = recDom.xpath



            for pi in proxInfo:
                if len(pi) > 1:
                    # adjacency match
                                        

                try:
                    xp = xps[ni]
                except KeyError:
                    # No XPath
                    continue
                el = xpathfn(xp)[0]
                located = None
                for ci, c in enumerate(el.iter()):
                    # Ignore comments processing instructions etc.
                    if c.text:
                        text = c.text
                        if len(c.text) > offset:
                            start = offset
                            try:
                                end = self.wordRe.search(text, start).end()
                            except:
                                # Well I still...
                                # haven't found...
                                # what I'm looking for!
                                pass
                            else:
                                located = 'text'
                                if not (c.tag == self.highlightTag):
                                    hel = self._insertHighlightElement(c,
                                                                       located,
                                                                       start,
                                                                       end)
                                    try:
                                        c.insert(0, hel)
                                    except TypeError:
                                        # Immutable element (?)
                                        break
                                break
                        else:
                            # Adjust offset accordingly
                            offset -= len(text)
                    if c != el and c.tail and located is None:
                        text = c.tail
                        if len(c.tail) > offset:
                            start = offset
                            try:
                                end = self.wordRe.search(text, start).end()
                            except:
                                # Well I still...
                                # haven't found...
                                # what I'm looking for!
                                pass
                            else:
                                if end == -1:
                                    end = len(text)
                                located = 'tail'
                                if not (c.tag == self.highlightTag):
                                    hel = self._insertHighlightElement(c,
                                                                       located,
                                                                       start,
                                                                       end)
                                    p = c.getparent()
                                    try:
                                        p.insert(p.index(c) + 1, hel)
                                    except TypeError:
                                        # Immutable element (?)
                                        break
                                break
                        else:
                            # Adjust offset accordingly
                            offset -= len(text)
        return StringDocument(etree.tostring(recDom))