import os
import csv
import pprint

import OSGridConverter
from PIL import Image

def main():
    options = parse_options()
    pubs = augment_pubs(filter_pubs(options, read_pubs(options)))

    print("\n".join([format_pub(p) for p in pubs]))
    
    pub_map = PubMap(pubs)
    pub_map.save("Woking.jpg")

def parse_options():
    return None

def read_pubs(options):
    filename = os.path.join(os.path.dirname(__file__), "pubs.csv")
    with open(filename, "r") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        return [dict(zip(header, row)) for row in reader]

def filter_pubs(options, pubs):
    return [p for p in pubs if p["LocalAuthority"].find("Woking") >= 0]

def augment_pubs(pubs):
    for pub in pubs:
        grid = OSGridConverter.latlong2grid(float(pub["Latitude"]), float(pub["Longitude"]))
        pub["Eastings"] = grid.E
        pub["Northings"] = grid.N
    return pubs

def format_pub(pub):
    return "{} ({}, {}) {}".format(pub["Name"], pub["Eastings"], pub["Northings"], pub["OSRef"])

class PubMap:
    def __init__(self, pubs):
        min_easting = min([p["Eastings"] for p in pubs])
        min_northing = min([p["Northings"] for p in pubs])
        max_easting = max([p["Eastings"] for p in pubs])
        max_northing = max([p["Northings"] for p in pubs])

        start_easting = min_easting - min_easting % 5000
        start_northing = min_northing - min_northing % 5000
        end_easting = max_easting - max_easting % 5000 + 4999
        end_northing = max_northing - max_northing % 5000 + 4999

        tiles = []
        self.image = Image.new(
            'RGB',
            (end_easting - start_easting + 1, end_northing - start_northing + 1)
        )
        for northing in range(start_northing, end_northing, 5000):
            for easting in range(start_easting, end_easting, 5000):
                square_origin = str(OSGridConverter.OSGridReference(easting, northing))
                filename = os.path.join(
                    square_origin[0:2],
                    square_origin[0:2] +
                    square_origin[3] +
                    square_origin[9] +
                    (square_origin[10] < "5" and "S" or "N") +
                    (square_origin[4] < "5" and "W" or "E") +
                    ".tif"
                )
                self.image.paste(
                    Image.open(filename).convert('RGB'),
                    (easting - start_easting, end_northing - northing - 4999)
                )

    def save(self, filename):
        self.image.save(filename)

main()
