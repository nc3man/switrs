#!/user/bin/env python3 -tt

# Imports
from collections import defaultdict
from dumpDictToCSV import dumpDictToCSV
from getDataCsv import getDataCsv

# User variables
inpath = 'C:/Users/karl/bike/sdcbc/advocacy/encinitas/switrs/260148/'
crashes_file = inpath + 'Accident_260148.csv'
parties_file = inpath + 'Party_260148.csv'
victims_file = inpath + 'Victim_260148.csv'
out_file = inpath + 'SWITRS_Encinitas_2024-2025.csv'

VERBOSE = False

# Do not edit below this line --------------------------------------------------
# Helper functions

def get_parties(case_id, parties):
    party_found = []
    for party in parties:
        if party['case_id'] == case_id:
            party_found.append(party) 
    
    # ensure that the party_found list is in party_number order
    parties_found = []
    for n in range(len(party_found)):
        for party in party_found:
            if int(party['party_number']) == n+1:
                parties_found.append(party)
        
    return parties_found
    
def get_victims(case_id, victims):
    victim_found = []
    for victim in victims:
        if victim['case_id'] == case_id:
            victim_found.append(victim)
    return victim_found
      
def distill(crash, parties, victims, analyzed, nparty_max, nvictim_max):
    case_id = crash['case_id']
    year = crash['accident_year']
    date = f"{split_YMD(crash['collision_date'])} {split_hhmm(crash['collision_time'])}"
    if crash['intersection'] == 'Y':
        location = crash['primary_rd'] + ' @ ' + crash['secondary_rd']
    else:
        location = crash['primary_rd'] + ' ' + f"{float(crash['distance']):.0f}" + 'ft ' \
        + crash['direction'] + ' / ' + crash['secondary_rd']
    collision_type = decode_collision(crash['type_of_collision'])
    weather = decode_weather(crash['weather_1'])
    if len(decode_weather(crash['weather_2'])) > 0:
        weather = weather + ' & ' + decode_weather(crash['weather_2'])
    surface = decode_surface(crash['road_surface'])
    weather_surface = weather + ' / ' + surface
    pcf = decode_pcf(crash['primary_coll_factor'], crash['pcf_viol_category'])
    pcf_viol = crash['pcf_violation'] + '.' + crash['pcf_viol_subsection']
    severity = decode_severity(int(crash['collision_severity']))
    int_turn = crash['intersection']
    hit_run = decode_hit_run(crash['hit_and_run'])
    
    # add to output dictionary
    analyzed['Case_ID'].append(case_id)
    analyzed['Year'].append(year)
    analyzed['Date'].append(date)
    analyzed['Location'].append(location)
    analyzed['Weather/Surface'].append(weather_surface)
    analyzed['Collision Type'].append(collision_type)
    analyzed['Primary Collision Factor'].append(pcf)
    analyzed['PCF Violation'].append(pcf_viol)
    analyzed['Int/Turn'].append(int_turn)
    analyzed['Hit & Run'].append(hit_run)
    analyzed['Severity'].append(severity)

    if VERBOSE:
        print(f"CaseID:{case_id} Year:{year} Date:{date} Location:{location} Weather/Surface:{weather_surface} Collision_Type:{collision_type} PCF:{pcf} PCF_Violation:{pcf_viol} Int/Turn:{int_turn} Hit_Run:{hit_run} Severity:{severity}")

    # Pull out relevant party data
    nparties = len(parties)
    for n in range(nparties):
        p_age_sex = parties[n]['party_age'] + '/' + parties[n]['party_sex']
        p_dir = parties[n]['dir_of_travel']
        p_movement = decode_movement(parties[n]['move_pre_acc'])
        try:
            p_type = decode_party_type(int(parties[n]['party_type']))
        except:
            p_type = parties[n]['party_type']
        p_fault = parties[n]['at_fault']
        p_sobriety = decode_sobriety(parties[n]['party_sobriety'])
        p_drugs = decode_drugs(parties[n]['party_drug_physical'])
        p_oaf = decode_oaf(parties[n]['oaf_1'])
        p_oaf_2 = decode_oaf(parties[n]['oaf_2'])
        if len(p_oaf_2) > 0:
            p_oaf = p_oaf + ' / ' + p_oaf_2
        p_oaf_viol = decode_oaf_violation(parties[n]['oaf_viol_cat'])
        p_oaf_viol_cvc = parties[n]['oaf_viol_section'] + '.' + parties[n]['oaf_violation_suffix']
        
        prefix = f'P{n+1}'

        if VERBOSE:
            print(f"{prefix}_Age/Sex:{p_age_sex} {prefix}_Type:{p_type} {prefix}_Dir:{p_dir} {prefix}_Movement:{p_movement} {prefix}_Fault:{p_fault} {prefix}_Sobriety:{p_sobriety} {prefix}_Drugs:{p_drugs} {prefix}_Other Associated Factors:{p_oaf} {prefix}_Other Associated Violation:{p_oaf_viol} {prefix}_OAF_CVC:{p_oaf_viol_cvc}")
        
        analyzed[f'{prefix}_Age/Sex'].append(p_age_sex)
        analyzed[f'{prefix}_Type'].append(p_type)
        analyzed[f'{prefix}_Dir'].append(p_dir)
        analyzed[f'{prefix}_Movement'].append(p_movement)
        analyzed[f'{prefix}_Fault'].append(p_fault)
        analyzed[f'{prefix}_Sobriety'].append(p_sobriety)
        analyzed[f'{prefix}_Drugs'].append(p_drugs)
        analyzed[f'{prefix}_Other Associated Factors'].append(p_oaf)
        analyzed[f'{prefix}_Other Associated Violation'].append(p_oaf_viol)
        analyzed[f'{prefix}_OAF_CVC'].append(p_oaf_viol_cvc)
                
    # Fill in nulls for nparties < nparty_max
    for n in range(nparties, nparty_max):
        prefix = f'P{n+1}'
        analyzed[f'{prefix}_Age/Sex'].append('')
        analyzed[f'{prefix}_Type'].append('')
        analyzed[f'{prefix}_Dir'].append('')
        analyzed[f'{prefix}_Movement'].append('')
        analyzed[f'{prefix}_Fault'].append('')
        analyzed[f'{prefix}_Sobriety'].append('')
        analyzed[f'{prefix}_Drugs'].append('')
        analyzed[f'{prefix}_Other Associated Factors'].append('')
        analyzed[f'{prefix}_Other Associated Violation'].append('')
        analyzed[f'{prefix}_OAF_CVC'].append('')
    
    # Pull out relevant victim data
    nvictims = len(victims)
    for n in range(nvictims):
        v_party = 'P' + victims[n]['party_number']
        v_role = decode_role(int(victims[n]['victim_role']))
        v_injury = decode_injury(int(victims[n]['victim_degree_of_injury']))
        
        prefix = f'V{n+1}'
        if VERBOSE:
            print(f"{prefix}_Party:{v_party} {prefix}_Role:{v_role} {prefix}_Injury:{v_injury}")
        analyzed[f'{prefix}_Party'].append(v_party)
        analyzed[f'{prefix}_Role'].append(v_role)
        analyzed[f'{prefix}_Injury'].append(v_injury)
        
    #  Fill in nulls for nvictims < nvictim_max
    for n in range(nvictims, nvictim_max):
        prefix = f'V{n+1}'
        analyzed[f'{prefix}_Party'].append('')
        analyzed[f'{prefix}_Role'].append('')
        analyzed[f'{prefix}_Injury'].append('')
                
    return analyzed
    
