#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Please note that the function 'make_request' is provided for your reference only.
You will not be able to to actually use it from within the Udacity web UI.
All your changes should be in the 'extract_carrier' function.
Also note that the html file is a stripped down version of what is actually on
the website.

Your task in this exercise is to get a list of all airlines. Exclude all of the
combination values like "All U.S. Carriers" from the data that you return.
You should return a list of codes for the carriers.
"""

from bs4 import BeautifulSoup
html_page = "../Data/options.html"


def extract_carriers(page):
    data = []

    with open(page, "r") as html:
        # do something here to find the necessary values
        soup = BeautifulSoup(html, "lxml")
        carrier_list = soup.find(id="CarrierList")
        for option in carrier_list.find_all('option'):
            if option["value"] not in ["All", "AllUS", "AllForeign"]:
                data.append(option["value"])
               # print option["value"]

    return data

def extract_airports(page):
    data = []
    with open(page, "r") as html:
        soup = BeautifulSoup(html, "lxml")
        airport = soup.find(id="AirportList")
        for air in airport.find_all("option"):
            if air["value"] not in ["All", "AllMajors", "AllOthers"]:
                data.append(air["value"])
                #print air["value"]
    return data

def make_request(data):
    eventvalidation = data["eventvalidation"]
    viewstate = data["viewstate"]
    airport = data["airport"]
    carrier = data["carrier"]

    r = requests.post("http://www.transtats.bts.gov/Data_Elements.aspx?Data=2",
                    data={'AirportList': airport,
                          'CarrierList': carrier,
                          'Submit': 'Submit',
                          "__EVENTTARGET": "",
                          "__EVENTARGUMENT": "",
                          "__EVENTVALIDATION": eventvalidation,
                          "__VIEWSTATE": viewstate
                    })

    return r.text


def test():
    data = extract_carriers(html_page)
    assert len(data) == 15
    assert "G4" in data
    assert "NK" in data
    data = extract_airports(html_page)
    assert len(data) == 15
    assert "ATL" in data
    assert "ABR" in data

test()
