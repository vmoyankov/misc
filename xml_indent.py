#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrettyPrint XML

Usage:

    dom = ET.parse(file)
    process(dom)
    indent(dom)
    dom.write()

"""

from xml.etree import ElementTree as ET

def indent(elem, level=0, ind="  "):
    i = "\n" + level * ind
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + ind
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        # last element is special!
        for elem in elem:
            indent(elem, level+1, ind)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if not level:
            return
        if not elem.text or not elem.text.strip():
            elem.text = None
        if not elem.tail or not elem.tail.strip():
            elem.tail = i

if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        if f == '-':
            f = sys.stdin
        dom = ET.parse(f)
        indent(dom.getroot(), ind="    ")
        dom.write(sys.stdout, encoding='unicode')
