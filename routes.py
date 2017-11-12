from flask import Flask, render_template, request
import pandas as pd
from bokeh.embed import components
from sqlalchemy import create_engine
import json
from scatter_chart import make_houseplot





app = Flask(__name__)
## Pull in private data
with open('config.json', 'r') as infile:
    config = json.loads(infile.read())
dbloc = config['dbloc']

jsapikey="https://maps.googleapis.com/maps/api/js?key={}&callback=initMap".format(config['jsapikey'])
times = ['morning', 'evening']


# Index page
@app.route('/')
def index():
    #Determine the selected feature
    current_time = request.args.get("time")
    if current_time == None:
        current_time = "morning"
    # Create the plot
    engine = create_engine(dbloc, echo=True)
    connection = engine.connect()
    data= pd.read_sql("SELECT * FROM drivetimes", con=connection)
    dests =list(data.start.unique())
    plot = make_houseplot(data, current_time)
	# Embed plot into HTML via Flask Render
    script, div = components(plot)
    return render_template("chart.html", script=script, div=div,
                           times=times,  current_time=current_time,
                           dests = dests, mapskey= jsapikey)


# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=5000, debug=True)
#cool maps straight from google https://developers.google.com/maps/documentation/javascript/examples/directions-simple