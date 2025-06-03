#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
import numpy as np
import time
import os

# User variables
years = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025',]
search_cities = ['Encinitas', 'Carlsbad', 'Solana Beach', 'Oceanside', 'Del Mar', 'Vista']
inpath = 'C:/Users/karl/python/switrs/CCRS_raw/'
outpath = 'C:/Users/karl/python/switrs/CCRS/'

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

def get_parties(collision_id, parties):
    party_found = [party for party in parties if party['CollisionId'] == collision_id]
    
    # ensure that the party_found list is in party_number order
    parties_found = []
    for n in range(len(party_found)):
        for party in party_found:
            if int(party['PartyNumber']) == n+1:
                parties_found.append(party)
        
    return parties_found
    
def distill(crash, parties, injureds, nparty_max, logger):
    nparties = len(parties)
    ninjureds = len(injureds)
    
    collision_id = crash['Collision Id']
    date_time = crash['Crash Date Time']
    dow = crash['Day Of Week']
    lighting = crash['LightingDescription']
    try:
        weather = crash['Weather 1']
        if len(crash['Weather 2']) > 0:
            weather = weather + ' + ' + crash['Weather 2']
    except:
        weather = 'n/a' # before 2016
    try:
        road_condition = crash['Road Condition 1']
        if len(crash['Road Condition 2']) > 0:
            road_condition = road_condition + ' + ' +  crash['Road Condition 2'] 
    except:
        road_condition = 'n/a' # before 2016

    # location
    primary_road = crash['PrimaryRoad']
    secondary_road = crash['SecondaryRoad']
    secondary_direction = crash['SecondaryDirection']
    secondary_distance = crash['SecondaryDistance']
    if crash['SecondaryUnitOfMeasure']=='M':
        secondary_distance = str(float(secondary_distance) * M2FT) 
    latitude = crash['Latitude']
    longitude = crash['Longitude']
        
    # collision stuff
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
    cited = crash['PrimaryCollisionFactorIsCited']
    hit_run = decode_hit_run(crash['HitRun'])
    pcf_party = crash['PrimaryCollisionPartyNumber']

    # create dictionary for this crash
    analyzed = {}
    analyzed['CollisionId'] = collision_id
    analyzed['Date-Time'] = date_time
    analyzed['Day of Week'] = dow
    analyzed['Lighting'] = lighting
    analyzed['Weather'] = weather
    analyzed['Road Condition'] = road_condition
    analyzed['Primary Road'] = primary_road
    analyzed['Secondary Road'] = secondary_road
    analyzed['Secondary Dir'] = secondary_direction
    analyzed['Secondary Dist ft'] = secondary_distance
    analyzed['Latitude'] = latitude
    analyzed['Longitude'] = longitude
    analyzed['Collision Type'] = collision_type
    analyzed['Motor Vehicle Involved With'] = other_vehicle
    analyzed['Primary Collision Factor'] = pcf
    analyzed['PCF Violation'] = pcf_violation
    analyzed['PCF Party Num'] = pcf_party
    analyzed['Cited'] = cited
    analyzed['Hit & Run'] = hit_run
    analyzed['Num Parties'] = str(nparties)
    
    # fill in injury counts table for this crash
    analyzed, logger = add_injury_counts(analyzed, injureds, logger)
    
    # CCRS total injury counts may differ from our count - record any deltas
    if num_injured != analyzed['Num Injured']:
        logger['logfile'].write(f'CID:{collision_id} CCRS num_injured={num_injured} != Calculated num_injured={analyzed['Num Injured']}\n')
        logger['nwarnings'] += 1
    if num_killed != analyzed['Num Killed']:
        logger['logfile'].write(f'CID:{collision_id} CCRS num_killed={num_killed} != Calculated num_killed={analyzed['Num Killed']}\n')
        logger['nwarnings'] += 1
                   
    # add in parties in party_number order
    for party in parties:
        injured_party = [injured for injured in injureds if injured['PartyNumber']==party['PartyNumber']]
        analyzed = add_party(analyzed, party, injured_party)
        
    #  Fill in nulls when nparties < nparty_max
    for n in range(nparties, nparty_max):
        analyzed = add_empty_party(analyzed, str(n+1))
                
    return analyzed, logger
    
