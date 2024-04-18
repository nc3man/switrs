#!/user/bin/env python3 -tt

# Imports
from collections import defaultdict
from dumpDictToCSV import dumpDictToCSV
from getDataCsv import getDataCsv

# User variables
inpath = 'C:/Users/karl/bike/vista/'
crashes_file = inpath + 'Crashes_bike.csv'
parties_file = inpath + 'Parties_bike.csv'
victims_file = inpath + 'Victims_bike.csv'
out_file = inpath + 'SWITRS_Vista_2018-2023.csv'

# Do not edit below this line --------------------------------------------------

# Function declarations

def get_parties(case_id, parties):
    party_found = []
    for party in parties:
        if party['CASE_ID'] == case_id:
            party_found.append(party) 
    
    # ensure that the party_found list is in PARTY_NUMBER order
    parties_found = []
    for n in range(len(party_found)):
        for party in party_found:
            if int(party['PARTY_NUMBER']) == n+1:
                parties_found.append(party)
        
    return parties_found
    
def get_victims(case_id, victims):
    victim_found = []
    for victim in victims:
        if victim['CASE_ID'] == case_id:
            victim_found.append(victim)
    return victim_found
    
def split_hhmm(time_digits):
    # format 4-digit time hhmm as hh:mm
    if len(time_digits) == 4:
        time = time_digits[0:2] + ':' + time_digits[2:]
    else:
        time = time_digits
    return time
        
