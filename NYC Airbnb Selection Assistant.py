# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 22:38:02 2019

@author: Nadeem Choudhury
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Import and drop unnecessary columns. Make sure to specify the correct directory in Line 15.
file = pd.read_csv('C:/Users/NadeemChoudhury/Documents/Python Works/NYC Airbnb Selection Assistant/listings.csv')
file = file.drop(columns = ['availability_365', 'calculated_host_listings_count', 'last_review', 'host_id', 'id', 'minimum_nights', 'reviews_per_month'])

#Create dictionary with number of Airbnbs in each borough. 
neighborhoodDict = dict(file.neighborhood_group.value_counts())

#Display pie chart of Airbnbs in each borough.
print('\nWelcome to the New York City Airbnb Selection Assistant!\n\nHere is the breakdown of the Airbnbs in New York City by borough.')   
pie = plt.pie([float(v) for v in neighborhoodDict.values()], labels=neighborhoodDict.keys(), textprops={'fontsize': 14}, autopct='%1.1f%%')
plt.title('Percentage of Airbnbs in NYC by Borough')
plt.show(pie)

#Obtain desired Airbnb location using Geopy from program user.
keys = list(neighborhoodDict.keys())
YN = 'n'
borough = None
while YN.lower() == 'n':
    location = input("Please enter an address, zipcode, or landmark that you would like to stay near?\n>>")
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    location = geolocator.geocode(location)
    while location == None:
        print('\nThis is not a valid location. Please try again.')
        location = input("Please enter an address, zipcode, or landmark that you would like to stay nearby?\n>>")
        geolocator = Nominatim(user_agent="specify_your_app_name_here")
        location = geolocator.geocode(location)
    print ("Is the following address correct?\n\n" + location.address + "\n")
    YN = input('Enter Y or N\n>>')
    for key in keys:
        if key in location.address:
            borough = key
    if borough == None:
        print('This location is not in New York City. Please try again.')
        YN = 'n'

#Compute distance between user input location and each Airbnb. Print distance of closest Airbnb.
coordinates = [location.latitude, location.longitude]
fileFilter = file[file.neighborhood_group == borough]
fileFilter['Distance'] = "0"
fileFilter = fileFilter.reset_index()
print('\nPlease wait while the program locates the Airbnbs in the area.')
for row in range (0, len(fileFilter)):
    fileFilter.loc[row, 'Distance'] = geodesic(coordinates, (fileFilter.loc[row, 'latitude'], fileFilter.loc[row, 'longitude'])).miles
lowest = fileFilter['Distance'].min()
print ("\nThis location is in " + borough + ". " + "The closest Airbnb is " + str(round(lowest, 2)) + " miles away.\n\nHere are the types and quantities of Airbnb units currently available in the borough.")

#Display bar graph of the room types in the borough of the user input location.       
roomCount = fileFilter.room_type.value_counts()
plt.figure(figsize=(10,7))
plt.xlabel("Room Type",fontsize=18)
plt.ylabel("Number Available in " + borough, fontsize=18)
plt.title("Types of Rooms Available in " +borough, fontsize=24)
bar = plt.bar(roomCount.index, height = roomCount, width = 0.8)
plt.show(bar)

#Filter dataset to only include Airbnbs within the user's desired radius.
radius = input('Within how many miles of this location would you like to stay? Please enter a number greater than 0 and less than or equal to 5.\n>>')
while type(radius) == str:
    try:
        radius = float(radius)
        if radius <= 0 or radius >5:
           radius = 'string' 
    except:
        print('Invalid entry. Please try again.')
        radius = input('Within how many miles of this location would you like to stay? Please enter a number greater than 0 and less than 5.\n>>')
fileFilter = fileFilter[fileFilter.Distance <= radius]

#Create numpy array of the average price of each Airbnb type within the radius.
neighCount = fileFilter.neighborhood.value_counts()
neighIndex = list(neighCount.index)
roomTypes = ['Entire home/apt', 'Private room', 'Shared room', 'Hotel room']
neighMeans = []
for x in neighIndex:
    Filter1 = fileFilter[fileFilter.neighborhood == x]
    E, P, S, H = 0, 0, 0, 0
    E = Filter1[Filter1.room_type == 'Entire home/apt']['price'].mean()
    P = Filter1[Filter1.room_type == 'Private room']['price'].mean()
    S = Filter1[Filter1.room_type == 'Shared room']['price'].mean()
    H = Filter1[Filter1.room_type == 'Hotel room']['price'].mean()
    neighMeans.append([round(E, ndigits = 2), round(P, ndigits = 2), round(S, ndigits = 2), round(H, ndigits = 2)])
meansArray = np.array(neighMeans, dtype=float)
meansArray = np.nan_to_num(meansArray)

#Display heatmap of average Airbnb price by neighborhood and Airbnb type.
print('\nHere is a heatmap of the average price of each room type in neighborhoods within the radius you would like to stay in.')
ax = sns.heatmap(meansArray, vmax = 500, xticklabels = roomTypes, yticklabels = neighIndex, annot = True, fmt=".2f", cmap="YlGnBu")
ax.set_title('Average Price of Each Room Type in Nearby Neighborhoods')
plt.show(ax)

#Define function to inquire user of what type of Airbnb they would like to stay in.
def preference():
    prefValid = False
    while prefValid == False:
        roomPref = input('What type of Airbnb would you like to stay in? \nEnter E for Entire home/apt.\nEnter P for Private room.\nEnter S for Shared room.\nEnter H for Hotel room.\n>>')
        if roomPref.lower() == 'e':
            roomPref = 'Entire home/apt'
            prefValid = True
        elif roomPref.lower() == 'p':
            roomPref = 'Private room'
            prefValid = True
        elif roomPref.lower() == 's':
            roomPref = 'Shared room'
            prefValid = True
        elif roomPref.lower() == 'h': 
            roomPref = 'Hotel room'
            prefValid = True
        else:
            print('Invalid entry. Please try again.')
        return roomPref
    
#Filter dataset to only include the Airbnbs of the user's preferred type.
Filter2 = fileFilter[fileFilter.room_type == preference()]
while Filter2.empty == True:
    print('\nThere are no Airbnbs of that room type available in this area. Please try again.')
    Filter2 = fileFilter[fileFilter.room_type == preference()]
    
#Display upto 10 Airbnbs within the user's specifications.
Filter2 = Filter2.sort_values(by=['price'])
Filter2 = Filter2.reset_index()
Filter3 = Filter2.drop(columns = ['level_0', 'index', 'room_type', 'neighborhood_group', 'name', 'latitude', 'longitude', 'host_name', 'number_of_reviews'])
print('Here are upto 10 Airbnbs that fall under your specifications, sorted by ascending room price.\n')
print(Filter3[0:10])

#Provide detailed information on the Airbnb that the user selects.
number = int(input('\nPlease enter the number of the Airbnb that you are interested in staying in for more information.\n>>'))
while number not in range(0,10) or number >= len(Filter3):
    print('This is not a valid number. Please try again.')
    number = int(input('\nPlease enter the number of the Airbnb(1-9) that you are interested in staying in for more information.\n>>'))
specs = Filter2.loc[number]
address = geolocator.reverse([specs['latitude'], specs['longitude']])
address = address.address
print('The address of this Airbnb is:\n' + address + '.\nIt is ' + str(round(specs['Distance'], 2)) + ' miles away from the location you entered.\nIt is hosted by ' + specs['host_name'] + ' and has been reviewed ' + str(specs['number_of_reviews']) + ' times.\n\nPlease enjoy your stay in New York City!')




