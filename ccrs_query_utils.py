#!/user/bin/env python3 -tt

# Imports
from datetime import datetime
import json
import urllib.request
import requests
import urllib.parse

# Globals

# endpoint prefix depends on search type (SQL or OData)
BASE_URL_SQL = "https://data.ca.gov/api/3/action/datastore_search_sql"
BASE_URL_ODATA = "https://data.ca.gov/api/3/action/datastore_search"

def query_city_ccrs(city_name, resource_id, use_like=False, limit=20000, offset=0, mode="auto"):
    """
    Query the California Crash Reporting System for a given city name.

    Parameters:
        city_name (str): The city to search for.
        resource_id: Correct crashes resource for requested year
        use_like (bool): If True, performs a partial match (SQL only).
        limit (int): Max number of results.
        offset (int): For pagination.
        mode (str): 'sql', 'odata', or 'auto'.

    Returns:
        List[dict]: Records returned from the API.
    """

    if mode not in ("sql", "odata", "auto"):
        raise ValueError("mode must be 'sql', 'odata', or 'auto'")

    # Automatically choose SQL if use_like is True
    if mode == "auto":
        mode = "sql" if use_like else "odata"

    if mode == "sql":
        # Build SQL query
        where_clause = f'"City Name" LIKE \'%{city_name}%\'' if use_like else f'"City Name" = \'{city_name}\''
        sql = (
            f'SELECT * FROM "{resource_id}" '
            f'WHERE {where_clause} '
            f'LIMIT {limit} OFFSET {offset}'
        )
        response = requests.get(BASE_URL_SQL, params={"sql": sql})

    elif mode == "odata":
        # OData requires exact match only
        filters = { "City Name": city_name }
        encoded_filters = urllib.parse.quote(str(filters).replace("'", '"'))
        url = (
            f"{BASE_URL_ODATA}"
            f"?resource_id={resource_id}&filters={encoded_filters}&limit={limit}&offset={offset}"
        )
        response = requests.get(url)

    # Handle response
    if response.ok:
        data = response.json()
        list_dict = response.json().get("result", {})
        records = list_dict['records']
        strip(records)
        reformat_time(records)
        if len(records)==limit:
            print("Number of records reached limit = {limit}. \
                Refactor query_city_ccrs with batching and pagination!")
            exit()

        return records
    else:
        print("Request failed:", response.status_code)
        print(response.text)
        exit()

def query_ccrs_by_collision_ids(collision_ids, resource_id, key, batch_size=200, page_size=200):
    """
    Query CCRS by a list of CollisionIds, handling batching and pagination.

    Args:
        collision_ids (list): List of CollisionId strings.
        resource_id: CCRS resource ID (parties or injuries for a single year)
        key: "Collision Id" for crashes resource; "CollisionId" for parties and injuries
        batch_size (int): Number of CollisionIds per batch query.
        page_size (int): Number of records to retrieve per page (max 200).

    Returns:
        List[dict]: All matching records.
    """
    all_records = []

    for i in range(0, len(collision_ids), batch_size):
        batch = collision_ids[i:i + batch_size]
        ids_str = ",".join(f"'{cid}'" for cid in batch)

        offset = 0
        while True:
            sql = (
                f'SELECT * FROM "{resource_id}" '
                f'WHERE "{key}" IN ({ids_str}) '
                f'LIMIT {page_size} OFFSET {offset}'
            )
            # print(f'query length = {len(BASE_URL_SQL) + len(sql)}')
            response = requests.get(BASE_URL_SQL, params={"sql": sql})

            if not response.ok:
                print(f"Batch {i}, offset {offset} failed:", response.status_code)
                print(response.text)
                exit()

            list_dict = response.json().get("result", {})
            records = list_dict['records']
            all_records.extend(records)

            if len(records) < page_size:
                break  # No more pages
            offset += page_size

    strip(all_records)

    return all_records

def strip(list_dict):
    if list_dict:
        # request output has some leading keys not needed
        if '_full_text' in list(list_dict[0].keys()):   # SQL requests only
            for d in list_dict:
                del d['_id']
                del d['_full_text']
        if '_id' in list(list_dict[0].keys()):
            for d in list_dict:
                del d['_id']

        # remove leading and trailing blanks for str objects
        remove_blanks(list_dict)

def remove_blanks(dicts):
    keys = list(dicts[0].keys())
    for dict in dicts:
        for k in keys:
            if isinstance(dict[k], str):
                dict[k].strip()

def reformat_time(crashes):
    for crash in crashes:
        for key in ['Crash Date Time','PreparedDate','ReviewedDate',\
                    'CreatedDate','ModifiedDate']:
            if crash[key] and 'T' in crash[key]:
                date_time = datetime.strptime(crash[key], '%Y-%m-%dT%H:%M:%S')
                crash[key] = date_time.strftime('%m/%d/%Y %I:%M:%S %p')