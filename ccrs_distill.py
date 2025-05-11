#!/user/bin/env python3 -tt

# Imports
from collections import defaultdict
from dumpDictToCSV import dumpDictToCSV
from getDataCsv import getDataCsv
import time

# User variables
years = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025',]
search_cities = ['Encinitas', 'Carlsbad', 'Solana Beach', 'Oceanside', 'Del Mar']
inpath = 'C:/Users/karl/python/switrs/CCRS/'

outpath = 'C:/Users/karl/python/switrs/CCRS/'

# Do not edit below this line --------------------------------------------------

# Globals
M2FT = 3.280839895 # convert meters to feet
INJURY_PERSON_TYPE = ['Driver', 'Bicyclist', 'Pedestrian', 'Passenger', 'Other' ]               
INJURY_TYPE = ['Fatal', 'Serious', 'Minor', 'Possible', 'Pain', 'Other' ]               
INJURY_TABLE_KEYS = []
for person in INJURY_PERSON_TYPE:
    for injury in INJURY_TYPE:
        INJURY_TABLE_KEYS.append(f'{person}-{injury}')

# Helper functions

def get_parties(collision_id, parties):
    party_found = []
    for party in parties:
        if party['CollisionId'] == collision_id:
            party_found.append(party) 
    
    # ensure that the party_found list is in party_number order
    parties_found = []
    for n in range(len(party_found)):
        for party in party_found:
            if int(party['PartyNumber']) == n+1:
                parties_found.append(party)
        
    return parties_found
    
def get_injureds(collision_id, injureds):
    injured_found = []
    for injured in injureds:
        if injured['CollisionId'] == collision_id:
            injured_found.append(injured)
    return injured_found
      
def distill(crash, parties, injureds, analyzed, nparty_max, ninjured_max):
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

    # add to output dictionary
    analyzed['CollisionId'].append(collision_id)
    analyzed['Date-Time'].append(date_time)
    analyzed['Day of Week'].append(dow)
    analyzed['Lighting'].append(lighting)
    analyzed['Weather'].append(weather)
    analyzed['Road Condition'].append(road_condition)
    analyzed['Primary Road'].append(primary_road)
    analyzed['Secondary Road'].append(secondary_road)
    analyzed['Secondary Dir'].append(secondary_direction)
    analyzed['Secondary Dist ft'].append(secondary_distance)
    analyzed['Latitude'].append(latitude)
    analyzed['Longitude'].append(longitude)
    analyzed['Collision Type'].append(collision_type)
    analyzed['Motor Vehicle Involved With'].append(other_vehicle)
    analyzed['Primary Collision Factor'].append(pcf)
    analyzed['PCF Violation'].append(pcf_violation)
    analyzed['PCF Party Num'].append(pcf_party)
    analyzed['Cited'].append(cited)
    analyzed['Hit & Run'].append(hit_run)
    analyzed['Num Parties'].append(nparties)
    analyzed['Num Killed'].append(num_killed)
    analyzed['Num Injured'].append(num_injured)
    
    # fill in injury counts table for this crash
    analyzed = add_injury_counts(analyzed, injureds)
                   
    # add in parties in party_number order
    for party in parties:
        analyzed = add_party(analyzed, party)
        
    #  Fill in nulls when nparties < nparty_max
    for n in range(nparties, nparty_max):
        analyzed = add_empty_party(analyzed, str(n+1))
                
    return analyzed
 
