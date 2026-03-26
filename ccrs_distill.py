#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from CVC_dictionary import lookup_cvc
import numpy as np
import time
import os

# User variables
years = ['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
search_cities = ['Del Mar', 'Solana Beach', 'Encinitas', 'Carlsbad', 'Vista', 'Oceanside',
    'Santee', 'San Marcos','Poway','National City','Lemon Grove','La Mesa','San Diego',
    'Imperial Beach','Escondido','El Cajon','Coronado','Chula Vista',
    'Unincorporated','San Diego Harbor','San Diego State Univ','Uc San Diego']

inpath = './CCRS_raw_update_api/'
outpath = './CCRS_from_raw_api/'
# inpath = './CCRS_raw_update_csv/'
# outpath = './CCRS_newest/'

# Do not edit below this line --------------------------------------------------

# Globals
M2FT = 3.280839895 # convert meters to feet
INJURY_PERSON_TYPE = ['Driver', 'Bicyclist', 'Pedestrian', 'Passenger', 'Other']               
INJURY_TYPE =['Fatal','SuspectSerious','SuspectMinor','PossibleInjury']

INJURY_TABLE_KEYS = []
for person in INJURY_PERSON_TYPE:
    for injury in INJURY_TYPE:
        INJURY_TABLE_KEYS.append(f'{person}-{injury}')
INJURY_FATAL_KEYS = np.array(['Fatal' in key for key in INJURY_TABLE_KEYS], dtype=bool)

logpath = outpath + 'logs/'

# Helper functions
   
def order_parties(parties):
    # parties for a particular crash may not be ordered by PartyNumber. Reorder so
    parties_reordered = []
    for n in range(len(parties)):
        for party in parties:
            if int(party['PartyNumber']) == n+1:
                parties_reordered.append(party)
        
    return parties_reordered
    
def distill(crash, parties, injureds, nparty_max, logger):
    import CVC_dictionary
    
    nparties = len(parties)
    ninjureds = len(injureds)
    
    collision_id = crash['Collision Id']
    date_time = crash['Crash Date Time']
    creation_date = crash['CreatedDate']
    modification_date = crash['ModifiedDate']
    city = crash['City Name']
    dow = crash['Day Of Week']
    lighting = crash['LightingDescription']
    try:
        weather = crash['Weather 1']
        if len(crash['Weather 2']) > 0:
            weather = weather + ' + ' + crash['Weather 2']
    except:
        weather = 'n/a' # before 2016
    
    roadway_surface = decode_roadway_surface(crash['RoadwaySurfaceCode']) 
    
    try:
        road_condition = crash['Road Condition 1']
        if len(crash['Road Condition 2']) > 0:
            road_condition = road_condition + ' + ' +  crash['Road Condition 2'] 
    except:
        road_condition = 'n/a' # before 2016
    
    if "Special Condition" in crash:
        special_condition = crash['Special Condition']
    else:
        special_condition = ''
        
    traffic_control_devices = decode_traffic_control_device(crash['TrafficControlDeviceCode'])

    # location
    primary_road = crash['PrimaryRoad']
    secondary_road = crash['SecondaryRoad']
    secondary_direction = crash['SecondaryDirection']
    secondary_distance = crash['SecondaryDistance']
    if crash['SecondaryUnitOfMeasure']=='M':
        secondary_distance = str(float(secondary_distance) * M2FT) 
    latitude = crash['Latitude']
    longitude = crash['Longitude']
    if latitude and longitude:
        geosrc = "CCRS"
    else:
        geosrc = ""
                      
    # collision stuff
    is_tow_away = crash['IsTowAway']
    pedestrian_action = crash['PedestrianActionDesc']
    collision_type = crash['Collision Type Description']
    if len(crash['Collision Type Other Desc']) > 0:
        collision_type = collision_type + ' / ' + crash['Collision Type Other Desc']
        
    other_vehicle = crash['MotorVehicleInvolvedWithDesc']
    if len(crash['MotorVehicleInvolvedWithOtherDesc']) > 0:
        other_vehicle = other_vehicle + ' + ' + crash['MotorVehicleInvolvedWithOtherDesc']
    pedestrian_action = crash['PedestrianActionDesc']
    
    # crash stuff
    num_injured = crash['NumberInjured']
    num_killed = crash['NumberKilled']
    
    try:
        pcf = decode_pcf(crash['Primary Collision Factor Code'])
    except:
        pcf = decode_pcf(crash['PrimaryCollisionFactorCode']) # before 2016
    try:
        pcf_violation = crash['Primary Collision Factor Violation']
    except:
        pcf_violation = crash['PrimaryCollisionFactorDescription'] # before 2016
    # pcf_description = decode_violation(pcf_violation)
    pcf_description = lookup_cvc(pcf_violation)
    if len(pcf_description)==0:
        pcf_description = pcf_violation

    cited = crash['PrimaryCollisionFactorIsCited']
    hit_run = decode_hit_run(crash['HitRun'])
    pcf_party = crash['PrimaryCollisionPartyNumber']

    # create dictionary for this crash
    analyzed = {}
    analyzed['CollisionId'] = collision_id
    analyzed['Crash Date-Time'] = date_time
    analyzed['CreatedDate'] = creation_date
    analyzed['ModifiedDate'] = modification_date
    analyzed['City'] = city
    analyzed['Day of Week'] = dow
    analyzed['Lighting'] = lighting
    analyzed['Weather'] = weather
    analyzed['Roadway Surface Desc'] = roadway_surface
    analyzed['Road Condition'] = road_condition
    analyzed['Special Condition'] = special_condition
    analyzed['Traffic Control Device Desc'] = traffic_control_devices 
    analyzed['Primary Road'] = primary_road
    analyzed['Secondary Road'] = secondary_road
    analyzed['Secondary Dir'] = secondary_direction
    analyzed['Secondary Dist ft'] = secondary_distance
    analyzed['Latitude'] = latitude
    analyzed['Longitude'] = longitude
    analyzed['GeoSrc'] = geosrc
    analyzed['GeoMatchType'] = ""
    analyzed['GeoConf'] = ""
    analyzed['GeoAccuracy'] = ""
    analyzed['GeoBbox'] = ""
    analyzed['Collision Type'] = collision_type
    analyzed['Motor Vehicle Involved With'] = other_vehicle
    analyzed['Primary Collision Factor'] = pcf
    analyzed['PCF Violation'] = pcf_violation
    analyzed['PCF Violation Description'] = pcf_description
    analyzed['PCF Party Num'] = pcf_party
    analyzed['Cited'] = cited
    analyzed['Hit & Run'] = hit_run
    analyzed['IsTowAway'] = is_tow_away
    analyzed['Pedestrian Action'] = pedestrian_action
    analyzed['Num Parties'] = str(nparties)
    
    # fill in injury counts table for this crash
    add_injury_counts(analyzed, injureds, logger)
    
    # CCRS total injury counts may differ from our count - record any deltas
    if num_injured and (num_injured != analyzed['Num Injured']):
        logger['logfile'].write(f'CID:{collision_id} CCRS num_injured={num_injured} != Calculated num_injured={analyzed['Num Injured']}\n')
        logger['nwarnings'] += 1
    if num_killed and (num_killed != analyzed['Num Killed']):
        logger['logfile'].write(f'CID:{collision_id} CCRS num_killed={num_killed} != Calculated num_killed={analyzed['Num Killed']}\n')
        logger['nwarnings'] += 1
                   
    # add in parties in party_number order
    for party in parties:
        injured_party = [injured for injured in injureds if injured['PartyNumber']==party['PartyNumber']]
        add_party(analyzed, party, injured_party)
        
    #  Fill in nulls when nparties < nparty_max
    for n in range(nparties, nparty_max):
        add_empty_party(analyzed, str(n+1))
                
    return analyzed
    
def add_party(analyzed, party, injured_party):
    # Pull out relevant party data
    p_num = party['PartyNumber']
    p_id = party['PartyId']
    p_type = party['PartyType']
    p_age = party['StatedAge']
    p_sex = party['GenderDescription']
    p_airbag = party['AirbagDescription']
    p_safety_equip = party['SafetyEquipmentDescription']
    p_special_info = party['Special Information']
    try:
        p_dir = party['DirectionOfTravel'] # new api format
        p_inattention = party['Inattention']
    except:
        p_dir = party['InattentionDirectionOfTravel']  # old csv format
        p_inattention = ''
        if len(p_dir) > 1:  # contains InAttention info - direction is last
            p_dir = p_dir[-1]
            p_inattention = p_dir[0:len(p_dir)-1]
    p_street = party['StreetOrHighwayName']
    if party['Lane']:
        p_lane = party['Lane']
        if party['TotalLanes']:
            p_lane = f"{p_lane} of {party['TotalLanes']}"
    else:
        p_lane = ''
    p_movement = party['MovementPrecCollDescription']
    try:
        p_vehicle = party['Vehicle1TypeDesc'] + ': ' + party['Vehicle1Year'] + '/' + party['Vehicle1Make'] + '/' + party['Vehicle1Model'] + '/' + party['Vehicle1Color'] 
    except:            
        p_vehicle = party['V1Year'] + '/' + party['V1Make'] + '/' + party['V1Model'] + '/' + party['V1Color']
    p_speed_limit = party['SpeedLimit']
    p_fault = party['IsAtFault']
    p_sobriety = party['SobrietyDrugPhysicalDescription1']
    if len(party['SobrietyDrugPhysicalDescription2']) > 0:
        p_sobriety = p_sobriety + ' + ' + party['SobrietyDrugPhysicalDescription2']
    try:
        p_oaf = party['Other Associate Factor']
    except:
        p_oaf = ''   
    try:
        p_special_information = party['Special Information']
    except:
        p_oaf = ''   
        
    # concatenate pertinent injured info corresponding to this party
    p_injured_list = ''
    p_injured_list_id = ''
    p_injury_extent_list = ''
    if len(injured_party) > 0:
        for injured in injured_party:
            p_injured_list = p_injured_list + f"{injured['InjuredPersonType']},"
            p_injured_list_id = p_injured_list_id + f"{injured['InjuredWitPassId']}~"
            p_injury_extent_list = p_injury_extent_list + f"{get_injury_extent(injured['ExtentOfInjuryCode'])},"
        p_injured_list = p_injured_list[0:-1]  # strip trailing comma
        p_injured_list_id = p_injured_list_id[0:-1]  # strip trailing separator
        p_injury_extent_list = p_injury_extent_list[0:-1]  # strip trailing comma

    prefix = f'P{p_num}'

    analyzed[f'{prefix} Party'] = p_num
    analyzed[f'{prefix} PartyId'] = p_id
    analyzed[f'{prefix} Type'] = p_type
    analyzed[f'{prefix} Age'] = p_age
    analyzed[f'{prefix} Gender'] = p_sex
    
    analyzed[f'{prefix} Fault'] = p_fault
    analyzed[f'{prefix} Other Assoc Factor'] = p_oaf
    analyzed[f'{prefix} InAttention'] = p_inattention
    analyzed[f'{prefix} Street/Hwy'] = p_street
    analyzed[f'{prefix} Lane'] = p_lane
    analyzed[f'{prefix} Direction'] = p_dir
    analyzed[f'{prefix} Movement'] = p_movement
    analyzed[f'{prefix} SpeedLimit'] = p_speed_limit
    analyzed[f'{prefix} Vehicle'] = p_vehicle
    
    analyzed[f'{prefix} Airbag'] = p_airbag
    analyzed[f'{prefix} Safety Equipment'] = p_safety_equip
    analyzed[f'{prefix} Special Information'] = p_special_info


    analyzed[f'{prefix} Sobriety'] = p_sobriety
    
    # add in associated injured persons lists
    analyzed[f'{prefix} Assoc Injured list'] = p_injured_list
    analyzed[f'{prefix} Assoc Injured list Id'] = p_injured_list_id
    analyzed[f'{prefix} Assoc Injury Extent list'] = p_injury_extent_list

def add_empty_party(analyzed, p_num):
    prefix = f'P{p_num}'

    analyzed[f'{prefix} Party'] = ''
    analyzed[f'{prefix} PartyId'] = ''
    analyzed[f'{prefix} Type'] = ''
    analyzed[f'{prefix} Age'] = ''
    analyzed[f'{prefix} Gender'] = ''
    analyzed[f'{prefix} Fault'] = ''
    analyzed[f'{prefix} Other Assoc Factor'] = ''  
    analyzed[f'{prefix} InAttention'] = ''  
    analyzed[f'{prefix} Street/Hwy'] = ''  
    analyzed[f'{prefix} Lane'] = ''  
    analyzed[f'{prefix} Direction'] = ''
    analyzed[f'{prefix} Movement'] = ''
    analyzed[f'{prefix} SpeedLimit'] = ''
    analyzed[f'{prefix} Vehicle'] = ''
    analyzed[f'{prefix} Airbag'] = ''
    analyzed[f'{prefix} Safety Equipment'] = ''
    analyzed[f'{prefix} Special Information'] = ''
    analyzed[f'{prefix} Sobriety'] = ''
    analyzed[f'{prefix} Assoc Injured list'] = ''
    analyzed[f'{prefix} Assoc Injured list Id'] = ''
    analyzed[f'{prefix} Assoc Injury Extent list'] = ''

def get_injury_extent(extent_of_injury):
    if extent_of_injury == 'Fatal':
        injury = 'Fatal'
    elif extent_of_injury=='SuspectSerious' or extent_of_injury=='SevereInactive':
        injury = 'SuspectSerious'
    elif extent_of_injury=='SuspectMinor' or extent_of_injury=='ComplaintOfPainInactive':
        injury = 'SuspectMinor'
    elif extent_of_injury=='PossibleInjury' or extent_of_injury=='OtherVisibleInactive':
        injury = 'PossibleInjury'
    else:
        injury = 'Unknown'
        
    return injury

def add_injury_counts(analyzed, injureds, logger):
    
    # If no injuries return 0's
    if not(injureds):
        analyzed['Num Killed'] = '0'
        analyzed['Num Injured'] = '0'
        for key in INJURY_TABLE_KEYS:
                analyzed[key] = '0'
        return analyzed
        
    injury_table = {key: 0 for key in INJURY_TABLE_KEYS}
    for injured in injureds:
        p_type = injured['InjuredPersonType']
        person = 'Unknown'  # default no match
        for s in INJURY_PERSON_TYPE:
            if s.lower() in p_type.lower():
                person = s
                break
        if person == 'Unknown': 
            # log exception
            logger['logfile'].write(f'CID:{analyzed['CollisionId']} Unexpected Injured Person type = {p_type}\n')
            logger['nwarnings'] += 1
            person = 'Other'
        
        inj_type = injured['ExtentOfInjuryCode']
        injury = get_injury_extent(inj_type)
        if injury == 'Unknown':
            # log exception
            logger['logfile'].write(f'CID:{analyzed['CollisionId']} Unexpected Extent of Injury = {inj_type}\n')
            logger['nwarnings'] += 1


        injury_table[f'{person}-{injury}'] += 1
 
    table_num = np.array([injury_table[key] for key in INJURY_TABLE_KEYS],dtype=int)
    fatal_num = table_num[INJURY_FATAL_KEYS]
    num_killed = fatal_num.sum()
    num_injured = table_num.sum()-num_killed
    
    analyzed['Num Killed'] = str(num_killed)
    analyzed['Num Injured'] = str(num_injured)
           
    for key in INJURY_TABLE_KEYS:
        analyzed[key] = str(injury_table[key])
    
def decode_pcf(pcf):
    if pcf == 'A':
        desc = 'Vehicle Code Violation'
    elif pcf == 'B':
        desc = 'Other Improper Driving'
    elif pcf == 'C':
        desc = 'Other Than Driver'
    elif pcf == 'D':
        desc = 'Unknown'
    elif pcf == 'E':
        desc = 'Fell Asleep'
    else:
        desc = 'Not Stated'
    return desc

def decode_hit_run(hit_run):
    if hit_run == 'F':
        desc = 'Felony'
    elif hit_run == 'M':
        desc = 'Misdemeanor'
    else:
        desc = ' '
    return desc
    
def decode_roadway_surface(code):
    if code=='A':
        desc = 'Dry'
    elif code=='B':
        desc = 'Wet'
    elif code=='C':
        desc = 'Snowy-Icy'
    elif code=='D':
        desc = 'Slippery(Muddy,Oily,etc)'
    elif len(code) > 0:
        desc = f"UNKNOWN CODE={code}"
    else:
        desc = ''
        
    return desc

def decode_traffic_control_device(code):
    if code=='A':
        desc = 'Controls Functioning'
    elif code=='B':
        desc = 'Controls NOT Functioning'
    elif code=='C':
        desc = 'Controls Obscured'
    elif code=='D':
        desc = 'NO Controls Present/Factor'
    elif len(code) > 0:
        desc = f"UNKNOWN CODE={code}"
    else:
        desc = ''
        
    return desc

def open_append(filename):
    # First check to see if it exists - will delete to open new file
    if os.path.exists(filename):
        os.remove(filename)
    # Create new file and open in append mode
    file_obj = open(filename, 'a')
    return file_obj

# End helper functions ---------------------------------------------------------

def main():
    
    begtime_all = time.perf_counter()
    n = 0
 
    for search_city in search_cities:
        for year in years:
            
            print(f"\nDistilling {search_city} {year}")
 
            crashes_file = inpath + f'CCRS_crashes_{search_city}_{year}.csv'
            parties_file = inpath + f'CCRS_parties_{search_city}_{year}.csv'
            injured_file = inpath + f'CCRS_injured_{search_city}_{year}.csv'
            out_file = outpath + f'CCRS_{search_city}_{year}.csv'
            begtime = time.perf_counter()
            n+=1
 
            # read data from CCRS raw data files
            crashes, crash_keys  = getListDictCsv(crashes_file, ',', encoding='cp850')
            parties, party_keys  = getListDictCsv(parties_file, ',', encoding='cp850')
            injureds, injured_keys = getListDictCsv(injured_file, ',', encoding='cp850')
                       
            # quickly determine max #parties for all crash records
            nparty_max  = 0
            for crash in crashes:
                crash_parties = [ party for party in parties if party['CollisionId']==crash['Collision Id'] ]
                if len(crash_parties) > nparty_max: nparty_max = len(crash_parties)
            
            analyzed = []
            logfile = f'{logpath}warnings_{search_city}_{year}.log'
            logger = {'logfile': open_append(logfile), 'nwarnings':0}
            
            # first deal out parties and injureds by crashes['Collision Id']
            party_dict = dict()
            injured_dict = dict()
            for crash in crashes:
                party_dict[crash['Collision Id']] = []
                injured_dict[crash['Collision Id']] = []                
            for party in parties:
                party_dict[party['CollisionId']].append(party)
            for injured in injureds:
                injured_dict[injured['CollisionId']].append(injured)
            
            # distill data for each crash
            for crash in crashes:
                crash_parties = order_parties(party_dict[crash['Collision Id']])
                crash_injureds = injured_dict[crash['Collision Id']]
                crash_distill = distill(crash, crash_parties, crash_injureds, nparty_max, logger)
                analyzed.append(crash_distill)
                                
            # save analyzed dictionary to CSV file (use keys from the first crash)
            crash_keys = list(analyzed[0].keys())
            dumpListDictToCSV(analyzed, out_file, ',', crash_keys)
            print(f"\nOutput saved in {out_file}")
            print(f"Time to distill: {time.perf_counter()-begtime:.4f} sec")
            
            # See if any issues occurred
            logger['logfile'].close()
            if logger['nwarnings'] > 0:
                print(f'logger FOUND! see {logger['nwarnings']} messages in {logfile}')
            else:
                os.remove(logfile)
            
    print(f"\nTotal time to distill CCRS records for {len(years)} years and {len(search_cities)} cities: {time.perf_counter()-begtime_all:.4f} sec")

   
# Main body
if __name__ == '__main__':
    main()