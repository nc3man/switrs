#!/user/bin/env python3 -tt

# Imports
from collections import defaultdict
from dumpDictToCSV import dumpDictToCSV
from getDataCsv import getDataCsv
import json
import urllib.request
import time

# User variables
year = '2024'
outpath = 'C:/Users/karl/python/switrs/CCRS/'
crashes_resource = 'f775df59-b89b-4f82-bd3d-8807fa3a22a0'
parties_resource = '93892d36-017b-4a2a-bc0b-f1f385060b96'
injuries_resource = 'a36a0078-d7e1-4244-8337-0a59433c9b84'

search_city = 'Encinitas'
out_file_suffix = 'Encinitas_' + year + '.csv'

# Do not edit below this line --------------------------------------------------

# Helper functions

def get_records(endpoint_url):
    fileobj = urllib.request.urlopen(endpoint_url)
    response_dict = json.loads(fileobj.read())
    return response_dict['result']['records']

def get_records_by_collisionId(endpoint_template, collision_ids):

    records = []

    for cid in collision_ids:
        print(cid)
        endpoint_url = endpoint_template.replace('COLLISION_ID', cid)
        records_cid = get_records(endpoint_url)
        for record in records_cid:
            records.append(record)

    return records

# End helper functions ---------------------------------------------------------

def main():

    print(f"Trimming full CCRS raw data for {year} and {search_city}")
    begtime = time.perf_counter()

    # Set up CCRS API endpoint URLs
    injury_template='https://data.ca.gov/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20%22' \
        + injuries_resource + '%22%20WHERE%20%22CollisionId%22%20LIKE%20%27' + 'COLLISION_ID' + '%27'

    # fetch crashes data via CCRS API filtered by 'City Name'=search_city
    crash_endpoint ='https://data.ca.gov/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20%22' \
        + crashes_resource + '%22%20WHERE%20%22City%20Name%22%20LIKE%20%27' + search_city + '%27'
    crashes = get_records(crash_endpoint)
    collision_ids = [crash['Collision Id'] for crash in crashes]

    # fetch parties data filtered by selected collision_ids
    party_template='https://data.ca.gov/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20%22' \
        + parties_resource + '%22%20WHERE%20%22CollisionId%22=%27' + 'COLLISION_ID' + '%27'
    parties = get_records_by_collisionId(party_template, collision_ids)

    # fetch injuries data filtered by selected collision_ids
    injury_template='https://data.ca.gov/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20%22' \
        + injuries_resource + '%22%20WHERE%20%22CollisionId%22=%27' + 'COLLISION_ID' + '%27'
    injuries = get_records_by_collisionId(injury_template, collision_ids)

    print(f"Time to fetch all CCRS data: {time.perf_counter()-begtime:.4f} sec")
    begtime = time.perf_counter()

    # Pull collision_ids from crashes

    print(len(collision_ids))

    # # save filtered dictionaries to CSV file
    # crash_out = outpath + 'CCRS_crashes_' + out_file_suffix
    # dumpDictToCSV(crashes, crash_out, ',',  crash_keys, encoding='cp850')
    # print(f"\n{len(crashes['Collision Id'])} Filtered Crashes saved in {crash_out}")
    #
    # party_out = outpath + 'CCRS_parties_' + out_file_suffix
    # dumpDictToCSV(parties, party_out, ',',  party_keys, encoding='cp850')
    # print(f"{len(parties['CollisionId'])} Filtered parties saved in {party_out}")
    #
    # injury_out = outpath + 'CCRS_injuries_' + out_file_suffix
    # dumpDictToCSV(injuries, injury_out, ',',  injury_keys, encoding='cp850')
    # print(f"{len(injuries['CollisionId'])} Filtered injuries saved in {injury_out}")
    #
    # print(f"\nTime to save filtered data: {time.perf_counter()-begtime:.4f} sec")


# Main body
if __name__ == '__main__':
    main()