def split_hhmm(time_digits):
    # reformat time hhmm as hh:mm
    if len(time_digits) == 4:
        time = time_digits[0:2] + ':' + time_digits[2:]
    elif len(time_digits) == 3:
        time = time_digits[0:1] + ':' + time_digits[1:]
    elif len(time_digits) == 2:
        time = '0:' + time_digits[0:]
    elif len(time_digits) == 1:
        time = '0:0' + time_digits[0]
    else:
        time = time_digits
    return time

def split_YMD(date_digits):
    # reformat date yyyymmdd as mm/dd/yyyy
    if len(date_digits) == 8:
        date = date_digits[4:6] + '/' + date_digits[6:]+  '/' + date_digits[0:4]
    else:
        print(f"WARNING! - unrecognzable date={date_digits}")
        date = date_digits
    return date
      
def decode_weather(code):
    if code == 'A':
        weather = 'Clear'
    elif code == 'B':
        weather = 'Cloudy'
    elif code == 'C':
        weather = 'Raining'
    elif code == 'D':
        weather = 'Snowing'
    elif code == 'E':
        weather = 'Fog'
    elif code == 'F':
        weather = 'Other'
    elif code == 'G':
        weather = 'Wind'
    else:
        weather = ''

    return weather
    
def decode_surface(code):
    if code == 'A':
        surface = 'Dry'
    elif code == 'B':
        surface = 'Wet'
    elif code == 'C':
        surface = 'Icy or Snowy'
    elif code == 'D':
        surface = 'Slippery'
    else:
        surface = 'Not Stated'

    return surface
    
