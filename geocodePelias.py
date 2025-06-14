import requests
from geopy.distance import distance
from geopy.point import Point

BEARING = {"N":0, "E":90, "S":180, "W":270}
M2FT = 3.280839895 # convert meters to feet
FT2M = 1.0/M2FT
API_READ_TIMEOUT=20

def pelias_geocode(query):
    url = "http://localhost:4000/v1/search"
    params = {
        "text": query,
    }
    try:
        response = requests.get(url, params=params, timeout=API_READ_TIMEOUT)
        data = response.json()
    except:  # try twice
        response = requests.get(url, params=params, timeout=API_READ_TIMEOUT)
        data = response.json()

    if data["features"]:
        coords = data["features"][0]["geometry"]["coordinates"]
        match_type = data["features"][0]["properties"]["match_type"]
        confidence = data["features"][0]["properties"]["confidence"]
        accuracy = data["features"][0]["properties"]["accuracy"]
        bbox = data["bbox"]

        found = {"status":"OK",
            "lat":coords[1],
            "lon":coords[0],
            "match_type":match_type,
            "confidence":confidence,
            "accuracy":accuracy,
            "bbox":bbox
        }

        return found
    else:
        return {"status":"NO MATCH"}

def move_along_bearing(start_coords, distance_meters, bearing_degrees):
    start_point = Point(start_coords[0], start_coords[1])
    # geopy distance takes km, so convert meters
    dest = distance(meters=distance_meters).destination(point=start_point, bearing=bearing_degrees)
    return (dest.latitude, dest.longitude)

def geocode_pelias(crash):
    # set up Pelias decoder query
    city = crash["City"]
    road1 = crash["Primary Road"]
    road2 = crash["Secondary Road"]
    if len(road2) > 0 and road2 != "NOT STATED":
        intersection = True
    else:
        intersection = False
    dist_ft = crash["Secondary Dist ft"]
    if len(dist_ft) > 0:
        dist_ft = float(dist_ft)
    else:
        dist_ft = 0.0
    direction = crash["Secondary Dir"]
    if len(direction) > 0:
        direction = direction[0:1].upper()
    else:
        direction = "N"
        dist_ft = 0.0

    if intersection:
        query = f"{road1} and {road2}, {city}, CA"
    else:
        query = f"{road1}, {city}, CA"

    # get lat, lon of intersection
    geocoded = pelias_geocode(query)
    if geocoded['status'] == "OK":
        latlon = [ geocoded["lat"], geocoded["lon"] ]

        # move along intersection point
        if dist_ft > 0.0:
            latlon = move_along_bearing(latlon, dist_ft*FT2M, BEARING[direction])
        crash['Latitude'] = str(latlon[0])
        crash['Longitude'] = str(latlon[1])
        crash['GeoSrc'] = "Pelias"
        crash['GeoMatchType'] = geocoded["match_type"]
        crash['GeoConf'] = str(geocoded["confidence"])
        crash['GeoAccuracy'] = geocoded["accuracy"]
        if len(geocoded["bbox"]) > 0 and geocoded["match_type"] != "exact":
            bbox_str = [str(b) for b in geocoded["bbox"]]
            crash['GeoBbox'] = ",".join(bbox_str)
        else:
            crash['GeoBbox'] = ""

    else:
        crash['Latitude'] = geocoded['status']
        crash['Longitude'] = geocoded['status']
        crash['GeoSrc'] = "Pelias"
        crash['GeoMatchType'] = ""
        crash['GeoConf'] = ""
        crash['GeoAccuracy'] = ""
        crash['GeoBbox'] = ""
