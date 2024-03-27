import requests
import json
import time
import re
import csv
from geopy.geocoders import Nominatim

def getwebinfo(url): 
    '''
    Returns a list
    [0] = Instagram
    [1] = Email
    '''
    try: 
        result = []
        # Send a GET request to the website
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            print("______Success______")

            # Extract all text from the website
            website_text = response.text
            #print(website_text)

            # Instagram Regex Search
            regex_pattern = r'https:\/\/www.instagram.com\/[a-zA-Z0-9_]+\/?'
            matches = re.findall(regex_pattern, website_text)
            for match in matches:
                if match != "https://www.instagram.com/p/":
                    print(match)
                    ans = input("(y/n) Instagram: ")
                    if ans == 'y':
                        result.append(match)
                        break
            if len(result) == 0:
                result.append("FIND")

            #Email \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b
            regex_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            matches = re.findall(regex_pattern, website_text)
            for match in matches:
                print(match)
                ans = input("(y/n) Email: ")
                if ans == 'y':
                    result.append(match)
                    break
            if len(result) == 1:
                result.append("")
        return result
    except Exception as e:
        # Code to handle any other exceptions
        print(f"An error occurred: {str(e)}")
        return result



def get_coordinates(city):
    try:
        geolocator = Nominatim(user_agent="my-app")  # Initialize geocoder
        location = geolocator.geocode(city)  # Retrieve location information

        if location:
            latitude = location.latitude
            longitude = location.longitude
            return latitude, longitude
        else:
            return None
    except Exception as e:
        print(f"An error occurred during geocoding: {str(e)}")
        return None


def google_places_details(api_key, place_id):
    print("Getting Details for: " + place_id)
    base_url = "https://maps.googleapis.com/maps/api/place/details/json?"
    place_id = "place_id=" + place_id
    fields = "&fields=name,website,formatted_address,formatted_phone_number"
    key = "&key=" + api_key

    request_url = base_url + place_id + fields + key

    response = requests.get(request_url).json()
    
    if response['status'] == 'OK':
        print("Success")
        return response['result']
    else:
        return None

def google_places_search(api_key, query, location, radius=50000, num_pages=1):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    query = "query=" + query
    location = "&location=" + location
    radius = "&radius=" + str(radius)
    key = "&key=" + api_key

    results = []

    for page in range(num_pages + 1):
        request_url = base_url + query + location + radius + key

        if page > 0:
            request_url += "&pagetoken=" + next_page_token

        response = requests.get(request_url).json()

        if 'results' in response:
            results += response['results']

        if 'next_page_token' not in response:
            break

        next_page_token = response['next_page_token']

    return results







###### Main
api_key = "AIzaSyCgMuoR9-O9Y4raUBjptBDa9HaXMbGFT_o"
query = "casinos in Reno"

city = "Reno"
cresults = get_coordinates(city)
coords = string_result = ' '.join(str(item) for item in cresults)

print("Getting info for", city , " at coordinates: ", coords)

# Query top 40 clubs
data = google_places_search(api_key, query, coords, radius=50000, num_pages=6)
print(len(data))

clubList = []
placeIdList =[]

# For every element in results, say yes, no, to include it or not
count = 1
for element in data:
    print(count)
    print(element["name"])
    addToList = input("Add to list? (y/n)")
    
    if(addToList == 'y'):
        placeIdList.append(element["place_id"])
        print("Added!")
    print("___________________________________________________________________")
    count += 1


#Once All clubs have been approved, Begin the Detail Queries for each one 
for clubID in placeIdList:
    clubDictionary = {
        "name": "", 
        "website": "",
        "phone": 0,
        "email": "",
        "address": "",
        "ig": ""
    }
    detailResponse = google_places_details(api_key, clubID)
    print(detailResponse)
    clubDictionary["name"] = detailResponse.get('name','N/A')
    clubDictionary["website"] = detailResponse.get('website','N/A')
    clubDictionary["phone"]= detailResponse.get('formatted_phone_number','N/A')
    clubDictionary["address"]= detailResponse.get('formatted_address','N/A')

    if(clubDictionary["website"] != 'N/A'):
        list = getwebinfo(clubDictionary["website"])
        if len(list) != 0:
            clubDictionary["ig"] = list[0]
            clubDictionary["email"] = list[1]
        
    clubList.append(clubDictionary)
  

#Once All details are filled, Write approved data to a csv for pasting 
csv_file = city + ".csv"

# Write to CSV
with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=clubList[0].keys())
    writer.writeheader()
    for data in clubList:
        writer.writerow(data)