import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def climate_anal():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/station<br/>"
        f"Most Active Station - Temperature for the Last Year: /api/v1.0/tobs<br/>"
        f"Station Temperature from start to end dates in format(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"Station Temperature for one year from date in format(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
# Create our session (link) from Python to the DB
    session = Session(engine)
# Query precipitation
    sel = [Measurement.station, Measurement.date, Measurement.tobs]
    precipqry = session.query(*sel).all()

    session.close()
 
    # Convert list of tuples into normal list
    precipitation = []
    for station, date, tobs in precipqry:
        dict_precip = {}
        dict_precip["Station"] = station
        dict_precip["Date"] = date
        dict_precip["Precipitation"] = tobs
        precipitation.append(dict_precip)

    return jsonify(precipitation)


@app.route("/api/v1.0/station")
def station():
# Create our session (link) from Python to the DB
    session = Session(engine)
# Query station table
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    stationqry = session.query(*sel).all()

    session.close()

# Convert list of tuples into normal list
    stations = []
    for station, name, lat, lon, elev in stationqry:
        dict_stations = {}
        dict_stations["Station"] = station
        dict_stations["Name"] = name
        dict_stations["Latitude"] = lat
        dict_stations["Longitude"] = lon
        dict_stations["Elevation"] = elev
        stations.append(dict_stations)

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
# Create our session (link) from Python to the DB
    session = Session(engine)
# find the most active station (i.e. what station has the most rows?
    session.query(Measurement.station, func.count(Measurement.date)).group_by(Measurement.station).\
    order_by(func.count(Measurement.date).desc()).all()
    most_active = session.query(Measurement.station).first

# Retrieve and convert date, calculate 1 year prior date
    rec_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    most_rec_date = dt.datetime.strptime(rec_date.date, '%Y-%m-%d')
    yr_date = most_rec_date - dt.timedelta(days=365)

# Query 1 year's observations for the most active station
    for station in most_active():
        sel = [Measurement.date, Measurement.tobs]
        yr_qry = session.query(*sel).filter(Measurement.date >= yr_date).all()

    session.close()

# Convert list of tuples into normal list
    all_tobs = []
    for date, tobs in yr_qry:
        dict_tobs = {}
        dict_tobs["Station"] = station
        dict_tobs["Date"] = date
        dict_tobs["Tobs"] = tobs
        all_tobs.append(dict_tobs)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>/<stop>")
def get_temp_start_stop(start, stop):
# Create our session (link) from Python to the DB
    session = Session(engine)

# Select the first and last dates of the data set for the range of dates
    start_date = session.query(func.min(Measurement.date)).first()[0]
    end_date = session.query(func.max(Measurement.date)).first()[0]

# Query min, avg, max observations
    mamqry = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)).all()

    session.close()

# Convert list of tuples into normal list
    all_tobs = []
    for min, avg, max in mamqry:
        dict_tobs = {}
        dict_tobs["Min"] = min
        dict_tobs["Avg"] = avg
        dict_tobs["Max"] = max
        all_tobs.append(dict_tobs)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def get_temp_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

# Select the first date of the data set for the start of the range of dates
    start_date = session.query(func.min(Measurement.date)).first()[0]

# Query min, avg, max observations
    mamqry = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

# Convert list of tuples into normal list
    all_tobs = []
    for min, avg, max in mamqry:
        dict_tobs = {}
        dict_tobs["Min"] = min
        dict_tobs["Avg"] = avg
        dict_tobs["Max"] = max
        all_tobs.append(dict_tobs)

    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)
