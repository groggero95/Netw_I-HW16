#!/usr/bin/python
import os
import socket
import geocoder
import gmplot
import csv
import sys
import webbrowser
import socket
import geoip2.database
import sqlite3
import pandas.io.sql as sql

## Many thanks to Rehan Rajput for helping us with the usage of GMaps API

#Put your own API keys here: get it -> https://cloud.google.com/maps-platform/
# WARNING: without API keys, it won't work!
API_KEY = "AIzaSyB5a50hwGReYBheMsFwcrlPVBp8BU_g8Uk"
EURECOM=(43.614452, 7.071345)
reader_city = geoip2.database.Reader('./GeoLite2-City.mmdb')
reader_asn = geoip2.database.Reader('./GeoLite2-ASN.mmdb')


# Convert the SQL database into a more easily manageable .CSV file
def SQLtoCSV(browser='firefox', filein='cookies.sqlite', fileout='out.csv'):
	con = sqlite3.connect(filein)
	if browser=='firefox':
		table = sql.read_sql('select baseDomain from moz_cookies', con)
	elif browser=='chrome':
		table=sql.read_sql('select host_key from cookies', con)
	table.to_csv(fileout)


# Open the .csv file containing the DB of the host of the cookies
# Input the file name, return a list of IPs as set so that duplicated elements are not contained
def DBtoIPs(filename='out.csv'):
	IPs=[]
	with open((str(filename))) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for i, line in enumerate(csv_reader):
			print line
			if i != 0:
				try:	
					print len(line)
    					IPs.append(socket.gethostbyname(line[1]))
    				except socket.gaierror, IndexError:
    					pass
    	return set(IPs)

# Converts IP -> Geocode, using GeoIP2 database
# Input a single IP or a list containing IPs
# Returns single cordinates or list with location and company name
def FromIPtoLatLon(ips):
        locs = []
        for x in ips:
            try:
            	response_c=reader_city.city(x)
            	response_a=reader_asn.asn(x)
            	locs.append((response_c.location.latitude, response_c.location.longitude))
            	#locs.append((response_c.location.latitude, response_c.location.longitude, response_a.autonomous_system_organization))
            except geoip2.errors.AddressNotFoundError:
            	# do nothing in case of errors
            	pass
        return set(locs)



# Converts IP -> Geocode, using geocoder
# Input a single IP or a list containing IPs
# Returns single cordinates or list
def FromIPtoGeoCode(ips):
    if(type(ips) == list):
        ret = []
        for x in ips:
            pos = geocoder.ip(x).latlng
            ret.append((pos[0],pos[1]))
            	#sleep(1) #to avoid hitting API limit
            #except IndexError:
            #	pass
        return ret
    pos = geocoder.ip(ips).latlng
    return (pos[0],pos[1])

# Converts location -> Geocode
# Input a single item or list
# Returns single coordiantes or list
def FromNametoGeocode(addresses):
    if(type(addresses) == list):
        ret = []
        for x in addresses:
            pos = geocoder.google(x,key=API_KEY).latlng
            try:
            	ret.append((pos[0],pos[1]))
            	#sleep(1) #to avoid hitting API limit
            except IndexError:
            	pass
        return ret
    pos = geocoder.google(addresses,key=API_KEY).latlng
    return (pos[0],pos[1])

# Plot all the Geocode
# WARNING: needs a list in this format: [(lat1,long1), (lat2,long2)]
# Can receive as input the central point on the map (lat, long) and the name of output file
def PlotMap(positions,center=(),filename="map.html"):
    if(len(center) < 2):
        center = positions[0]
        positions.pop(0)
    filename = str(filename)
    gmap = gmplot.GoogleMapPlotter(center[0],center[1],8,apikey=API_KEY)
    for x in positions:
        gmap.marker(x[0],x[1])
    gmap.draw('./' + filename)
   
if __name__ == "__main__":
	map_name='map_cookies.html'
	
	if len(sys.argv) < 2:
		filesql='cookies.sqlite'
		browser='firefox'
	elif len(sys.argv) == 2:
		filesql=(sys.argv[1])
		browser='firefox'
	else:
		filesql=(sys.argv[1])
		browser=sys.argv[2]
        
        SQLtoCSV(browser, filesql)
	IP_list=DBtoIPs()
	GEO_pos=list(FromIPtoLatLon(IP_list))
	print GEO_pos
	PlotMap(GEO_pos, EURECOM, map_name)
	map_open = 'file:///'+os.getcwd()+'/' + map_name
	webbrowser.open_new_tab(map_open)
	
