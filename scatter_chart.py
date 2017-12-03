#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:07:52 2017

@author: sentinel
"""

import pandas as pd
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import HoverTool, Legend
from bokeh.layouts import row
from sqlalchemy import create_engine
import math
import json

## Pull in private data
with open('config.json', 'r') as infile:
    config = json.loads(infile.read())
dbloc = config['dbloc']

## Pick colors for people
colormapPerson ={config['personA']:'red', config['personB']:'blue'}
colormapCommute ={'evening':'orange', 'morning':'blue'}

## Sort offices and people by destination
def personify(x):
    if x.start == config['AOffice']:
        return config['personA']
    elif x.dest == config['AOffice']:
        return config['personA']
    elif x.start == config['BOffice']:
        return config['personB']
    elif x.dest ==config['BOffice']:
        return config['personB']
    else:
        pass

def id_drive(time):
    if (time.hour >= 6) & (time.hour < 9):
        return 'morning'
    elif (time.hour >= 16) & (time.hour < 19):
        return 'evening'
    else:
        return None

def make_houseplot(data, time):
    ## Format the data properly
    data['person']=data.apply(lambda x: personify(x), axis=1)
    data['realtime']=pd.to_datetime(data.starttime)
    data['hour'] =data.realtime.apply(lambda x: int(x.hour))
    data['color'] = data.person.apply(lambda x: colormapPerson[x])

    if str(time).lower() == 'morning':
        houses =list(data.start.unique())
        pdata = data[(data.hour >= 6) & (data.hour < 9)]
        pdata['house']=pdata.start
        pdata['tripstart']=pdata.start
        
    elif str(time).lower() == 'evening':
        houses = list(data.dest.unique())
        pdata = data[(data.hour >= 16) & (data.hour < 19)]
        pdata['house']=pdata.dest
        pdata['tripstart']=pdata.dest
        
    ##establish column data source
    source = ColumnDataSource(pdata)
    
    ##establish plot
    p = figure(title="Drive Times by House for {time}".format(time=time),\
               x_range=houses, y_range=(0, 75), plot_width=1000, plot_height=800,\
               tools=['hover'])
    hover = HoverTool(tooltips=[("TripTaken", "@starttime"),\
                                ("Start", "@start"),\
                                ("Dest", "@dest"),\
                                ("Person", "@person")])
    
    p.scatter("tripstart", "drivetime", color='color', source=source, size=10,\
              legend='person')
    p.add_tools(hover)
    p.xaxis.major_label_text_font_size="12pt"
    p.xaxis.major_label_orientation = math.pi/2
       
    return(p) 

def show_estimates(data):
    ### Clean up the data for everything
    data.columns = ['id', 'address', config['personA']+'_guess',config['personA']+'_traffic', config['personB']+'_guess',\
               config['personB']+'_traffic', 'date_time']
    data['cleandate']=data.date_time.apply(lambda x: pd.to_datetime(x))
    data['hour'] = data.cleandate.apply(lambda x: int(x.hour))
    data['commute'] =data.cleandate.apply(lambda x: id_drive(x))
    data['color'] = data.commute.apply(lambda x: colormapCommute[x])
    houses =list(data.address.unique())
    
    ## Sub-divide data
    amdata = data[data['hour']<=12]
    print(amdata.head())
    pmdata = data[data['hour']>=12]
    sourceAM = ColumnDataSource(amdata)
    sourcePM= ColumnDataSource(pmdata)
    
    ## Make Tooltips
    ##establish amplot
    p1 = figure(title="Morning Drive Estimates From Google",\
               x_range=houses, y_range=(0, 75))
    
    ama = p1.scatter("address", config['personA']+'_traffic', color='color',\
              marker='inverted_triangle', source=sourceAM, size=10,)
    
    amb = p1.scatter("address", config['personB']+'_guess', color='color',\
              marker='x', source=sourceAM, size=10)
    
    ## add the pretties
    legend = Legend(items=[
                (config['personA'], [ama]),\
                (config['personB'], [amb]),
                 ], location=(0, -30))
    
    p1.xaxis.major_label_text_font_size="12pt"
    p1.xaxis.major_label_orientation = math.pi/2
    p1.add_layout(legend, 'right')
    
    ##establish amplot
    p2 = figure(title="Evening Drive Estimates From Google",\
               x_range=houses, y_range=(0, 75))
    pma = p2.scatter("address", config['personA']+'_traffic', color='color',\
              marker='inverted_triangle', source=sourcePM, size=10)
    
    pmb = p2.scatter("address", config['personB']+'_guess', color='color',\
              marker='x', source=sourcePM, size=10)    
    
    ## add the pretties
    legend2 = Legend(items=[
                (config['personA'], [pma]),\
                (config['personB'], [pmb]),
                 ], location=(0, -30))
    
    p2.xaxis.major_label_text_font_size="12pt"
    p2.xaxis.major_label_orientation = math.pi/2
    p2.add_layout(legend2, 'right')
    
    ##
    return p1, p2


if __name__ == "__main__":
    ### Get my Data and get a subset
    engine = create_engine(dbloc, echo=True)
    connection = engine.connect()
#    data= pd.read_sql("SELECT * FROM drivetimes", con=connection)
#    p = make_houseplot(data, 'Morning')
    data= pd.read_sql("SELECT * FROM driveestimates", con=connection)
    p= show_estimates(data)