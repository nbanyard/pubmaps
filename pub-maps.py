import os
import csv
import pprint

import OSGridConverter
from PIL import Image

def main():
    options = parse_options()
    pubs = augment_pubs(filter_pubs(options, read_pubs(options)))
    bounding_box = pub_bounding_box(options, pubs)
    pub_map = PubMap(options, bounding_box)
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

def pub_bounding_box(options, pubs):
    margin = 200
    return (
        min([p["Eastings"] for p in pubs]) - margin,
        min([p["Northings"] for p in pubs]) - margin,
        max([p["Eastings"] for p in pubs]) + margin,
        max([p["Northings"] for p in pubs]) + margin,
        )

class PubMap:
    def __init__(self, options, bounding_box):
        self.width = (297 - 10) * 300 / 25.4
        self.height = (210 - 10) * 300 / 25.4
        self.bounding_box = bounding_box
        self.image = Image.new(
            "RGB",
            (self.width, self.height)
        )
        
    def load_tiles(self):
        tile_eastings = range(self.bounding_box[0] - self.bounding_box[0] % 5000, self.bounding_box[1], 5000)
        tile_northings = range(self.bounding_box[1] - self.bounding_box[1] % 5000, self.bounding_box[3], 5000)
        tile_northings.reverse()


        alltiles = Image.new(
            'RGB',
            (len(tile_eastings) * 5000, len(tile_northings) * 5000)
        )
        
        for across, eastings in enumerate(tile_eastings):
            for down, northings in enumerate(tile_northings):
                alltiles.paste(
                    Image.open(tile_filename(eastings, northings)).convert('RGB'),
                    (across * 5000, down * 5000)
                )
            


    def save(self, filename):
        self.image.save(filename)

        
def tile_filename(eastings, northings);
    square_origin = str(OSGridConverter.OSGridReference(easting, northing))
    return os.path.join(
        square_origin[0:2],
        square_origin[0:2] +
        square_origin[3] +
        square_origin[9] +
        (square_origin[10] < "5" and "S" or "N") +
        (square_origin[4] < "5" and "W" or "E") +
        ".tif"
    )


main()
