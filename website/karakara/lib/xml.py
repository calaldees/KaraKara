

#-------------------------------------------------------------------------------
# Python Dictionary to XML
#-------------------------------------------------------------------------------

from xml.etree.ElementTree import Element, tostring

def dictToXMLString(d):

    def dictToElement(d, tag):
        e = Element(tag)
        if isinstance(d, str): # is String
            e.text = d
        elif type(d) in [int, float, bool]:
            e.text = str(d)
        elif hasattr(d,'keys'): # is Dict
            for key in d.keys():
                e.append(dictToElement(d[key], key))
        elif hasattr(d, '__iter__'): # is List
            for i in d:
                e.append(dictToElement(i, 'item'))
        return e
        
    return tostring(dictToElement(d, 'root'), encoding="utf-8")
