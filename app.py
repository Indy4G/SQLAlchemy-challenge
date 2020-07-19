from flask import Flask, jsonify
app = Flask(__name__)

import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine,reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

@app.route("/")
def home():
    return (
        f"<h1>Hawaii Climate Data API(V1) Home Page</h1></br>"
        f"Avilable Routes:</br></br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/**Enter-Start-Date (yyy-dd-mm)**</br>"
        f"/api/v1.0/**Enter-Start-Date (yyy-dd-mm)**/**Enter-End-Date (yyy-dd-mm)**"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)


    # Design a query to retrieve the last 12 months of precipitation data and plot the results:
    # Calculate the date 1 year ago from the last data point in the database
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    startDate = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    data = session.query(Measurement.date,Measurement.prcp)\
    .filter(Measurement.date >= startDate).order_by(Measurement.date).all()
    
    # Close session
    session.close()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    prcp_df = pd.DataFrame(data)
    prcp_df = prcp_df.dropna()
    prcp_df = prcp_df.rename(columns={'prcp':'precipitation'})

    # Sort the dataframe by date
    prcp_df = prcp_df.sort_values(by=['date'])

    # Turn the dataframe into a dictionary
    prcp_dict = dict(zip(prcp_df.date, prcp_df.precipitation))
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query
    stations = session.query(Measurement.station, func.count(Measurement.station))\
    .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Close session
    session.close()
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Queries
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    startDate = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    temps = session.query(Measurement.tobs).filter(Measurement.date >= startDate).all()

    # Close session
    session.close()
    
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def tobs_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Queries
    top_station = 'USC00519281'
    temps = session.query(\
              func.min(Measurement.tobs),\
              func.avg(Measurement.tobs),\
              func.max(Measurement.tobs))\
              .filter(Measurement.station == top_station)\
              .filter(Measurement.date >= start).all()
    
    # Close session
    session.close()
    
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Queries
    top_station = 'USC00519281'
    temps = session.query(\
              func.min(Measurement.tobs),\
              func.avg(Measurement.tobs),\
              func.max(Measurement.tobs))\
              .filter(Measurement.station == top_station)\
              .filter(Measurement.date >= start)\
              .filter(Measurement.date <= end).all()
    
    # Close session
    session.close()
    
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=False)