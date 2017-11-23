#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 16:07:52 2017

@author: sentinel
"""

import pandas as pd
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import HoverTool
from sqlalchemy import create_engine
import math
import json

## Pull in private data
with open('config.json', 'r') as infile:
    config = json.loads(infile.read())
dbloc = config['dbloc']

## Pick colors for people
colormap ={config['personA']:'red', config['personB']:'blue'}

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


def make_houseplot(data, time):
    ## Format the data properly
    data['person']=data.apply(lambda x: personify(x), axis=1)
    data['realtime']=pd.to_datetime(data.starttime)
    data['hour'] =data.realtime.apply(lambda x: int(x.hour))
    data['color'] = data.person.apply(lambda x: colormap[x])

    if str(time).lower() == 'morning':
        houses =list(data.start.unique())
        pdata = data[(data.hour >= 6) & (data.hour < 9)]
        pdata['house']=pdata.start
    elif str(time).lower() == 'evening':
        houses = list(data.dest.unique())
        pdata = data[(data.hour >= 16) & (data.hour < 19)]
        pdata['house']=pdata.dest
        
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
    
    p.scatter("start", "drivetime", color='color', source=source, size=10,\
              legend='person')
    p.add_tools(hover)
    p.xaxis.major_label_text_font_size="12pt"
    p.xaxis.major_label_orientation = math.pi/2
       
    return(p) 

if __name__ == "__main__":
    ### Get my Data and get a subset
    engine = create_engine(dbloc, echo=True)
    connection = engine.connect()
    data= pd.read_sql("SELECT * FROM drivetimes", con=connection)
    p = make_houseplot(data, 'Morning')
    show(p)