def decode_collision(code):
    if code == 'A':
        collision_type = 'Head-On'
    elif code == 'B':
        collision_type = 'Sideswipe'
    elif code == 'C':
        collision_type = 'Rear End'
    elif code == 'D':
        collision_type = 'Broadside'
    elif code == 'E':
        collision_type = 'Hit Object'
    elif code == 'F':
        collision_type = 'Overturned'
    elif code == 'G':
        collision_type = 'Vehicle/Pedestrian'
    elif code == 'H':
        collision_type = 'Other'
    else:
        collision_type = 'Not Stated'
    
    return collision_type
    
def decode_hit_run(code):
    if code == 'F':
        hit_run = 'Felony'
    elif code == 'M':
        hit_run = 'Misdemeanor'
    else:
        hit_run = 'No'    
    return hit_run    
    
def decode_pcf(primary_collision_factor, pcf_violation_category):
    if primary_collision_factor == 'A':
        if pcf_violation_category == '01':
            pcf = 'DUI'
        elif pcf_violation_category == '02':
            pcf = 'Impeding Traffic'
        elif pcf_violation_category == '03':
            pcf = 'Unsafe Speed'
        elif pcf_violation_category == '04':
            pcf = 'Following Too Closely'
        elif pcf_violation_category == '05':
            pcf = 'Wrong Side of Road'
        elif pcf_violation_category == '06':
            pcf = 'Improper Passing'
        elif pcf_violation_category == '07':
            pcf = 'Unsafe Lane Change'
        elif pcf_violation_category == '08':
            pcf = 'Improper Turning'
        elif pcf_violation_category == '09':
            pcf = 'Automobile Right of Way'
        elif pcf_violation_category == '10':
            pcf = 'Pedestrian Right of Way'
        elif pcf_violation_category == '11':
            pcf = 'Pedestrian Violation'
        elif pcf_violation_category == '12':
            pcf = 'Traffic Signals and Signs'
        elif pcf_violation_category == '13':
            pcf = 'Hazardous Parking'
        elif pcf_violation_category == '14':
            pcf = 'Lights'
        elif pcf_violation_category == '15':
            pcf = 'Brakes'
        elif pcf_violation_category == '16':
            pcf = 'Other Equipment'
        elif pcf_violation_category == '17':
            pcf = 'Other Hazardous Violation'
        elif pcf_violation_category == '18':
            pcf = 'Other Than Driver (or Pedestrian)'
        elif pcf_violation_category == '19':
            pcf = ' '
        elif pcf_violation_category == '20':
            pcf = ' '
        elif pcf_violation_category == '21':
            pcf = 'Unsafe Starting or Backing'
        elif pcf_violation_category == '22':
            pcf = 'Other Improper Driving'
        elif pcf_violation_category == '23':
            pcf = 'Pedestrian/Other Under Influence'
        elif pcf_violation_category == '24':
            pcf = 'Fell Asleep'
        elif pcf_violation_category == '00':
            pcf = 'Unknown'
        else:
            pcf = 'Not Stated'
            
    elif primary_collision_factor == 'B':
        pcf = 'Other Improper Driving'
    elif primary_collision_factor == 'C':
        pcf = 'Other Than Driver'
    elif primary_collision_factor == 'D':
        pcf = 'Unknown'
    elif primary_collision_factor == 'E':
        pcf = 'Fell Asleep'
    else:
        pcf = 'Not Stated'
    
    return pcf
    
def decode_severity(code):
    if code == 1:
        severity = 'Fatal'
    elif code == 2:
        severity = 'Injury (Severe)'
    elif code == 3:
        severity = 'Injury (Other Visible)'
    elif code == 4:
        severity = 'Injury (Complaint of Pain)'
    elif code == 0:
        severity = 'Property Damage Only'
    return severity
    
def decode_party_type(code):
    if code == 1:
        type = 'DRVR'
    elif code == 2:
        type = 'PED'
    elif code == 3:
        type = 'PARKED'
    elif code == 4:
        type = 'BICY'
    elif code == 5:
        type = 'Other'
    else:
        type = 'Not Stated'
    return type
    
def decode_sobriety(code):
    if code == 'A':
        sobriety = 'Had Not Been Drinking'
    elif code == 'B':
        sobriety = 'Had Been Drinking, Under Influence'
    elif code == 'C':
        sobriety = 'Had Been Drinking, Not Under Influence'
    elif code == 'D':
        sobriety = 'Had Been Drinking, Impairment Unknown'
    elif code == 'G':
        sobriety = 'Impairment Unknown'
    elif code == 'H':
        sobriety = 'Not Applicable'
    else:
        sobriety = ''

    return sobriety

