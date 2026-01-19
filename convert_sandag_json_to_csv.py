import json
import csv
from dumpDictToCSV import dumpListDictToCSV
from collections import defaultdict

inpath = 'C:/Users/karl/python/switrs/pelias/docker/projects/sandiego-county/data/openaddresses/us/ca/'

with open(inpath + 'SANDAG_Address_Points.geojson') as f:
    data = json.load(f)

addresses = []

for feature in data["features"]:
    props = feature["properties"]
    coords = feature["geometry"]["coordinates"]

    number = str(props.get("ADDRNMBR", ""))

    street_parts = [
        props.get("ADDRPDIR", ""),
        props.get("ADDRNAME", ""),
        props.get("ADDRSFX", ""),
        props.get("ADDRPOSTD", "")
    ]
    street = " ".join(part for part in street_parts if part)

    address = dict()

    address["number"] = number
    address["street"] = street.title()
    address["city"] = props.get("COMMUNITY", "")
    address["region"] = props.get("STATE", "CA")
    address["postcode"] = props.get("ADDRZIP", "")
    address["country"] = "US"
    address["lon"] = float(coords[0])
    address["lat"] = float(coords[1])
    address["khr"] = "pad"

    addresses.append(address)

header = ["number","street","city","region","postcode","country","lon","lat", "khr"]

# dumpListDictToCSV(addresses, inpath + 'openaddresses_sandiego_3.csv', ',', header)

with open(inpath + 'openaddresses_sandiego_3.csv', "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    for address in addresses:
        # ensure lon and lat are floats (not strings), others as appropriate
        address["lon"] = float(address["lon"])
        address["lat"] = float(address["lat"])
        writer.writerow(address)


