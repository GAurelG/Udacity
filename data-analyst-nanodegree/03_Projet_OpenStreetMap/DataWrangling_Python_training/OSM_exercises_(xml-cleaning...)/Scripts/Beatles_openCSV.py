import os

DATADIR = ""
DATAFILE = "../Data/beatles-1.csv"

def parse_file(datafile):
    data = []
    numb = 0
    header = []
    with open(datafile, "rb") as f:
        for line in f:
            splt = line.split(",")
            splt = map(lambda x: x.replace('\xc2\xa0',''), splt)
            splt = map(lambda x: x.strip(), splt)
            if numb == 0:
               header = splt
               numb += 1

            elif numb < 11:
                line_dict = dict(zip(header, splt))
                numb += 1
                data.append(line_dict)
            else:
                exit
            
    return data


def test():
    # a simple test of your implemetation
    datafile = DATAFILE #os.path.join(DATADIR, DATAFILE)
    d = parse_file(datafile)
    firstline = {'Title': 'Please Please Me', 'UK Chart Position': '1', 'Label': 'Parlophone(UK)', 'Released': '22 March 1963', 'US Chart Position': '-', 'RIAA Certification': 'Platinum', 'BPI Certification': 'Gold'}
    tenthline = {'Title': '', 'UK Chart Position': '1', 'Label': 'Parlophone(UK)', 'Released': '10 July 1964', 'US Chart Position': '-', 'RIAA Certification': '', 'BPI Certification': 'Gold'}

    assert d[0] == firstline
    assert d[9] == tenthline

test()