def decode_drugs(code):
    if code == 'E':
        drugs = 'Under Drug Influence'
    elif code == 'F':
        drugs = 'Impairment - Physical'
    elif code == 'H':
        drugs = 'Not Applicable'
    elif code == 'I':
        drugs = 'Sleepy/Fatigued'
    else:
        drugs = ''

    return drugs
    
def decode_oaf(code):
    if code == 'A':
        oaf = 'Violation'
    elif code == 'E':
        oaf = 'Vision Obscurements'
    elif code == 'F':
        oaf = 'Inattention'
    elif code == 'G':
        oaf = 'Stop and Go Traffic'
    elif code == 'H':
        oaf = 'Entering/Leaving Ramp'
    elif code == 'I':
        oaf = 'Previous Collision'
    elif code == 'J':
        oaf = 'Unfamiliar With Road'
    elif code == 'K':
        oaf = 'Defective Vehicle Equipment'
    elif code == 'L':
        oaf = 'Uninvolved Vehicle'
    elif code == 'M':
        oaf = 'Other'
    elif code == 'O':
        oaf = 'Runaway Vehicle'
    elif code == 'P':
        oaf = 'Inattention, Cell Phone'
    elif code == 'Q':
        oaf = 'Inattention, Electronic Equip.'
    elif code == 'R':
        oaf = 'Inattention, Radio/CD'
    elif code == 'S':
        oaf = 'Inattention, Smoking'
    elif code == 'T':
        oaf = 'Inattention, Eating'
    elif code == 'U':
        oaf = 'Inattention, Children'
    elif code == 'V':
        oaf = 'Inattention, Animal'
    elif code == 'W':
        oaf = 'Inattention, Personal Hygiene'
    elif code == 'X':
        oaf = 'Inattention, Reading'
    elif code == 'Y':
        oaf = 'Inattention, Other'
    else:
        oaf = ''

    return oaf
    
def decode_oaf_violation(code):
    if code == '01':
        oaf_viol = 'Under Influence in Public (647F)'
    elif code == '02':
        oaf_viol = 'County Ordinance'
    elif code == '03':
        oaf_viol = 'City Ordinance'
    elif code == '05':
        oaf_viol = 'Business/Professions Code'
    elif code == '06':
        oaf_viol = 'Felony Penal Code'
    elif code == '08':
        oaf_viol = 'Controlled Substances (Felony Health and Safety)'
    elif code == '09':
        oaf_viol = 'Health/Safety Code (Misdemeanor)'
    elif code == '10':
        oaf_viol = 'Penal Code (Misdemeanor)'
    elif code == '11':
        oaf_viol = 'Streets/Highways Code'
    elif code == '13':
        oaf_viol = 'Welfare/Institutions Code'
    elif code == '15':
        oaf_viol = 'Manslaughter'
    elif code == '16':
        oaf_viol = 'Unspecified Non-Vehicle Code'
    elif code == '17':
        oaf_viol = 'Fish & Game Code'
    elif code == '18':
        oaf_viol = 'Agriculture Code'
    elif code == '19':
        oaf_viol = 'Hit and Run'
    elif code == '20':
        oaf_viol = 'Driving or Bicycling Under the Influence'
    elif code == '21':
        oaf_viol = 'Improper Lane Change'
    elif code == '22':
        oaf_viol = 'Impeding Traffic'
    elif code == '23':
        oaf_viol = 'Failure to Heed Stop Signal'
    elif code == '24':
        oaf_viol = 'Failure to Heed Stop Sign'
    elif code == '25':
        oaf_viol = 'Unsafe Speed'
    elif code == '26':
        oaf_viol = 'Reckless Driving'
    elif code == '27':
        oaf_viol = 'Wrong Side of Road'
    elif code == '28':
        oaf_viol = 'Unsafe Lane Change'
    elif code == '29':
        oaf_viol = 'Improper Passing'
    elif code == '30':
        oaf_viol = 'Following Too Closely'
    elif code == '31':
        oaf_viol = 'Improper Turning'
    elif code == '33':
        oaf_viol = 'Automobile Right-of-Way'
    elif code == '34':
        oaf_viol = 'Pedestrian Right-of-Way'
    elif code == '35':
        oaf_viol = 'Pedestrian Violation'
    elif code == '37':
        oaf_viol = ' '
    elif code == '38':
        oaf_viol = 'Hazardous Parking'
    elif code == '39':
        oaf_viol = 'Lights'
    elif code == '40':
        oaf_viol = 'Brakes'
    elif code == '43':
        oaf_viol = 'Other Equipment'
    elif code == '44':
        oaf_viol = 'Other Hazardous Movement'
    elif code == '46':
        oaf_viol = 'Improper Registration'
    elif code == '47':
        oaf_viol = 'Other Non-Moving Violation'
    elif code == '48':
        oaf_viol = 'Excessive Smoke'
    elif code == '49':
        oaf_viol = 'Excessive Noise'
    elif code == '50':
        oaf_viol = 'Overweight'
    elif code == '51':
        oaf_viol = 'Oversize'
    elif code == '52':
        oaf_viol = 'Over Maximum Speed'
    elif code == '53':
        oaf_viol = 'Unsafe Starting or Backing'
    elif code == '60':
        oaf_viol = 'Off-Highway Vehicle Violation'
    elif code == '61':
        oaf_viol = 'Child Restraint'
    elif code == '62':
        oaf_viol = 'Seat Belt'
    elif code == '63':
        oaf_viol = 'Seat Belt (Equipment)'
    elif code == '00':
        oaf_viol = ' '
    else:
        oaf_viol = ' '

    return oaf_viol
    
