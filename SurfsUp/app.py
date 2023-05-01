# Import the dependencies.
import os 
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
SQLITE_PATH = os.path.join("Resources", "hawaii.sqlite")


os.chdir(os.path.dirname(os.path.realpath(__file__)))
engine = create_engine(f"sqlite:///{SQLITE_PATH}")

# reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session link from Python to the DB
session = Session(engine)

# Set up Flask
app = Flask(__name__)

# Define the homepage
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
#Create session link
    session = Session(engine)

    """Return a dictionary of date:prcp values for the last 12 months of data"""
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_ago = (dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query the database for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert the query results to a dictionary
    prcp_data = {}
    for date, prcp in results:
        prcp_data[date] = prcp

    return jsonify(prcp_data)
session.close()

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
#Create session link
    session = Session(engine)

    """Return a list of stations"""
    
    # Query all Stations
    stations = session.query(Station.name, Station.station).all()

    # convert list to dictionary
    stations_dict = dict(stations)

    return jsonify(stations_dict)
session.close()

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    #Create session link
    session = Session(engine)

    """Return a list of temperature observations for the most active station in the last 12 months of data"""
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_ago = (dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query the database for the last 12 months of temperature observations for the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).\
        order_by(func.count().desc()).first().station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= year_ago).all()

    # Convert the query results to a list of dictionaries
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temperature'] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)
session.close()


# Define the start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)


    """Return a JSON list of the minimum temperature, the average temperature, 
    and the maximum temperature for all the dates greater than or equal to the start date"""
    # Query the database
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()
    # Create a list of dictionaries
    start_date_list = []
    for min_temp, avg_temp, max_temp in results:
        dict = {}
        dict["Minimum Temperature"] = min_temp
        dict["Average Temperature"] = avg_temp
        dict["Maximum Temperature"] = max_temp
        start_date_list.append(dict)
    return jsonify(start_date_list) 

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
 # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the maximum temperature for the dates from start date to end date inclusive"""
    # Query the database
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()
    
    # Create a list of dictionaries
    start_end_date_list = []
    for min_temp, avg_temp, max_temp in results:
        dict = {}
        dict["Minimum Temperature"] = min_temp
        dict["Average Temperature"] = avg_temp
        dict["Maximum Temperature"] = max_temp
        start_end_date_list.append(dict)

    return jsonify(start_end_date_list)

# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