def add_party(analyzed, party, injured_party):
    # Pull out relevant party data
    p_num = party['PartyNumber']
    p_type = party['PartyType']
    p_age = party['StatedAge']
    p_sex = party['GenderDescription']
    try:
        p_dir = party['InattentionDirectionOfTravel']
        if len(p_dir) > 1:  # contains InAttention info - direction is last
            dir = p_dir[-1]
            inattention = p_dir[0:len(p_dir)-1]
            p_dir = f'{dir}-{inattention}'
    except:
        p_dir = party['DirectionOfTravel'] # before 2016
    p_lane = party['Lane']
    p_movement = party['MovementPrecCollDescription']
    p_vehicle = party['V1Year'] + '/' + party['V1Make'] + '/' + party['V1Model'] + '/' + party['V1Color']
    p_speed_limit = party['SpeedLimit']
    p_fault = party['IsAtFault']
    p_sobriety = party['SobrietyDrugPhysicalDescription1']
    if len(party['SobrietyDrugPhysicalDescription2']) > 0:
        p_sobriety = p_sobriety + ' + ' + party['SobrietyDrugPhysicalDescription2']
    try:
        p_oaf = party['Other Associate Factor']
    except:
        p_oaf = ''    # before 2016
        
    # concatenate pertinent injured info corresponding to this party
    p_injured_list = ''
    p_injury_extent_list = ''
    if len(injured_party) > 0:
        for injured in injured_party:
            p_injured_list = p_injured_list + f"{injured['InjuredPersonType']},"
            p_injury_extent_list = p_injury_extent_list + f"{get_injury_extent(injured['ExtentOfInjuryCode'])},"
        p_injured_list = p_injured_list[0:-1]  # strip trailing comma
        p_injury_extent_list = p_injury_extent_list[0:-1]  # strip trailing comma

    prefix = f'P{p_num}'

    analyzed[f'{prefix} Party'] = p_num
    analyzed[f'{prefix} Type'] = p_type
    analyzed[f'{prefix} Age'] = p_age
    analyzed[f'{prefix} Gender'] = p_sex
    
    analyzed[f'{prefix} Fault'] = p_fault
    analyzed[f'{prefix} Other Assoc Factor'] = p_oaf
    analyzed[f'{prefix} Lane'] = p_lane
    analyzed[f'{prefix} Dir-InAttention'] = p_dir
    analyzed[f'{prefix} Movement'] = p_movement
    analyzed[f'{prefix} SpeedLimit'] = p_speed_limit
    analyzed[f'{prefix} Vehicle'] = p_vehicle

    analyzed[f'{prefix} Sobriety'] = p_sobriety
    
    # add in associated injured persons lists
    analyzed[f'{prefix} Assoc Injured list'] = p_injured_list
    analyzed[f'{prefix} Assoc Injury Extent list'] = p_injury_extent_list
    
    return analyzed

def add_empty_party(analyzed, p_num):
    prefix = f'P{p_num}'

    analyzed[f'{prefix} Party'] = ''
    analyzed[f'{prefix} Type'] = ''
    analyzed[f'{prefix} Age'] = ''
    analyzed[f'{prefix} Gender'] = ''
    analyzed[f'{prefix} Fault'] = ''
    analyzed[f'{prefix} Other Assoc Factor'] = ''  
    analyzed[f'{prefix} Lane'] = ''  
    analyzed[f'{prefix} Dir-InAttention'] = ''
    analyzed[f'{prefix} Movement'] = ''
    analyzed[f'{prefix} SpeedLimit'] = ''
    analyzed[f'{prefix} Vehicle'] = ''
    analyzed[f'{prefix} Sobriety'] = ''
    analyzed[f'{prefix} Assoc Injured list'] = ''
    analyzed[f'{prefix} Assoc Injury Extent list'] = ''

    return analyzed

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
        return analyzed, logger
        
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
            continue
        
        inj_type = injured['ExtentOfInjuryCode']
        injury = get_injury_extent(inj_type)
        if injury == 'Unknown':
            # log exception
            logger['logfile'].write(f'CID:{analyzed['CollisionId']} Unexpected Extent of Injury = {inj_type}\n')
            logger['nwarnings'] += 1
            continue

        injury_table[f'{person}-{injury}'] += 1
 
    table_num = np.array([injury_table[key] for key in INJURY_TABLE_KEYS],dtype=int)
    fatal_num = table_num[INJURY_FATAL_KEYS]
    num_killed = fatal_num.sum()
    num_injured = table_num.sum()-num_killed
    
    analyzed['Num Killed'] = str(num_killed)
    analyzed['Num Injured'] = str(num_injured)
           
    for key in INJURY_TABLE_KEYS:
        analyzed[key] = str(injury_table[key])
        
    return analyzed, logger
    
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
            
            # distill data for each crash
            for crash in crashes:
                crash_parties = get_parties(crash['Collision Id'], parties)  # in party order
                crash_injureds = [injured for injured in injureds if injured['CollisionId']==crash['Collision Id']]

                crash_distill, logger = distill(crash, crash_parties, crash_injureds, nparty_max, logger)
                analyzed.append(crash_distill)
                
            # save analyzed dictionary to CSV file (use keys from the last crash)
            dumpListDictToCSV(analyzed, out_file, ',',  list(crash_distill.keys()))
            print(f"\nOutput saved in {out_file}")            
            print(f"Time to distill into readable spreadsheet: {time.perf_counter()-begtime:.4f} sec")
            
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