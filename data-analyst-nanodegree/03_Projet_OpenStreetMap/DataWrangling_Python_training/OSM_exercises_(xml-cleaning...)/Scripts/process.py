"""assume that you combined the code from the previous 2 exercises with code
from the lesson on how to build requests, and downloaded all the data locally.
The files are in a directory "data", named after the carrier and airport:
"{}-{}.html".format(carrier, airport), for example "FL-ATL.html".

The table with flight info has a table class="dataTDRight". Your task is to
extract the flight data from that table as a list of dictionaries, each
dictionary containing relevant data from the file and table row. This is an
example of the data structure you should return:

data = [{"courier": "FL",
        "airport": "ATL",
        "year": 2012,
        "month": 12,
        "flights": {"domestic": 100,
        "international": 100}
        },
        {"courier": "..."}
]   

Note - year, month, and the flight data should be integers.
You should skip the rows that contain the TOTAL data for a year.

There are couple of helper functions to deal with the data files.
Please do not change them for grading purposes.
All your changes should be in the 'process_file' function.
"""
from bs4 import BeautifulSoup
from zipfile import ZipFile
import os
datadir = "../Data"
filedir = "FL-ATL.html"

def open_zip(datadir):
    with ZipFile('{0}.zip'.format(datadir), 'r') as myzip:
        myzip.extractall()

def process_all(datadir):
    files = os.listdir(datadir)
    return files

def process_file(f):
    """
    This function extracts data from the file given as the function argument in
    a list of dictionaries. This is example of the data structure you should
    return:
    
    data = [{"courier": "FL",
            "airport": "ATL",
            "year": 2012,
            "month": 12,
            "flights": {"domestic": 100,
            "international": 100}
            },
            {"courier": "..."}
    ]

    Note - year, month, and the flight data should be integers.
    You should skip the rows that contain the TOTAL data for a year.
    """
    data = []
    info = {}
    header = ["year", "month", "domestic", "international", "total"]
    info["courier"], info["airport"] = f[:6].split("-")
    # Note: create a new dictionary for each entry in the output data list.
    # If you use the info dictionary defined here each element in the list 
    # will be a reference to the same info dictionary.
    with open("{}/{}".format(datadir, f), "r") as html:
        soup = BeautifulSoup(html, 'lxml')
        all_data = soup.find_all('tr', attrs={'class' : 'dataTDRight'})
        for data1 in all_data:
            topito = {}
            topito["courier"] = info["courier"]
            topito["airport"] = info["airport"]
            topito["flights"] = {}
            for data2, head in zip(data1.find_all('td'),header):
                if head != "total":
                    if head == "domestic" or head == "international":
                        topito["flights"][head] = int(data2.string.replace(',', ''))
                    else:
                        topito[head] = data2.string
            if topito["month"] != "TOTAL":
                topito["month"] = int(topito["month"])
                topito["year"] = int(topito["year"])
                data.append(topito)

    return data

def test():
    print "Running a simple test..."
    open_zip(datadir)
    files = process_all(datadir)
    data = []
    # Test will loop over three data files.
    for f in files:
        data += process_file(f)

    assert len(data) == 399  # Total number of rows
    for entry in data[:3]:
        assert type(entry["year"]) == int
        assert type(entry["month"]) == int
        assert type(entry["flights"]["domestic"]) == int
        assert len(entry["airport"]) == 3
        assert len(entry["courier"]) == 2
        assert data[0]["courier"] == 'FL'
        assert data[0]["month"] == 10
        assert data[-1]["airport"] == "ATL"
        assert data[-1]["flights"] == {'international': 108289, 'domestic': 701425}
    print "... success!"
if __name__ == "__main__":
    process_file(filedir)