def decode_movement(code):
    if code == 'A':
        movement = 'Stopped'
    elif code == 'B':
        movement = 'Proceeding Straight'
    elif code == 'C':
        movement = 'Ran Off Road'
    elif code == 'D':
        movement = 'Making Right Turn'
    elif code == 'E':
        movement = 'Making Left Turn'
    elif code == 'F':
        movement = 'Making U-Turn'
    elif code == 'G':
        movement = 'Backing'
    elif code == 'H':
        movement = 'Slowing/Stopping'
    elif code == 'I':
        movement = 'Passing Other Vehicle'
    elif code == 'J':
        movement = 'Changing Lanes'
    elif code == 'K':
        movement = 'Parking Maneuver'
    elif code == 'L':
        movement = 'Entering Traffic'
    elif code == 'M':
        movement = 'Other Unsafe Turning'
    elif code == 'N':
        movement = 'Crossed Into Opposing Lane'
    elif code == 'O':
        movement = 'Parked'
    elif code == 'P':
        movement = 'Merging'
    elif code == 'Q':
        movement = 'Traveling Wrong Way'
    elif code == 'R':
        movement = 'Other'
    else:
        movement = ''

    return movement

def decode_role(code):
    if code == 1:
        role = 'Driver'
    elif code == 2:
        role = 'Passenger'
    elif code == 3:
        role = 'Pedestrian'
    elif code == 4:
        role = 'Bicyclist'
    elif code == 5:
        role = 'Other'
    elif code == 6:
        role = 'Non-Injured Party'
    else:
        role = ''
    return role
    
def decode_injury(code):
    if code == 1:
        injury = 'Killed'
    elif code == 2:
        injury = 'Severe Injury'
    elif code == 3:
        injury = 'Other Visible Injury'
    elif code == 4:
        injury = 'Complaint of Pain'
    else:
        injury = ''
    return injury

# End helper functions ---------------------------------------------------------

def main():

    # read data from SWITRS raw data files
    crashes, crash_keys  = getDataCsv(crashes_file, ',', pivot=True)
    parties, party_keys  = getDataCsv(parties_file, ',', pivot=True)
    victims, victim_keys = getDataCsv(victims_file, ',', pivot=True)
    
    # quickly determine max #parties, #victims for all crash records
    nparty_max  = 0
    nvictim_max = 0
    for crash in crashes:
        crash_parties = get_parties(crash['case_id'], parties)
        crash_victims = get_victims(crash['case_id'], victims)
        if len(crash_parties) > nparty_max: nparty_max = len(crash_parties)
        if len(crash_victims) > nvictim_max: nvictim_max = len(crash_victims)
    
    # distill data for each crash
    n = 0
    analyzed = defaultdict(list)
    for crash in crashes:
        crash_parties = get_parties(crash['case_id'], parties)
        crash_victims = get_victims(crash['case_id'], victims)
        n+=1
        if VERBOSE:
            print(f"\nCrash {n} --  #parties: {len(crash_parties)}   #victims: {len(crash_victims)} ")
        
        analyzed = distill(crash, crash_parties, crash_victims, analyzed, nparty_max, nvictim_max)
        
    # save analyzed dictionary to CSV file
    dumpDictToCSV(analyzed, out_file, ',',  list(analyzed.keys()))
    print(f"\nOutput saved in {out_file}")
        
# Main body
if __name__ == '__main__':
    main()