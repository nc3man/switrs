import requests
from geopy.distance import distance
from geopy.point import Point

API_KEY = REDACTED
SDBOUNDS = "32.34,-117.29|33.56,-116.00"
BEARING = {"N":0, "E":90, "S":180, "W":270}
M2FT = 3.280839895 # convert meters to feet
FT2M = 1.0/M2FT
API_READ_TIMEOUT=20

def google_geocode(query, api_key, bounds=None):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": query,
        "key": api_key
    }
    if bounds:
        params["bounds"] = bounds  # format: "SW_lat,SW_lng|NE_lat,NE_lng"

    try:
        response = requests.get(url, params=params, timeout=API_READ_TIMEOUT)
        data = response.json()
    except: # try again
        response = requests.get(url, params=params, timeout=API_READ_TIMEOUT)
        data = response.json()

    if data["status"] == "OK":
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    else:
        return None

def move_along_bearing(start_coords, distance_meters, bearing_degrees):
    start_point = Point(start_coords[0], start_coords[1])
    # geopy distance takes km, so convert meters
    dest = distance(meters=distance_meters).destination(point=start_point, bearing=bearing_degrees)
    return (dest.latitude, dest.longitude)

def geocode_google(crash):
    # set up Google Maps API decoder query
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
        query = f"{road1} & {road2}, {city}, CA"
    else:
        query = f"{road1}, {city}, CA"

    # get lat, lon of query
    latlon = google_geocode(query, API_KEY, bounds=SDBOUNDS)
    if latlon:
        # move along intersection point
        if dist_ft > 0.0:
            try:
                latlon = move_along_bearing(latlon, dist_ft*FT2M, BEARING[direction])
                crash['Latitude'] = str(latlon[0])
                crash['Longitude'] = str(latlon[1])
            except:
                crash['Latitude'] = "NO MATCH"
                crash['Longitude'] = "NO MATCH"
        else:
            crash['Latitude'] = str(latlon[0])
            crash['Longitude'] = str(latlon[1])

    else:
        crash['Latitude'] = "NO MATCH"
        crash['Longitude'] = "NO MATCH"

    crash['GeoSrc'] = "Google"

