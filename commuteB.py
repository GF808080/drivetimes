#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 18:30:47 2017

@author: sentinel
"""

import googlemaps
from datetime import datetime
import json
from sqlSetup import Houses, DriveTimes
from sqlalchemy import create_engine

## Pull in private data
with open('config.json', 'r') as infile:
    config = json.loads(infile.read())
dbloc = config['dbloc']
maps_key = config['maps_key']
workdir = config['workdir']

#set up sqlalchemy stuff
engine = create_engine(config['dbloc'], echo=True)
connection = engine.connect()

#set google key
gmaps = googlemaps.Client(key=maps_key)

### get destinations
BOffice = config['BOffice']
myHouses =connection.execute(Houses.select())


for house in myHouses:
    house=house[1]
    #get best estimate
    result = gmaps.distance_matrix(house, BOffice, mode="driving",
                                             language="en-US",
                                            units="imperial",
                                            departure_time=datetime.now(),
                                            traffic_model="best_guess")

    print(house+"====>"+BOffice)
    try:
        #extract the duration and insert into db
        print("Best Guess Duration")
        estimate = result['rows'][0]['elements'][0]['duration']['text']
        estimate = int(estimate.replace(' mins', ''))
        print(estimate)
        ins = DriveTimes.insert().values(start = house,\
                                         dest=BOffice,\
                                         starttime=datetime.now(),\
                                         drivetime=estimate)
        connection.execute(ins)
        
    except:
        print("Error on {}".format(house))