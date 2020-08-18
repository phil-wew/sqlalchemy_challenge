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

        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"

        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"

        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"

        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates >= to the start date <br/>"
        f"<br/>"

        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between <br/>"
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



@app.route(f'/api/v1.0/<start>')
@app.route(f'/api/v1.0/<start>/<end>')
def stats (start=None, end=None):
    session= Session(engine)

    """ Return TMIN,TAVG,TMAX"""

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]


    if not end:
        observations = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temperatures = list(np.ravel(observations))
        return jsonify(temperatures)

    
    end_obs = session.query(*sel).\
        filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    temperatures = list(np.ravel(end_obs))
    return jsonify(temperatures)


# * Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.

# * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` 
# for all dates greater than and equal to the start date.

# * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` 
# for dates between the start and end date inclusive.



if __name__ == "__main__":
    app.run(debug=True)   