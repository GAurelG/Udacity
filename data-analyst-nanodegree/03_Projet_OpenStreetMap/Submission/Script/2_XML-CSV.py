#!/usr/bin/env python2 
# -*- coding: utf-8 -*-

# In this part we read through the XML File, clean street names as described
# in the audit phase, and insert the results in csv files to later inmport in 
# the database.
# Some function are duplicate from the audit part (the street_name function) 
# to have each part of the process independant from the others and facilitate
# reading and correction. 
#
# Some functions where taken from the Udacity exercices. they are:
# - get_element()
# - validat_element()
# - the UnicodeDictWriter class and the associated functions
# These functions are in a cleary delimited section.
#
# The process_map() function is partially similar to the one from the course,
# the main difference is the separation of the test function.
# - process_map()
#
# The file is divided in 5 sections:
# - Shapping element Functions
# - Audit and update street names
# - Test Functions
# - Helper Functions/from Course
# - Main Function

# ================================================== #
#               Global informations/variables        #
# ================================================== #

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
from collections import defaultdict
import cerberus
import Schema
import ast
from unicodedata import normalize

SCHEMA = Schema.schema
#### File locations ####

OSM_PATH = "../Data/sample500_paris_france.osm"
NODES_PATH = "../Data/0_nodes.csv"
NODE_TAGS_PATH = "../Data/0_nodes_tags.csv"
WAYS_PATH = "../Data/0_ways.csv"
WAY_NODES_PATH = "../Data/0_ways_nodes.csv"
WAY_TAGS_PATH = "../Data/0_ways_tags.csv"

#### correction files ####

STREET_MAP = "../Data/1_street.map"
IGNORE = "../Data/3_ignore.map"
END_NAME = "../Data/4_end_names.map"

#### Regular expressions compiler ####

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\'"\,\. \t\r\n]')
PHONE = re.compile(r'phone')
PHONNB = re.compile(r'((?:\d\s?|\d\.|\d-){9}$)')


#### Fields for the CSV files, it should match the SQL tables ####

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version',
               'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']



# ================================================== #
#               Shapping element Functions           #
# ================================================== #

def shape_element(element, node_attr_fields=NODE_FIELDS, 
                  ways_attr_fields=WAY_FIELDS, default_tag_type='regular'):
    """return cleaned, corrected and shaped node or way XML element as Python
       dict.
       
    variables:
        - element: element of an XML file
        - node_attr_fields: list of fields for the node dict ~ name of the 
                            columns in the node CSV output
        - ways_attr_fields: list of fields for the way dict ~ name of the 
                            columns in the way CSV output
        - default_tag_type: string or any other element descripting the 
                            default tag type
     
     output:
         - if element inputed is a 'node' tag: output a dictionary of the 
              node and its associated tags
         - if the input element is a 'way' tag, output a dictionary of ways,
              its associated tags and its associated nodes"""
              
    node_attribs = {}
    way_attribs = {}
    way_nodes = {}
    tags = []
    if element.tag == 'node':
        node_attribs= wn_shape(element, node_attr_fields)
        tags, _ = sub_tag_shape(element, node_attribs['id'])
        try:
            node_attribs['uid']
            node_attribs['changeset']
            node_attribs['timestamp']
            node_attribs['lon']
            node_attribs['version']
            node_attribs['lat']
            node_attribs['id']
            node_attribs['user']
            return {'node': node_attribs, 'node_tags': tags}
        except:
            return None
    elif element.tag == 'way':
        way_attribs = wn_shape(element, ways_attr_fields)
        tags, way_nodes = sub_tag_shape(element, way_attribs['id'], True)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


def wn_shape(element, attrib_fields):
    """return a dict either way or node attrib dict depending on the inputed
    element.
    
    variable:
        - element: XML element
        - attrib_fields: list of fields for the node or way dictionary 
                         to output
            
    output:
        - dictionary of the way or node element informations"""
    attribs = {}
    for key, value in element.attrib.items():
        if key in attrib_fields:
            attribs[key] = value
    return attribs


