#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
"""
Your task is to explore the data a bit more.
The first task is a fun one - find out how many unique users
have contributed to the map in this particular area!

The function process_map should return a set of unique user IDs ("uid")
"""

def get_user(element):
    attrib = element.attrib
    try:
        user = attrib['user']
    except KeyError:
        user = None
    return user

def process_map(filename):
    users = set()
    a = None
    for _, element in ET.iterparse(filename):
        a = get_user(element)
        if a != None:
            users.add(a)
            

    return users


def test():

    users = process_map('example.osm')
    pprint.pprint(users)
    assert len(users) == 6



if __name__ == "__main__":
    test()

