from flask import Flask, render_template, request, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
import pandas as pd
from bokeh.embed import components
import json
from scatter_chart import make_houseplot, show_estimates
from commute_estimate import estimate_commutes
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)

###############################################################################
##Pull in the private data
###############################################################################
with open('config.json', 'r') as infile:
    config = json.loads(infile.read())
dbloc = config['dbloc']
jsapikey="https://maps.googleapis.com/maps/api/js?key={}&callback=initMap".format(config['jsapikey'])
times = ['morning', 'evening']

## person A has an office in town so you have to avoid highways to avoid HOV
AOffice = config['AOffice']
BOffice = config['BOffice']

##DB Config
app.config['SQLALCHEMY_DATABASE_URI'] = dbloc
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



###############################################################################
##Define DB schema in here because that's what flasksqlalchemy wants?
###############################################################################
class houses(db.Model):
    __tablename__ = "houses"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String, unique=True)  


class drivetimes(db.Model):
    __tablename__ = "drivetimes"
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.String)
    dest = db.Column(db.String)
    starttime = db.Column(db.DateTime)
    drivetime = db.Column(db.Integer)
    
class offices(db.Model):
    __tablename__ = "offices"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String)
    person = db.Column(db.String)

        
class Driveestimates(db.Model):
    __tablename__ = "Driveestimates"
    id = db.Column(db.Integer)
    address = db.Column(db.String, primary_key=True)
    AOffice_guess = db.Column(db.Integer)
    AOffice_traffic = db.Column(db.Integer)
    BOffice_guess = db.Column(db.Integer)
    BOffice_traffic = db.Column(db.Integer)
    date_time = db.Column(db.DateTime, primary_key=True)
    

###############################################################################
##Track Times on Select Houses
###############################################################################
@app.route('/')
def index():
    #Determine the selected feature
    current_time = request.args.get("time")
    if current_time == None:
        current_time = "morning"
    # Create the plot
    conn = db.engine.connect().connection
    data= pd.read_sql("SELECT * FROM drivetimes", con=conn)
    dests =list(data.start.unique())
    observedplot = make_houseplot(data, current_time)
	# Embed plot into HTML via Flask Render
    oscript, odiv = components(observedplot)
    return render_template("chart.html", oscript=oscript, odiv=odiv,
                           times=times,  current_time=current_time,
                           dests = dests,  AOffice = AOffice)

@app.route('/add_house', methods=['GET', 'POST'])
def add_house():
    if request.method == 'GET':
        return render_template('add_house.html')
    else:
        address=request.form["Address"]
        print(address)
        toinsert = houses(address=address)
        db.session.add(toinsert)
        db.session.commit()
        return '<h1> House added </h1>'



###############################################################################
##Track Routes on Select Houses
###############################################################################
@app.route('/surface_maps')
def surface_maps():
    conn = db.engine.connect().connection
    data= pd.read_sql("SELECT * FROM drivetimes", con=conn)
    dests =list(data.start.unique())
    return render_template("drivemaps.html", dests=dests, mapskey= jsapikey,
                           title = "Surface Routes", hwy_val='true')
    
@app.route('/hwy_maps')
def hwy_maps():
    conn = db.engine.connect().connection
    data= pd.read_sql("SELECT * FROM drivetimes", con=conn)
    dests =list(data.start.unique())
    return render_template("drivemaps.html", dests=dests, mapskey= jsapikey,
                           title = "Highway Routes", hwy_val='false')    
###############################################################################
##Track Routes on Select Houses
###############################################################################
@app.route('/all_estimates')
def all_estimates():
    conn = db.engine.connect().connection
    data= pd.read_sql("SELECT * FROM Driveestimates", con=conn)
    p=show_estimates(data)
    oscript, odiv = components(p)
    return render_template('estimates.html', oscript=oscript, odiv=odiv)

@app.route('/add_house_estimate', methods=['GET', 'POST'])
def add_house_estimate():
    if request.method == 'GET':
        return render_template('add_house.html')
    else:
        address=request.form["Address"]
        print(address)
            ### set a basic morning time and evening times for commutes
        morning_commute = datetime(2018, 9,25, 7)
        evening_commute = datetime(2018, 9,25, 17)
        commutes = [morning_commute, evening_commute]
        for time in commutes:
        ##ne, new DriveEstimate
            ne=estimate_commutes(address, time)
            toinsert = Driveestimates(address=address,\
                                      AOffice_guess=ne['AOffice_guess'],\
                                      AOffice_traffic=ne['AOffice_traffic'],\
                                      BOffice_guess=ne['BOffice_guess'],\
                                      BOffice_traffic=ne['BOffice_traffic'],\
                                      date_time=ne['date_time'])
            db.session.add(toinsert)
            db.session.commit()
        return '<h1> House added for estimate </h1>'   
# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=5000, debug=True)
    
#cool maps straight from google https://developers.google.com/maps/documentation/javascript/examples/directions-simple