def sub_tag_shape(element, attrib_ID, way=False):
    """return a list of dict for node and way subtags.
    
    variables:
        - element: an XML element
        - attrib_ID: The ID of the way or node parent tag
        - way: Boolean, makes the function format the tag as a way 
               or node subtag
    
    output:
        - tuple of tags and way nodes informations in the case of a
          way subtag"""
    tags = []
    way_nodes = []
    for child in element:
        if child.tag == 'tag':
            dict_tag = sub_tag(child, attrib_ID)
            if dict_tag != None:
                tags.append(dict_tag)
        elif child.tag == 'nd' and way:
            position = len(way_nodes)
            node_id = child.attrib['ref']
            way_id = attrib_ID
            way_nodes.append({'id' : way_id, 'node_id' : node_id, 
                              'position' : position})
    return (tags, way_nodes)


def sub_tag(child, tag_id,  problem_chars=PROBLEMCHARS,
                             lower_colon = LOWER_COLON):
    """create the sub tag element and correct the name if it is a
    street name or phone number.
    
    variable:
        - child: XML element
        - tag_id: ID from the parent tag
        - problem_chars: regular expression defining characters making 
                         the tag not formatable.
                         If a match is found, return: None
        - lower colon: regular expression searching for tag with 'k' attrib
                       containing a two part value 
                       (~ expression containing ':')
     
    output:
        - None if bad value are found in the tag or tag is missing fields
        - dictionary of the sub_tag attribute with value corrected if the 
          value is a street name or a phone number"""
          
    is_street = False
    tag_dict = { "id" : tag_id, "type" : "regular"}
    for key, value in child.attrib.items():
        if key == 'k':
            bad_char = problem_chars.search(value)
            if bad_char:
                return None
            colon = lower_colon.search(value)
            if value == "addr:street":
                is_street = True
            if colon:
                tag_dict['key'] = value.split(":", 1)[1]
                tag_dict['type'] = value.split(":")[0]
            else:
                tag_dict['key'] = value
        elif key == 'v' and is_street:
           tag_dict['value'] = check_name(value) 
        elif is_phone_nb(child) and key == 'v':
            tag_dict['value'] = check_phone(value)
        elif key == 'v':
            tag_dict['value'] = value
    if tag_dict['value'] == None:
        return None
    else:
        return tag_dict

# ================================================== #
#               Audit and update street names        #
# ================================================== #

#### dictionary of the wrongly written street names and their good mapping ####

def mapping_in(file1 = STREET_MAP, file2 = IGNORE, file3 = END_NAME):
    """import the dictionary of the wrongly written street names from the
    file.
    variables:
        - file1, file2, file3: location of the file to open and import 
                               into dictionary
                               
    output: 3 dictionary corresponding to the inputed files"""
    
    with codecs.open(file1, 'r') as st_map, \
         codecs.open(file2, 'r') as ign, \
         codecs.open(file3, 'r') as end_nm:
             streetmap = ast.literal_eval(st_map.read()) 
             ignore = ast.literal_eval(ign.read())
             end_correct = ast.literal_eval(end_nm.read())
    return streetmap, ignore, end_correct

