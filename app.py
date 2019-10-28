# Dependencies
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, desc, select
from flask import Flask,jsonify

# Database Setup
engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

@app.route("/")
def home():
    return(
        "Available Routes:<br/>"
        "/api/v1.0/precipitation Precipitation by Station and Date<br/>"
        "/api/v1.0/station Stations<br/>"
        "/api/v1.0/tobs Temperatures for the previous year<br/>"
        "/api/v1.0/<start> Minimum temperature, the average temperature, and the max temperature for a given start date<br/>"
        "/api/v1.0/<start>/<end> Minimum temperature, the average temperature, and the max temperature for between start date< and end date<br/>"
    )

def precipitation_results_to_list(results):
    measures = []
    for date,precipitation,station in results:
        measure = {}
        measure["date"] = date
        measure["precipitation"] = precipitation
        measure["station"] = station
        print(measure)
        measures.append(measure)
    return measures

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp.label('precipitation'),Measurement.station).all()
    session.close()
    return jsonify(precipitation_results_to_list(results))

def station_results_to_list(results):
    stations = []
    for station,name,latitude,longitude,elevation in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        print(station_dict)
        stations.append(station_dict)
    return stations

@app.route("/api/v1.0/station")
def stations():
    session = Session(engine)
    results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()
    return jsonify(station_results_to_list(results))

def string_to_date(text):
    return dt.datetime(int(text[:4]),int(text[5:7]),int(text[8:]))

def one_year_before(last_date):
    first_date = last_date - dt.timedelta(days=365)
    return str(first_date)[:10]

def temp_results_to_list(results):
    temperatures = []
    for date,temperature,station in results:
        measure = {}
        measure["date"] = date
        measure["temperature"] = temperature
        measure["station"] = station
        print(measure)
        temperatures.append(measure)
    return temperatures

@app.route("/api/v1.0/tobs")
    session = Session(engine)
    max_date = engine.execute('SELECT MAX(date) FROM measurement').fetchall()
    last_date = string_to_date(max_date[0][0])
    first_date = one_year_before(last_date)
    results = session.query(Measurement.date,Measurement.tobs.label('temperature'),Measurement.station).where(Measurement.date >= first_date).all()
    session.close()
    return jsonify(temp_results_to_list(results))

def check_date(text):
    try:
        date = string_to_date(text)
        return True
    except:
        return False

def temp_results_to_statistics(results):
    statistics = {}
    statistics["Minimum Temperature"] = results[0][0]
    statistics["Average Temperature"] = round(results[0][1],2)
    statistics["Maximum Temperature"] = results[0][2]
    statistics["From Date"] = results[0][3]
    statistics["To Date"] = results[0][4]
    print(statistics)
    return statistics

@app.route("/api/v1.0/<start>")
    def temperatures_by_start_date(start):
        good_start = check_date(start)
        if good_start:
            session = Session(engine)
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs),func.min(Measurement.date),func.max(Mesurement.date)).filter(Measurement.date >= start).all()
            session.close()
            return jsonify(temp_results_to_statistics(results))
        else:
            return jsonify({"error": f"{start} is not a date."}), 404

@app.route("/api/v1.0/<start>/<end>")
    def temperatures_by_start_date(start):
        good_start = check_date(start)
        good_end = check_date(end)
        if good_start and good_end:
            session = Session(engine)
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs),func.min(Measurement.date),func.max(Mesurement.date)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
            session.close()
            return jsonify(temp_results_to_statistics(results))
        else:
            return jsonify({"error": f"{start} and/or {end} is not a date."}), 404