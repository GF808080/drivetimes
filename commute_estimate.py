#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 18:29:52 2017

@author: sentinel
"""

import googlemaps
from datetime import datetime
import json
from sqlalchemy import create_engine
import os

os.chdir(r'/home/sentinel/drivetimes')
## Pull in private data
with open('config.json', 'r') as infile:
    config = json.loads(infile.read())
dbloc = config['dbloc']
maps_key = config['maps_key']
workdir = config['workdir']
logfile = config['logfile']


#set google key
gmaps = googlemaps.Client(key=maps_key)

#estimate a morning commute on a Tuesday during a school-year

# Set offices
AOffice = config['AOffice']
BOffice = config['BOffice']
ofices = [AOffice, BOffice]

##########
## Function for app
##########
def estimate_commutes(new_address, time):
        commuteA = gmaps.distance_matrix(new_address, AOffice, mode="driving",
                                            language="en-US",
                                            units="imperial",
                                            departure_time=time,
                                            avoid='highways',
                                            traffic_model="best_guess")
        print(time.isoformat()+" For A")
        #extract the duration and insert into db
        try:
            estimate = commuteA['rows'][0]['elements'][0]['duration']['text']
            AOffice_guess = int(estimate.replace(' mins', ''))
            ### Traffic
            estimate = commuteA['rows'][0]['elements'][0]['duration_in_traffic']['text']
            AOffice_traffic = int(estimate.replace(' mins', ''))
        except:
            AOffice_guess='failed run'
            AOffice_traffic='failed run'
            print('failed commuteA')
            
        commuteB = gmaps.distance_matrix(new_address, BOffice, mode="driving",
                                            language="en-US",
                                            units="imperial",
                                            departure_time=time,
                                            traffic_model="best_guess")
        print(time.isoformat()+" For B")
        #extract the duration and insert into db
        try:
            estimate = commuteB['rows'][0]['elements'][0]['duration']['text']
            BOffice_guess = int(estimate.replace(' mins', ''))
            ### Traffic
            estimate = commuteB['rows'][0]['elements'][0]['duration_in_traffic']['text']
            BOffice_traffic = int(estimate.replace(' mins', ''))
        except:
            BOffice_traffic = 'failed run'
            BOffice_guess = 'failed run'
            print('failed commute b')
        
        Driveestimates={'address':new_address,\
                                         'AOffice_guess':AOffice_guess,\
                                         'AOffice_traffic':AOffice_traffic,\
                                         'BOffice_guess':BOffice_guess,\
                                         'BOffice_traffic':BOffice_traffic,\
                                         'date_time':time}
        return(Driveestimates)

        

##########
## Function independent of app
##########        
def ext_estimate_commutes(new_address):
    from sqlSetup import DriveEstimates
    #set up sqlalchemy stuff
    engine = create_engine(config['dbloc'], echo=True)
    connection = engine.connect()
    ### set a basic morning time and evening times for commutes
    morning_commute = datetime(2018, 9,25, 7)
    evening_commute = datetime(2018, 9,25, 17)
    commutes = [morning_commute, evening_commute]
    for commute in commutes:
        commuteA = gmaps.distance_matrix(new_address, AOffice, mode="driving",
                                            language="en-US",
                                            units="imperial",
                                            departure_time=commute,
                                            avoid='highways',
                                            traffic_model="best_guess")
        print(commute.isoformat()+" For A")
        #extract the duration and insert into db
        try:
            estimate = commuteA['rows'][0]['elements'][0]['duration']['text']
            AOffice_guess = int(estimate.replace(' mins', ''))
            ### Traffic
            estimate = commuteA['rows'][0]['elements'][0]['duration_in_traffic']['text']
            AOffice_traffic = int(estimate.replace(' mins', ''))
        except:
            AOffice_guess=None
            AOffice_traffic=None
            print('failed commuteA')
            
        commuteB = gmaps.distance_matrix(new_address, BOffice, mode="driving",
                                            language="en-US",
                                            units="imperial",
                                            departure_time=commute,
                                            traffic_model="best_guess")
        print(commute.isoformat()+" For B")
        #extract the duration and insert into db
        try:
            estimate = commuteB['rows'][0]['elements'][0]['duration']['text']
            BOffice_guess = int(estimate.replace(' mins', ''))
            ### Traffic
            estimate = commuteB['rows'][0]['elements'][0]['duration_in_traffic']['text']
            BOffice_traffic = int(estimate.replace(' mins', ''))
        except:
            BOffice_traffic = None
            BOffice_guess = None
            print('failed commute b')
        
        ins = DriveEstimates.insert().values(address = new_address,\
                                         AOffice_guess=AOffice_guess,\
                                         AOffice_traffic=AOffice_traffic,\
                                         BOffice_guess=BOffice_guess,\
                                         BOffice_traffic=BOffice_traffic,\
                                         date_time=commute)
        #insAddress = Houses.insert().values(address=new_address)
        connection.execute(ins)

if __name__ == '__main__':
    houses =['2602 AMANDA CT, VIENNA, VA 22180','7602 Brittany Parc Ct 22043']
    for house in houses:
        print(house)   
        ext_estimate_commutes(house)