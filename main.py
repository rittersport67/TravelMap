import xml.etree.ElementTree as ET
import requests
import csv
from enum import Enum
import plotly.graph_objects as go

# Path to your XML file
xml_file = "/Users/seb/Documents/Python-Exercices/maps/trips.xml"

# Path to your CSV file
csv_file = "/Users/seb/Documents/Python-Exercices/maps/ISO-3166-Countries-with-Regional-Codes.csv"



CSV_HEADER = []
CSV_FRAME = []

LIST_STATUS = []

class status(Enum):
    NO_ERROR = 0
    COUNTRYCODE_NOT_FOUND = 1
    REQUEST_CITY_DATA_ERROR = 2
    LATITUDE_LONGITUDE_NOT_FOUND = 3

class Coordonates:
    def __init__(self,lattitude,longitude) -> None:
        self.lattitude = lattitude
        self.longitude = longitude


class Trip:
        def __init__(self, city, country):
            self.city = city
            self.country = country
            self.countrycode = None
        
        def __init__(self, city, country,coordonates : Coordonates):
            self.city = city
            self.country = country
            self.countrycode = None
            self.city_coordonates = coordonates

        def is_city_coordonates_defined(self):
            if self.city_coordonates.lattitude is not None and self.city_coordonates.longitude is not None:
                return True
            return False

        def add_lattitude(self, lattitude):
            self.city_coordonates.lattitude = lattitude
        
        def add_longitude(self, longitude):
            self.city_coordonates.longitude = longitude
        
        def add_countrycode(self, countrycode):
            self.countrycode = countrycode


class RawDataCountryWrapper:
    def __init__(self, name=None, alpha_2=None, alpha_3=None, country_code=None, iso_3166_2=None, region=None, sub_region=None, intermediate_region=None, region_code=None, sub_region_code=None, intermediate_region_code=None):
       self.name = name
       self.alpha_2 = alpha_2
       self.alpha_3 = alpha_3
       self.country_code = country_code
       self.iso_3166_2 = iso_3166_2
       self.region = region
       self.sub_region = sub_region
       self.intermediate_region = intermediate_region
       self.region_code = region_code
       self.sub_region_code = sub_region_code
       self.intermediate_region_code = intermediate_region_code

def get_list_of_countries_object():
    list_of_countries_object = []
    open_file = open(csv_file,'r')
    if len(CSV_HEADER) != number_user_attributes:
        print("The number of columns in the CSV file is not correct")
    else:
        for row in CSV_FRAME:
            country = RawDataCountryWrapper()
            for i in range(number_user_attributes):
                setattr(country, CSV_HEADER[i], row[i])
            list_of_countries_object.append(country)
    return list_of_countries_object

def get_countrycode(country,list_of_countries_object):
    for country_object in list_of_countries_object:
        if country_object.name == country:
            return country_object.alpha_2, status.NO_ERROR
    return None,status.COUNTRYCODE_NOT_FOUND

def retrieve_lat_lng(data, city):
    # Parse the XML data
    root = ET.fromstring(data)
    # Access the geoname elements
    for geoname in root.findall('geoname'):
        name = geoname.find('name').text
        if name == city:
            lat = geoname.find('lat').text
            lng = geoname.find('lng').text
            return lat, lng,status.NO_ERROR
    return None, None,status.LATITUDE_LONGITUDE_NOT_FOUND


def get_citydata(city, countrycode):
    url = f"http://api.geonames.org/search?q={city}&country={countrycode}&maxRows=10&username=rittersport67"
    response = requests.get(url)
    try: 
        data = response.content
        return data,status.NO_ERROR
    except Exception as e:
        return None,status.REQUEST_CITY_DATA_ERROR


# Read the CSV file
with open(csv_file, mode='r') as file:
    reader = csv.reader(file)

    CSV_HEADER = next(reader)  # Read the header row
 
    for row in reader:
        CSV_FRAME.append(row) # Access the data in each row
        
# Get the number of user attributes
number_user_attributes = len([a for a in dir(RawDataCountryWrapper()) if not a.startswith('__')])

list = get_list_of_countries_object()

# Parse the XML file
tree = ET.parse(xml_file)

# Get the root element
root = tree.getroot()


# Access elements and attributes in the XML file
for element in root:
    # Access elements and attributes in the XML file
    trips = []
    for trip in root:
        city = trip.find("city").text
        country = trip.find("country").text
        latitude = trip.find("latitude").text if trip.find("latitude") is not None else None
        longitude = trip.find("longitude").text if trip.find("longitude") is not None else None
        trip = Trip(city, country,Coordonates(latitude,longitude))
        trips.append(trip)
        if not trip.is_city_coordonates_defined():
            countrycode,status = get_countrycode(country,list)
            if status == status.NO_ERROR:
                trip.add_countrycode(countrycode)   
                data,status = get_citydata(trip.city,trip.countrycode)
                if status == status.NO_ERROR:
                    lat,lng,status = retrieve_lat_lng(data,trip.city)
                    ET.SubElement(trip,"latitude")
                    for child in trip:
                        if child.tag == "latitude":
                            child.text = lat
                    ET.SubElement(trip,"longitude")
                    for child in trip:
                        if child.tag == "longitude":
                            child.text = lng
            tree.write(xml_file)