def check_name(name):
    """check the street name and return the street name, corrected
    if necessary.
    variable:
        - name: string
    output:
        - string if the name is correct or has been corrected
        - None if the name can't be corrected"""
        
    streetmap, ignore, end_correct = mapping_in()
    name = name.lower()
    if name not in ignore:
        street =  name.split(" ", 1)
        if street[0] in streetmap.keys():
            street[0] = streetmap[street[0]]

        if street[0] == u"rond":
            stnd = street[1].split(" ", 1)
            if stnd[0] == u"point":
                street[0] = u"rond-point"
                street[1] = stnd[1]

        if street[0] in [u"centre", u"c"]:
            #when "centre" and "commercial" are separated,
            #change them to "c.cial"
            stnd = street[1].split(" ", 1)
            if stnd[0] in [u"cial", u"commercial"]:
                street[0] = u"c.cial"
                street[1] = stnd[1]

        if street[0] == u"zone":
            #when zone industrielle/activité/artisanale commerciale
            # are written in plain text, change them to zi/za/zac
            stnd = street[1].split(" ", 1)
            if stnd[0] == u"industrielle":
                street[0] = u"zi"
                street[1] = stnd[1]
            elif stnd[0] == u"activite":
                street[0] = u"za"
                street[1] = stnd[1]
            elif stnd[0] == u"artisanale":
                street[0] = u"zac"
                street[1] = stnd[1]
                
        try:
            if street[1] and street[1] in end_correct.keys():
                street[1] = end_correct[street[1]]
        except:
            pass
        name = " ".join(street)
    else:
        name = None
    return name 

# ================================================== #
#           Audit and update phones numbers          #
# ================================================== #


def is_phone_nb(elem, reg=PHONE):
    """look in an XML element to see if the 'k' attribute contain the 
       string 'phone'.
       variable:
           - elem: XML element
           - reg: regular expression
       output:
           - boolean, True if match found else False """
           
    m = reg.search(elem.attrib['k'])
    if m:
        return True
    else:
        return False

def check_phone(value, reg=PHONNB):
    """take a string as input and correct it if it looks like a phone
       number.
       variable:
           - value: a string
           - reg: regular expression to find the phone number
       output:
           - value corrected if it looked like a phone number
           - value uncorrected if it doesn't look like a phone number
           """         
    numb = reg.search(value)
    if numb:
        group = numb.group()
        if '.' in value:
            group = ''.join(group.split('.')) 
        if '-' in value:
            group = ''.join(group.split('-'))
        group = ''.join(group.split(' '))
        group = '+33' + group
        return group
    else:
        return value

# ================================================== #
#               Test Functions                       #
# ================================================== #

def test_shape(file_in, tags=('node', 'way')):
    """validate the output of the shape_element() function against the
    specified schema."""
    validator = cerberus.Validator()
    i = 0
    pourc = 220864
    pr = 0
    j = 0
    k = 0
    for element in get_element(file_in, tags):
        
        el = shape_element(element)
        if el:
            validate_element(el, validator)
        k = i - j
        if i%10000 == 0:
            print i
        if k == pourc:
            j = i
            pr += 1
            print "pourcentage done: ", pr
        i += 1 
    return "no formating error found, validation passed!"


def test_check(bad_names, crt_names):
    """test the check_name function, take two list in:
    bad_names: list of example of badly formated names
    crt_names: list of the matching good names"""
    names = zip(bad_names, crt_names)
    for name in names:
        better_name = check_name(name[0])
        print name[0], "=>", better_name
        assert better_name == name[1]
    return "test of check_name function done"

def test_shape_success(file_in):
    """run the check function to see if it finishes or raise an error"""
    for element in get_element(file_in, tags=('node', 'way')):
        shape_element(element)
    return 'Shape has been done, now check against cerberus validator'



# ================================================== #
#               Helper Functions/from Course         #
# ================================================== #

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag
    variables:
        - osm_file: string of the file path
        - tags: tuple of tags to yield"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema
    variable:
        - element: an XML element
        - validator: a validator from Cerberus library
        - schema: a schema to validate against"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #

#changes were made to the function to match the separation with the
#test functions.

def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)
       variable:
           - file_in: a filepath
       output:
           - 'Done!' when XML file has been parsed and CSV files 
                     where written"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        i = 0
        nb_nd = 0
        nb_w = 0

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                    nb_nd += 1
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
                    nb_w += 1
            i += 1
            if i%10000 == 0:
                print i
        print "number of node written = ", nb_nd
        print "number of way written = ", nb_w
        return 'Done!'


if __name__ == '__main__':
    #process_map(OSM_PATH)
    print "script disabled, uncomment previous line (488)"
    #test_shape_success(OSM_PATH)
    #test_shape(OSM_PATH)

