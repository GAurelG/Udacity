#!/usr/bin/env python
# -*- coding: utf-8 -*-
# So, the problem is that the gigantic file is actually not a valid XML, because
# it has several root elements, and XML declarations.
# It is, a matter of fact, a collection of a lot of concatenated XML documents.
# So, one solution would be to split the file into separate documents,
# so that you can process the resulting files as valid XML documents.

import xml.etree.ElementTree as ET
PATENTS = '../Data/patent.data'

def get_root(fname):
    tree = ET.parse(fname)
    return tree.getroot()


def split_file(filename):
    """
    Split the input file into separate files, each containing a single patent.
    As a hint - each patent declaration starts with the same line that was
    causing the error found in the previous exercises.

    The new files should be saved with filename in the following format:
    "{}-{}".format(filename, n) where n is a counter, starting from 0.
    """
    n = 0
    files = []
    ploup = []
    with open(filename, 'r') as oldfile:
        xml_dec = oldfile.readline()
        ploup.append(xml_dec)
        for line in oldfile:
            if line != xml_dec:
                to_ploup = line
                ploup.append(to_ploup)
                
            else:
                files.append(ploup)
                ploup = []
                ploup.append(xml_dec)
                n += 1
        files.append(ploup)
    n = 0
    for fil in files:
        newfilename = "{}-{}".format(filename, n)
        fil_write = "".join(fil)
        with open(newfilename, 'w') as newfile:
            newfile.write(fil_write)
            n += 1
    return '1'

def test():
    split_file(PATENTS)
    for n in range(4):
        try:
            fname = "{}-{}".format(PATENTS, n)
            f = open(fname, "r")
            if not f.readline().startswith("<?xml"):
                print "You have not split the file {} in the correct boundary!".format(fname)
            f.close()
        except:
            print "Could not find file {}. Check if the filename is correct!".format(fname)

test()
