import numpy as np

def createCrashPlacemarks( crashes, kmlFile ):
    # Bypass xml writing tools in python as the structure of the output
    # KML is very straightforward and faster to write directly.
    
    # kml document header
    fobj=open(kmlFile, 'w')
    kmlPlacemarkHeader(fobj)
    
    # Add a placemark with max injury severity color and description for each crash
    for crash in crashes:
        putPlaceMark(fobj, crash)

    # close kmlDocument
    closeKmlDocument(fobj)

def putPlaceMark(fobj, crash):

    # grab key data for description popup and placemark color style
    cid = crash['CollisionId']
    date_time = crash['Crash Date-Time']
    city = crash['City']
    c_type = crash['Collision Type']
    pcf    = crash['Primary Collision Factor']
    num_parties = int(crash['Num Parties'])
    num_injured = crash['Num Injured']
    num_killed  = crash['Num Killed']
    prim_road   = crash['Primary Road']
    second_road = crash['Secondary Road']
    dir2nd      = crash['Secondary Dir']
    if len(crash['Secondary Dist ft'])>0:
        dist2nd = int(float(crash['Secondary Dist ft']))
    else:
        dist2nd = 0
    latitude = float(crash['Latitude'])
    longitude = float(crash['Longitude'])
    try:
        geosrc = crash['GeoSrc']
    except:
        geosrc = ''
    
    # Sift through parties for simple lists: party, injured, injury_extent
    party_list   = ''
    injured_list = ''
    injury_extent_list  = ''
    for n in range(num_parties):
        prefix = f'P{n+1}'
        party_list = party_list + crash[f'{prefix} Type'] + ', '
        if len(crash[f'{prefix} Assoc Injured list'])>0:
            injured_list = injured_list + crash[f'{prefix} Assoc Injured list'] + ', '
        if len(crash[f'{prefix} Assoc Injury Extent list'])>0:
            injury_extent_list = injury_extent_list + crash[f'{prefix} Assoc Injury Extent list'] + ', '
    # strip trailing comma and blank
    party_list   = party_list[0:-2]
    injured_list = injured_list[0:-2]
    injury_extent_list  = injury_extent_list[0:-2]

    # Color placemark by the maximum severity encountered
    if 'Fatal' in injury_extent_list:
        style = '#redPlacemark' 
    elif 'Serious' in injury_extent_list:
        style = '#purplePlacemark' 
    elif 'Minor' in injury_extent_list:
        style = '#orangePlacemark' 
    elif 'Possible' in injury_extent_list:
        style = '#yellowPlacemark' 
    else:
        style = '#greenPlacemark'  # no injuries, property damage only

    # write out the placemark tags appropriately indented
    blanks = ''.join(np.tile('  ',2))
    desc_indent = ''.join(np.tile('   ',4))
    fobj.write(blanks+'<Placemark>\n')
    fobj.write(blanks+'   <name>Collision Id: ' + cid + '</name>\n')				
    fobj.write(blanks+'   <description><![CDATA[\n')				
    fobj.write(f"{desc_indent}<div>\n")
    fobj.write(f"{desc_indent}  Date-Time: {date_time}<br>\n")
    fobj.write(f"{desc_indent}  City: {city}<br>\n")
    fobj.write(f"{desc_indent}  Collision Type: {c_type}<br>\n")
    fobj.write(f"{desc_indent}  Primary Collision Factor: {pcf}<br>\n")
    fobj.write(f"{desc_indent}  Primary Rd: {prim_road}<br>\n")
    if dist2nd != 0:
        fobj.write(f"{desc_indent}  Secondary Rd: {second_road}   {dist2nd} ft {dir2nd}<br>\n")
    else:
        fobj.write(f"{desc_indent}  Secondary Rd: {second_road}<br>\n")
    fobj.write(f"{desc_indent}  Parties: {party_list}<br>\n")
    if style != '#greenPlacemark':
        fobj.write(f"{desc_indent}  Injured: {injured_list}<br>\n")
        fobj.write(f"{desc_indent}  Injury Extent: {injury_extent_list}<br>\n")
    else:
        fobj.write(f"{desc_indent}  Property damage only<br>\n")
    fobj.write(f"{desc_indent}  [Lat,Lon]=[{latitude:.4f}, {longitude:.4f}] {geosrc}<br>\n")
    fobj.write(f"{desc_indent}</div>\n")
    fobj.write(blanks+'   ]]></description>\n')				
    fobj.write(blanks+'   <styleUrl>' + style + '</styleUrl>\n')
    fobj.write(blanks+'   <Point>\n')           
    fobj.write(blanks+'      <coordinates>' + str(longitude) + ',' + str(latitude) + ',0</coordinates>\n')
    fobj.write(blanks+'   </Point>\n')           
    fobj.write(blanks+'</Placemark>\n')

def kmlPlacemarkHeader(fobj):
    headerLines = [ '<?xml version="1.0" encoding="UTF-8"?>', \
    '<kml xmlns="http://www.opengis.net/kml/2.2">', \
    '<Document>', \
    '    <Style id="greenPlacemark">', \
    '    <IconStyle>', \
    '        <scale>1.1</scale>', \
    '        <Icon>', \
    '          <href>https://maps.google.com/mapfiles/ms/icons/green-dot.png</href>', \
    '        </Icon>', \
    '    </IconStyle>', \
    '    </Style>', \
    '    <Style id="yellowPlacemark">', \
    '    <IconStyle>', \
    '        <scale>1.1</scale>', \
    '        <Icon>', \
    '          <href>https://maps.google.com/mapfiles/ms/icons/yellow-dot.png</href>', \
    '        </Icon>', \
    '    </IconStyle>', \
    '    </Style>', \
    '    <Style id="orangePlacemark">', \
    '    <IconStyle>', \
    '        <scale>1.1</scale>', \
    '        <Icon>', \
    '          <href>https://maps.google.com/mapfiles/ms/icons/orange-dot.png</href>', \
    '        </Icon>', \
    '    </IconStyle>', \
    '    </Style>', \
    '    <Style id="purplePlacemark">', \
    '    <IconStyle>', \
    '        <scale>1.1</scale>', \
    '        <Icon>', \
    '          <href>https://maps.google.com/mapfiles/ms/icons/purple-dot.png</href>', \
    '        </Icon>', \
    '    </IconStyle>', \
    '    </Style>', \
    '    <Style id="redPlacemark">', \
    '    <IconStyle>', \
    '        <scale>1.1</scale>', \
    '        <Icon>', \
    '          <href>https://maps.google.com/mapfiles/ms/icons/red-dot.png</href>', \
    '        </Icon>', \
    '    </IconStyle>', \
    '    </Style>', \
    '    <name>Crash Placemarks</name>' ]
    
    # write header lines to file
    for n in range(len(headerLines)):
        fobj.write(headerLines[n]+'\n')

def closeKmlDocument(fobj):
    fobj.write('</Document>\n')
    fobj.write('</kml>\n')
    fobj.close()
