#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import clock
import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "../Data/paris_france.osm"  # Replace this with your osm file
SAMPLE_FILE = "../Data/sample500_paris_france_list.osm"

k = 500 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
            
            
tstart = clock() #start recording time

to_write = []
for i, element in enumerate(get_element(OSM_FILE)):
    if i % k == 0:
        to_write.append(ET.tostring(element, encoding='utf-8'))

intime = clock()

alala = "".join(to_write)
twotime = clock()

with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')
    output.write(alala)
    output.write('</osm>')

tendwrite = clock()
print """generating took %f sec,\nwriting took %f sec,\ntotal time required : %f sec""" % (intime-tstart, tendwrite-twotime, tendwrite-tstart) 

