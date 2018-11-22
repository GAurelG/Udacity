#!/usr/bin/env python
# -*- coding: utf-8 -*-

# In this part, we audit the street names and phones numbers. Function used to
# audit both are separated, they share common parts, but for the clarity of
# presentation I choose to separate them.
#
# Street audit:
# In France, the street category name ("avenue"...) is the first word found in 
# the street name. We created different regular expression to audit the first 
# word, the last one and word that start with one or multiple spaces.
# A typical street name in france could be:
# Rue Marie Curie
# - The first word is the street type (Avenue, Boulevard...)
# - The last word would be the name of the street.
#
# Because street names ar often derived from well known personality, places, 
# flowers... we can also assess the ortograph of the last word in the street
# name.
#
# Phone number audit:
# in France phone numbers are composed of country code, one region number 
# and 8 digits, for example +33 1 12345678.
# people often doesn't write country code (replaces by a '0'), and the can
# group number by 2 or 3 starting from the end, separated by spaces, '.' 
# or '-'. 


import xml.etree.cElementTree as ET
from collections import defaultdict
import re

data = "../Data/paris_france.osm"#sample300_paris_france.osm"
first = "./1_first.txt"
first_2 = "./2_first.txt"
last = "./1_last.txt"
last_2 = "./2_last.txt"

first_word_re = re.compile(r'^\S+', re.IGNORECASE)
last_word_re = re.compile(r'\S+$', re.IGNORECASE) 
space_start_re = re.compile(r'^\s.*', re.IGNORECASE) #only one empty tag
two_frst_re = re.compile(r'^\S+\s+\S+', re.IGNORECASE)
last_two_re = re.compile(r'\S+\s+\S+$', re.IGNORECASE)

####### function from the course: #######

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")
    
def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys)#, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 
    
####### Street names Auditing function #######
    
## example of regular expression used to check street names:

REG1 = re.compile(r'[=\+/&<>;"\?%#$@\,\.\t\r\n]')
REG2 = re.compile(r'["-]')
REG3 = re.compile(r'jardins?')
REG4 = re.compile(r'zones?')
REG5 = re.compile(r'[\s.,_-]$')
REG6 = re.compile(r' - ')
REG7 = re.compile(r'epine')
REG8 = re.compile(r'z ?i')
REG9 = re.compile(r'rc ')
REG10 = re.compile(r'^a\d?')

## One regular expression used to check names starting with "n" or "rn"
## optionnally followed by a digit.
REG = re.compile(r'^r?n\d?')


def find_in_name(street_name, group = "t", reg = REG):
    """return names matching the regular expression (reg should be a compiled 
    regular expression). group parameters tells if we  should return the group
    matched (=g) or the overall street name (= "t"). """
    m = reg.search(street_name)
    if m and group == "g":
        return m.group()
    elif m and group == "t":
        return street_name
    else:
        return None


def street_audit2(data_xml, word_n = 't'):
    """Takes an open file as input and print the dict listing the word found 
    and the number of street processed"""
    total = 0
    street_types = defaultdict(int)
    context = ET.iterparse(data_xml, events=('start',))
    _, root = next(context)
    for event, element in context:
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                   # name = tag.attrib['v'].lower()
                    name = find_in_name(tag.attrib['v'].lower(), word_n)
                #    name = " ".join(name1[1:])
                    #print name1
                    if name:
                        total += 1
                        street_types[name] += 1
        root.clear()
    print_sorted_dict(street_types)
    print total

####### phones number Auditing function #######

# regular expressions to look for 'phone' string in tags
PHONE = re.compile(r'phone')

# regular expression to match strange input in phone number
PHONE1 = re.compile(r'[^\d\. +]')

# regular expressions used in the auditing of phones numbers
# see report for context in the use of theses expressions
POR2 = re.compile(r'((?:\d\s?){9}$)')
POR3 = re.compile(r'((?:\d\s?|\d\.){9}$)')

# regular expression matching phones numbers without the 
# country code. It matches phone number with numbers grouped
# and separated by space, '.' or '-' which correspond to the
# majority of phone writting style found in France. 
POR4 = re.compile(r'((?:\d\s?|\d\.|\d-){9}$)')

def find_phonenumb(elem, reg=POR4):
    """match a string against expression defining phone number
    variables:
        - elem: XML element
        - reg: regular expression to match phone number
    output:
        - matching string if found
        - False if nothing found"""
        
    n = reg.findall(elem.attrib['v'])
    m = reg.search(elem.attrib['v'])
    if n:
        if "-" in elem.attrib['v']:
            print n
        return n
    else:
        return False

def is_phone_nb(elem, reg=PHONE):
    """match 'phone' in an element attrib"""
    m = reg.search(elem.attrib['k'])
    if m:
        return True
    else:
        return False
       
def is_stphon(elem, reg=PHONE1):
    """match element different from the standard phones numbers"""
    m = reg.search(elem.attrib['v'])
    if m:
        return elem.attrib['v']

def phone_audit(data_xml):
    """audit phone number, print sorted dict of phone number matching 
       define regular expression"""
    total = 0
    phone_numb_tags = defaultdict(int)
    context = ET.iterparse(data_xml, events=('start',))
    _, root = next(context)
    for event, element in context:
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if is_phone_nb(tag):
                    number = find_phonenumb(tag)
                    strange = is_stphon(tag)
                    if number:
                        total += 1
                        #print number
                    tags = strange #tag.attrib['k']
                    #print strange
                    phone_numb_tags[tags] += 1
                    #total += 1
        root.clear()
    print_sorted_dict(phone_numb_tags)
    print total
    return None

if __name__ == '__main__':
    data_xml = open(data)
    #street_audit2(data_xml, "t")
    phone_audit(data_xml)
    data_xml.close()







