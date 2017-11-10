from flask import Flask, render_template, request
import pandas as pd
from bokeh.charts import BoxPlot, Histogram, Scatter
from bokeh.embed import components
from sklearn.datasets import load_iris
import numpy as np
app = Flask(__name__)
#from bokeh.io import output_file, show, save #comment me out for app running

#
##current_feature_name = "sepal length (cm)"
#p=BoxPlot(iris_df, values=current_feature_name, title='BoxPlot',\
#           plot_width=600,plot_height=400) 
#
#p.yaxis.axis_label='This is a y label'
#
#save(p, 'mytest.html')
#           plot_width=600,plot_height=400, color='species',\
#           label='species',legend='bottom_right') 
#
#show(p)

# Load the Iris Data Set
iris = load_iris()
iris_df = pd.DataFrame(data= np.c_[iris['data'], iris['target']],
                     columns= iris['feature_names'] + ['Species'])

feature_names = iris_df.columns[0:-1].values.tolist()

# Create the main plot
def create_figure(df, current_feature_name):
    p=BoxPlot(df, values=current_feature_name, title='BoxPlot',\
           plot_width=600,plot_height=400, label='Species')
    p.xaxis.axis_label = current_feature_name
    p.yaxis.axis_label = 'Count'
    return p

# Index page
@app.route('/')
def index():
	# Determine the selected feature
	current_feature_name = request.args.get("feature_name")
	if current_feature_name == None:
		current_feature_name = "sepal length (cm)"

	# Create the plot
	plot = create_figure(iris_df, current_feature_name)
		
	# Embed plot into HTML via Flask Render
	script, div = components(plot)
	return render_template("chart.html", script=script, div=div,
		feature_names=feature_names,  current_feature_name=current_feature_name)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=5000, debug=True)
"""

### code for including maps
flask google maps example
from flask_googlemaps import Map

@app.route("/")
def mapview():
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    return render_template('example.html', mymap=mymap)

Template:
in head:
    {{mymap.js}}
in body:
    {{mymap.html}}

### code for giving colors
from bokeh.palettes import brewer

    #   Create a list of colors per treatment given a dataframe and 
    #        column representing the treatments.
    #         
    #        Args:
    #            df - dataframe to get data from
    #            treatment_col - column to use to get unique treatments.
    #                 
    #        Inspired by creating colors for each treatment 
    #        Rough Source: http://bokeh.pydata.org/en/latest/docs/gallery/brewer.html#gallery-brewer
    #        Fine Tune Source: http://bokeh.pydata.org/en/latest/docs/gallery/iris.html
    # Get the number of colors we'll need for the plot.
    
def color_list_generator(df, treatment_col):
    colors = brewer["Spectral"][len(df[treatment_col].unique())]
 
    # Create a map between treatment and color.
    colormap = {i: colors[k] for k,i in enumerate(df[treatment_col].unique())}
 
    # Return a list of colors for each value that we will be looking at.
    return [colormap[x] for x in df[treatment_col]]
"""