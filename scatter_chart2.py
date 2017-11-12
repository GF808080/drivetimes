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


def personify(x):
    if x.start == 'Washington, DC 20007':
        return config['personA']
    elif x.dest == 'Washington, DC 20007':
        return config['personA']
    elif x.start == '22330 Glenn Dr, Sterling, VA 20164':
        return config['personB']
    elif x.dest =='22330 Glenn Dr, Sterling, VA 20164':
        return config['personB']
    else:
        pass


def make_houseplot(data, time):
    ## Format the data properly
    data['person']=data.apply(lambda x: personify(x), axis=1)
    houses =list(data.start.unique())
    data['realtime']=pd.to_datetime(data.starttime)
    data['hour'] =data.realtime.apply(lambda x: int(x.hour))
    if str(time).lower() == 'morning':
        pdata = data[(data.hour >= 6) & (data.hour < 9)]
    elif str(time).lower() == 'evening':
        pdata = data[(data.hour >= 16) & (data.hour < 19)]
    ##Tooltips
    source = ColumnDataSource(data=dict(
    x=list(data['start']),
    y=list(data['drivetime'],
    desc=['A', 'b', 'C', 'd', 'E'],
    ))
    
    hover = HoverTool(tooltips=[
        ("person", "$person"),
        ("date", "$realtime"),
        ("drivetime", "$drivetime"),
    ])
    ##establish plot
    p = figure(title="Drive Times by House for {time}".format(time=time),\
               x_range=houses, y_range=(0, 75), plot_width=800, plot_height=1200)

    #for personA
    data_pa= pdata[pdata.person==config['personA']]
    print(data_pa.head())
    p.circle(data_pa['start'], data_pa['drivetime'], fill_color='#440154',\
             size=10)
    #for personB
    data_pb = pdata[pdata.person==config['personB']]
    p.diamond(data_pb['start'], data_pb['drivetime'], fill_color='#35B778',\
              size=10)
    
    p.xaxis.major_label_text_font_size="12pt"
    p.xaxis.major_label_orientation = math.pi/2
    return(p)

if __name__ == "__main__":
    ### Get my Data and get a subset
    engine = create_engine(dbloc, echo=True)
    connection = engine.connect()
    data= pd.read_sql("SELECT * FROM drivetimes", con=connection)
    p = make_houseplot(data, 'Evening')
    show(p)

