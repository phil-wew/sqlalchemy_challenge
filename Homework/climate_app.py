import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request



#######################################
#Database Setup#
#######################################

engine = create_engine('sqlite:///hawaii.sqlite')

# reflect database #
Base = automap_base()

#reflect Tables

Base.prepare(engine, reflect=True)


#reference to tables

Measurement = Base.classes.measurement

Station = Base.classes.station



# #######################################
# #Flask Setup
# #######################################

app = Flask(__name__)




# #######################################
# #Flask Routes
# #######################################

@app.route('/')
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f'/api/v1.0/<start>` and `/api/v1.0/<start>/<end>'
    )


@app.route(f'/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    """Return rain fall for last year"""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_rain = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > last_year).\
    order_by(Measurement.date).all()

    rain = {date: prcp for date, prcp in year_rain}

    return jsonify(rain)


   
@app.route(f'/api/v1.0/stations')
def stations():
    session = Session(engine)

    """Return stations list"""

    station_list = session.query(Station.name, Station.station).all()

    stations = list(np.ravel(station_list))

    return jsonify(stations)


@app.route(f"/api/v1.0/tobs")
def active_station():
    session= Session(engine)

    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    active_stations = session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.tobs).desc()).all()

    most_active = active_stations[0][0]

    top_station=session.query(Measurement.station, Measurement.tobs).\
    filter(Measurement.station == most_active).\
    filter(Measurement.date >= last_year).\
    order_by(Measurement.date).all()

    tobs = list(np.ravel(top_station))    

    return jsonify(tobs)




if __name__ == "__main__":
    app.run(debug=True)   