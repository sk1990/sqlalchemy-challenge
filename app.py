import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

def calc_start_temps(start_date):
    return (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start_date)
        .all()
    )

def calc_temps(start_date, end_date):
    return (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start_date)
        .filter(Measurement.date <= end_date)
        .all()
    )

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of dates and percipitation observations from the last year<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of stations from the dataset<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of Temperature Observations (tobs) for the previous year<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- List of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- List of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range, inclusive<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_data_point = (
        session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    )
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    year_prcp = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= year_ago, Measurement.prcp != None)
        .order_by(Measurement.date)
        .all()
    )

    return jsonify(dict(year_prcp))

@app.route("/api/v1.0/stations")
def stations():
    session.query(Measurement.station).distinct().count()
    active_stations = (
        session.query(Measurement.station, func.count(Measurement.station))
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .all()
    )

    return jsonify(dict(active_stations))

@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_temp = (
        session.query(Measurement.tobs)
        .filter(Measurement.date >= year_ago, Measurement.station == "USC00519281")
        .order_by(Measurement.tobs)
        .all()
    )

    yr_temp = []
    for y_t in year_temp:
        yrtemp = {}
        yrtemp["tobs"] = y_t.tobs
        yr_temp.append(yrtemp)

    return jsonify(yr_temp)

@app.route("/api/v1.0/<start>")
def with_start(start):
    calc_start_temp = calc_start_temps(start)
    t_temp = list(np.ravel(calc_start_temp))

    t_min = t_temp[0]
    t_max = t_temp[2]
    t_avg = t_temp[1]
    t_dict = {
        "Minimum temperature": t_min,
        "Maximum temperature": t_max,
        "Avg temperature": t_avg,
    }

    return jsonify(t_dict)

@app.route("/api/v1.0/<start>/<end>")
def with_start_end(start, end):
    calc_temp = calc_temps(start, end)
    ta_temp = list(np.ravel(calc_temp))

    tmin = ta_temp[0]
    tmax = ta_temp[2]
    temp_avg = ta_temp[1]
    temp_dict = {
        "Minimum temperature": tmin,
        "Maximum temperature": tmax,
        "Avg temperature": temp_avg,
    }

    return jsonify(temp_dict)


if __name__ == "__main__":
    app.run(debug=True)