def distill(crash, parties, victims, analyzed):
    case_id = crash['CASE_ID']
    year = crash['ACCIDENT_YEAR']
    date = crash['COLLISION_DATE']
    time = split_hhmm(crash['COLLISION_TIME'])
    if crash['INTERSECTION'] == 'Y':
        location = crash['PRIMARY_RD'] + ' @ ' + crash['SECONDARY_RD']
    else:
        location = crash['PRIMARY_RD'] + ' ' + crash['DISTANCE'] + 'ft ' \
        + crash['DIRECTION'] + ' ' + crash['SECONDARY_RD']
    collision_type = decode_collision(crash['TYPE_OF_COLLISION'])
    weather = decode_weather(crash['WEATHER_1'])
    if len(decode_weather(crash['WEATHER_2'])) > 0:
        weather = weather + ' & ' + decode_weather(crash['WEATHER_2'])
    surface = decode_surface(crash['ROAD_SURFACE'])
    weather_surface = weather + ' / ' + surface
    pcf = decode_pcf(crash['PRIMARY_COLL_FACTOR'], crash['PCF_VIOL_CATEGORY'])
    pcf_viol = crash['PCF_VIOLATION'] + '.' + crash['PCF_VIOL_SUBSECTION']
    severity = decode_severity(int(crash['COLLISION_SEVERITY']))
    int_turn = crash['INTERSECTION']
    hit_run = decode_hit_run(crash['HIT_AND_RUN'])
    
    # add to output dictionary
    analyzed['Case_ID'].append(case_id)
    analyzed['Year'].append(year)
    analyzed['Date'].append(date)
    analyzed['Time'].append(time)
    analyzed['Location'].append(location)
    analyzed['Weather/Surface'].append(weather_surface)
    analyzed['Collision Type'].append(collision_type)
    analyzed['Primary Collision Factor'].append(pcf)
    analyzed['PCF Violation'].append(pcf_viol)
    analyzed['Int/Turn'].append(int_turn)
    analyzed['Hit & Run'].append(hit_run)
    analyzed['Severity'].append(severity)

    print(f"CaseID:{case_id} Year:{year} Date:{date} time:{time} Location:{location} Weather/Surface:{weather_surface} Collision_Type:{collision_type} PCF:{pcf} PCF_Violation:{pcf_viol} Int/Turn:{int_turn} Hit_Run:{hit_run} Severity:{severity}")

    # Pull out relevant party data
    nparties = len(parties)
    p1_age_sex = parties[0]['PARTY_AGE'] + '/' + parties[0]['PARTY_SEX']
    p1_dir = parties[0]['DIR_OF_TRAVEL']
    p1_movement = decode_movement(parties[0]['MOVE_PRE_ACC'])
    p1_type = decode_party_type(int(parties[0]['PARTY_TYPE']))
    p1_fault = parties[0]['AT_FAULT']
    p1_sobriety = decode_sobriety(parties[0]['PARTY_SOBRIETY'])
    p1_drugs = decode_drugs(parties[0]['PARTY_DRUG_PHYSICAL'])
    p1_oaf = decode_oaf(parties[0]['OAF_1'])
    p1_oaf_2 = decode_oaf(parties[0]['OAF_2'])
    if len(p1_oaf_2) > 0:
        p1_oaf = p1_oaf + ' / ' + p1_oaf_2
    p1_oaf_viol = decode_oaf_violation(parties[0]['OAF_VIOL_CAT'])
    p1_oaf_viol_cvc = parties[0]['OAF_VIOL_SECTION'] + '.' + parties[0]['OAF_VIOLATION_SUFFIX']
    print(f"P1_Age/Sex:{p1_age_sex} P1_Type:{p1_type} P1_Dir:{p1_dir} P1_Movement:{p1_movement} P1_Fault:{p1_fault} P1_Sobriety:{p1_sobriety} P1_Drugs:{p1_drugs} P1_Other Associated Factors:{p1_oaf} P1_Other Associated Violation:{p1_oaf_viol} P1_OAF_CVC:{p1_oaf_viol_cvc}")
    
    analyzed['P1_Age/Sex'].append(p1_age_sex)
    analyzed['P1_Type'].append(p1_type)
    analyzed['P1_Dir'].append(p1_dir)
    analyzed['P1_Movement'].append(p1_movement)
    analyzed['P1_Fault'].append(p1_fault)
    analyzed['P1_Sobriety'].append(p1_sobriety)
    analyzed['P1_Drugs'].append(p1_drugs)
    analyzed['P1_Other Associated Factors'].append(p1_oaf)
    analyzed['P1_Other Associated Violation'].append(p1_oaf_viol)
    analyzed['P1_OAF_CVC'].append(p1_oaf_viol_cvc)
    
    
    if nparties > 1:
        p2_age_sex = parties[1]['PARTY_AGE'] + '/' + parties[1]['PARTY_SEX']
        p2_dir = parties[1]['DIR_OF_TRAVEL']
        p2_movement = decode_movement(parties[1]['MOVE_PRE_ACC'])
        p2_type = decode_party_type(int(parties[1]['PARTY_TYPE']))
        p2_fault = parties[1]['AT_FAULT']
        p2_sobriety = decode_sobriety(parties[1]['PARTY_SOBRIETY'])
        p2_drugs = decode_drugs(parties[1]['PARTY_DRUG_PHYSICAL'])
        p2_oaf = decode_oaf(parties[1]['OAF_1'])
        p2_oaf_2 = decode_oaf(parties[1]['OAF_2'])
        if len(p2_oaf_2) > 0:
            p2_oaf = p2_oaf + ' / ' + p2_oaf_2
        p2_oaf_viol = decode_oaf_violation(parties[1]['OAF_VIOL_CAT'])
        p2_oaf_viol_cvc = parties[1]['OAF_VIOL_SECTION'] + '.' + parties[1]['OAF_VIOLATION_SUFFIX']
        print(f"P2_Age/Sex:{p2_age_sex} P2_Type:{p2_type} P2_Dir:{p2_dir} P2_Movement:{p2_movement} P2_Fault:{p2_fault} P2_Sobriety:{p2_sobriety} P2_Drugs:{p2_drugs} P2_Other Associated Factors:{p2_oaf} P2_Other Associated Violation:{p2_oaf_viol} P2_OAF_CVC:{p2_oaf_viol_cvc}")
        
        analyzed['P2_Age/Sex'].append(p2_age_sex)
        analyzed['P2_Type'].append(p2_type)
        analyzed['P2_Dir'].append(p2_dir)
        analyzed['P2_Movement'].append(p2_movement)
        analyzed['P2_Fault'].append(p2_fault)
        analyzed['P2_Sobriety'].append(p2_sobriety)
        analyzed['P2_Drugs'].append(p2_drugs)
        analyzed['P2_Other Associated Factors'].append(p2_oaf)
        analyzed['P2_Other Associated Violation'].append(p2_oaf_viol)
        analyzed['P2_OAF_CVC'].append(p2_oaf_viol_cvc)
                       
    if nparties > 2:
        p3_age_sex = parties[2]['PARTY_AGE'] + '/' + parties[2]['PARTY_SEX']
        p3_dir = parties[2]['DIR_OF_TRAVEL']
        p3_movement = decode_movement(parties[2]['MOVE_PRE_ACC'])
        p3_type = decode_party_type(int(parties[2]['PARTY_TYPE']))
        p3_fault = parties[2]['AT_FAULT']        
        p3_sobriety = decode_sobriety(parties[2]['PARTY_SOBRIETY'])
        p3_drugs = decode_drugs(parties[2]['PARTY_DRUG_PHYSICAL'])
        p3_oaf = decode_oaf(parties[2]['OAF_1'])
        p3_oaf_2 = decode_oaf(parties[2]['OAF_2'])
        if len(p3_oaf_2) > 0:
            p3_oaf = p3_oaf + ' / ' + p3_oaf_2
        p3_oaf_viol = decode_oaf_violation(parties[2]['OAF_VIOL_CAT'])
        p3_oaf_viol_cvc = parties[2]['OAF_VIOL_SECTION'] + '.' + parties[2]['OAF_VIOLATION_SUFFIX']
        print(f"P3_Age/Sex:{p3_age_sex} P3_Type:{p3_type} P3_Dir:{p3_dir} P3_Movement:{p3_movement} P3_Fault:{p3_fault} P3_Sobriety:{p3_sobriety} P3_Drugs:{p3_drugs} P3_Other Associated Factors:{p3_oaf} P3_Other Associated Violation:{p3_oaf_viol} P3_OAF_CVC:{p3_oaf_viol_cvc}")
        
        analyzed['P3_Age/Sex'].append(p3_age_sex)
        analyzed['P3_Type'].append(p3_type)
        analyzed['P3_Dir'].append(p3_dir)
        analyzed['P3_Movement'].append(p3_movement)
        analyzed['P3_Fault'].append(p3_fault)
        analyzed['P3_Sobriety'].append(p3_sobriety)
        analyzed['P3_Drugs'].append(p3_drugs)
        analyzed['P3_Other Associated Factors'].append(p3_oaf)
        analyzed['P3_Other Associated Violation'].append(p3_oaf_viol)
        analyzed['P3_OAF_CVC'].append(p3_oaf_viol_cvc)
        
    # Fill in nulls for nparties < 3
    if nparties == 1:
        analyzed['P2_Age/Sex'].append('')
        analyzed['P2_Type'].append('')
        analyzed['P2_Dir'].append('')
        analyzed['P2_Movement'].append('')
        analyzed['P2_Fault'].append('')
        analyzed['P2_Sobriety'].append('')
        analyzed['P2_Drugs'].append('')
        analyzed['P2_Other Associated Factors'].append('')
        analyzed['P2_Other Associated Violation'].append('')
        analyzed['P2_OAF_CVC'].append('')
         
        analyzed['P3_Age/Sex'].append('')
        analyzed['P3_Type'].append('')
        analyzed['P3_Dir'].append('')
        analyzed['P3_Movement'].append('')
        analyzed['P3_Fault'].append('')
        analyzed['P3_Sobriety'].append('')
        analyzed['P3_Drugs'].append('')
        analyzed['P3_Other Associated Factors'].append('')
        analyzed['P3_Other Associated Violation'].append('')
        analyzed['P3_OAF_CVC'].append('')
                
    elif nparties == 2:
        analyzed['P3_Age/Sex'].append('')
        analyzed['P3_Type'].append('')
        analyzed['P3_Dir'].append('')
        analyzed['P3_Movement'].append('')
        analyzed['P3_Fault'].append('')
        analyzed['P3_Sobriety'].append('')
        analyzed['P3_Drugs'].append('') 
        analyzed['P3_Other Associated Factors'].append('')
        analyzed['P3_Other Associated Violation'].append('')
        analyzed['P3_OAF_CVC'].append('')
    
    # Pull out relevant victim data
    nvictims = len(victims)    
    if nvictims > 0:
        v1_party = 'P' + victims[0]['PARTY_NUMBER']
        v1_role = decode_role(int(victims[0]['VICTIM_ROLE']))
        v1_injury = decode_injury(int(victims[0]['VICTIM_DEGREE_OF_INJURY']))
        print(f"V1_Party:{v1_party} V1_Role:{v1_role} V1_Injury:{v1_injury}")
        analyzed['V1_Party'].append(v1_party)
        analyzed['V1_Role'].append(v1_role)
        analyzed['V1_Injury'].append(v1_injury)
        
    if nvictims > 1:
        v2_party = 'P' + victims[1]['PARTY_NUMBER']
        v2_role = decode_role(int(victims[1]['VICTIM_ROLE']))
        v2_injury = decode_injury(int(victims[1]['VICTIM_DEGREE_OF_INJURY']))       
        print(f"V2_Party:{v2_party} V2_Role:{v2_role} V2_Injury:{v2_injury}")
        analyzed['V2_Party'].append(v2_party)
        analyzed['V2_Role'].append(v2_role)
        analyzed['V2_Injury'].append(v2_injury)
   
    if nvictims > 2:
        v3_party = 'P' + victims[2]['PARTY_NUMBER']
        v3_role = decode_role(int(victims[2]['VICTIM_ROLE']))
        v3_injury = decode_injury(int(victims[2]['VICTIM_DEGREE_OF_INJURY']))       
        print(f"V3_Party:{v3_party} V3_Role:{v3_role} V3_Injury:{v3_injury}")
        analyzed['V3_Party'].append(v3_party)
        analyzed['V3_Role'].append(v3_role)
        analyzed['V3_Injury'].append(v3_injury)

    if nvictims > 3:
        v4_party = 'P' + victims[3]['PARTY_NUMBER']
        v4_role = decode_role(int(victims[3]['VICTIM_ROLE']))
        v4_injury = decode_injury(int(victims[3]['VICTIM_DEGREE_OF_INJURY']))       
        print(f"V4_Party:{v4_party} V4_Role:{v4_role} V4_Injury:{v4_injury}")
        analyzed['V4_Party'].append(v4_party)
        analyzed['V4_Role'].append(v4_role)
        analyzed['V4_Injury'].append(v4_injury)
        
    #  Fill in nulls for nvictims < 4
    if nvictims == 0:
        analyzed['V1_Party'].append('')
        analyzed['V1_Role'].append('')
        analyzed['V1_Injury'].append('')
        analyzed['V2_Party'].append('')
        analyzed['V2_Role'].append('')
        analyzed['V2_Injury'].append('')
        analyzed['V3_Party'].append('')
        analyzed['V3_Role'].append('')
        analyzed['V3_Injury'].append('')
        analyzed['V4_Party'].append('')
        analyzed['V4_Role'].append('')
        analyzed['V4_Injury'].append('')      
    elif nvictims == 1:
        analyzed['V2_Party'].append('')
        analyzed['V2_Role'].append('')
        analyzed['V2_Injury'].append('')
        analyzed['V3_Party'].append('')
        analyzed['V3_Role'].append('')
        analyzed['V3_Injury'].append('')
        analyzed['V4_Party'].append('')
        analyzed['V4_Role'].append('')
        analyzed['V4_Injury'].append('')
    elif nvictims == 2:
        analyzed['V3_Party'].append('')
        analyzed['V3_Role'].append('')
        analyzed['V3_Injury'].append('')
        analyzed['V4_Party'].append('')
        analyzed['V4_Role'].append('')
        analyzed['V4_Injury'].append('')
    elif nvictims == 3:
        analyzed['V4_Party'].append('')
        analyzed['V4_Role'].append('')
        analyzed['V4_Injury'].append('')
        
        
    return analyzed

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
        severity = 'PDO'
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
        sobriety = '-'

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
        drugs = '-'

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


def main():

    # read data from SWITRS raw data files
    crashes, crash_keys  = getDataCsv(crashes_file, ',', pivot=True)
    parties, party_keys  = getDataCsv(parties_file, ',', pivot=True)
    victims, victim_keys = getDataCsv(victims_file, ',', pivot=True)
    
    # distill data for each crash
    n = 0
    analyzed = defaultdict(list)
    for crash in crashes:
        crash_parties = get_parties(crash['CASE_ID'], parties)
        crash_victims = get_victims(crash['CASE_ID'], victims)
        
        n += 1
        print(f"\nCrash {n} --  #parties: {len(crash_parties)}   #victims: {len(crash_victims)} ")
        
        analyzed = distill(crash, crash_parties, crash_victims, analyzed)
        
    dumpDictToCSV(analyzed, out_file, ',',  list(analyzed.keys()))
    print(f"\nOutput saved in {out_file}")
        
# Main body
if __name__ == '__main__':
    main()