def add_party(analyzed, party):
    # Pull out relevant party data
    p_num = party['PartyNumber']
    p_type = party['PartyType']
    p_age = party['StatedAge']
    p_sex = party['GenderDescription']
    try:
        p_dir = party['InattentionDirectionOfTravel']
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

    prefix = f'P{p_num}'

    analyzed[f'{prefix} Party'].append(p_num)
    analyzed[f'{prefix} Type'].append(p_type)
    analyzed[f'{prefix} Age'].append(p_age)
    analyzed[f'{prefix} Gender'].append(p_sex)
    
    analyzed[f'{prefix} Fault'].append(p_fault)
    analyzed[f'{prefix} Other Assoc Factor'].append(p_oaf)
    analyzed[f'{prefix} Lane'].append(p_lane)
    analyzed[f'{prefix} Dir'].append(p_dir)
    analyzed[f'{prefix} Movement'].append(p_movement)
    analyzed[f'{prefix} SpeedLimit'].append(p_speed_limit)
    analyzed[f'{prefix} Vehicle'].append(p_vehicle)

    analyzed[f'{prefix} Sobriety'].append(p_sobriety)
    
    return analyzed

def add_empty_party(analyzed, p_num):
    prefix = f'P{p_num}'

    analyzed[f'{prefix} Party'].append('')
    analyzed[f'{prefix} Type'].append('')
    analyzed[f'{prefix} Age'].append('')
    analyzed[f'{prefix} Gender'].append('')  
    analyzed[f'{prefix} Fault'].append('')  
    analyzed[f'{prefix} Other Assoc Factor'].append('')  
    analyzed[f'{prefix} Lane'].append('')    
    analyzed[f'{prefix} Dir'].append('')
    analyzed[f'{prefix} Movement'].append('')
    analyzed[f'{prefix} SpeedLimit'].append('')
    analyzed[f'{prefix} Vehicle'].append('')
    analyzed[f'{prefix} Sobriety'].append('')
    
    return analyzed
    
def add_injury_counts(analyzed, injureds):
    
    # If no injuries return 0's
    if not(injureds):
        for key in INJURY_TABLE_KEYS:
            analyzed[key].append(0)
        return analyzed
        
    injury_table = {key: 0 for key in INJURY_TABLE_KEYS}
    for injured in injureds:
        p_type = injured['InjuredPersonType']
        person = 'Other'  # default no match
        for s in INJURY_PERSON_TYPE:
            if s.lower() in p_type.lower():
                person = s
                break
           
        inj_type = injured['ExtentOfInjuryCode']
        injury = 'Other'  # default no match
        for s in INJURY_TYPE:
            if s.lower() in inj_type.lower():
                injury = s
                break

        injury_table[f'{person}-{injury}'] += 1
        
    for key in INJURY_TABLE_KEYS:
        analyzed[key].append(injury_table[key])
        
    return analyzed
    
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
            crashes, crash_keys  = getDataCsv(crashes_file, ',', pivot=True, encoding='cp850')
            parties, party_keys  = getDataCsv(parties_file, ',', pivot=True, encoding='cp850')
            injureds, injured_keys = getDataCsv(injured_file, ',', pivot=True, encoding='cp850')
            
            # quickly determine max #parties, #injureds for all crash records
            nparty_max  = 0
            ninjured_max = 0
            for crash in crashes:
                crash_parties = get_parties(crash['Collision Id'] ,parties)
                crash_injureds = get_injureds(crash['Collision Id'], injureds)
                if len(crash_parties) > nparty_max: nparty_max = len(crash_parties)
                if len(crash_injureds) > ninjured_max: ninjured_max = len(crash_injureds)
            
            # distill data for each crash
            analyzed = defaultdict(list)
            for crash in crashes:
                crash_parties = get_parties(crash['Collision Id'], parties)
                crash_injureds = get_injureds(crash['Collision Id'], injureds)
        
                analyzed = distill(crash, crash_parties, crash_injureds, analyzed, nparty_max, ninjured_max)
                
            # save analyzed dictionary to CSV file
            dumpDictToCSV(analyzed, out_file, ',',  list(analyzed.keys()))
            print(f"\nOutput saved in {out_file}")            
            print(f"Time to distill into readable spreadsheet: {time.perf_counter()-begtime:.4f} sec")
            
    print(f"\nTotal time to distill all {len(years)*len(search_cities)} years & cities: {time.perf_counter()-begtime_all:.4f} sec")
   
# Main body
if __name__ == '__main__':
    main()