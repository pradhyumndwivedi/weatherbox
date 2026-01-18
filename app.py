from flask import Flask, render_template, request, g
import time
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import load_model
from datetime import date, timedelta, datetime
import urllib.request
import json
import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from geopy.geocoders import Nominatim
import math

app = Flask(__name__)

def decimal_to_dms(decimal_degrees, is_latitude=True):
    degrees = int(decimal_degrees)
    minutes_float = abs(decimal_degrees - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    direction = ""
    if is_latitude:
        if decimal_degrees >= 0:
            direction = "N"
        else:
            direction = "S"
    else:  
        if decimal_degrees >= 0:
            direction = "E"
        else:
            direction = "W"
    return f"{abs(degrees)}° {minutes}' {seconds:.2f}\" {direction}"

def convert_24h_to_12h(time_24h_str):
    dt_object = datetime.strptime(time_24h_str, "%H:%M")
    time_12h_str = dt_object.strftime("%I:%M %p")
    return time_12h_str

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def dowork(request):
    scaler = MinMaxScaler(feature_range=(0, 1))
    API_KEY = "PUT YOUR API KEY HERE"
    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    LOCATION = "Raipur"
    UNIT_GROUP = "metric"
    CONTENT_TYPE = "json"
    INCLUDE = "hours"
    DATALIST = np.loadtxt('temp1.csv', delimiter=',')
    NEWDATAS = np.loadtxt('temp2.csv', delimiter=',')
    geolocator = Nominatim(user_agent="my_reverse_geocoding_app")
    if len(DATALIST) == 0:
        DATALIST = NEWDATAS = np.zeros(shape=(1,4))
        yr = g.request_start_time.tm_year
        mon = g.request_start_time.tm_mon
        day = g.request_start_time.tm_mday
        END_DATE = date(yr,mon,day)
        START_DATE = END_DATE - timedelta(days=5)
        request_url = (f"{BASE_URL}{urllib.parse.quote(LOCATION)}/{START_DATE}/{END_DATE}" 
            f"?unitGroup={UNIT_GROUP}&contentType={CONTENT_TYPE}" 
            f"&include={INCLUDE}&key={API_KEY}")
        try:
            response = urllib.request.urlopen(request_url)
            data = response.read()
            response.close()
            weather_data = json.loads(data.decode('utf-8'))
            days = weather_data.get('days')
            for i in range(len(days)):
                for j in range(len(days[i]['hours'])):
                    hour = days[i]['hours'][j]
                    DATALIST = np.append(DATALIST, [[hour['temp'], hour['humidity'], hour['windspeed'], hour['pressure']]], axis=0)
            DATALIST = DATALIST[-99:] 
            incdata = request.get_json()
            newdata = [incdata['temp'], incdata['humidity'], incdata['windspeed'], incdata['pressure']]
            DATALIST = np.append(DATALIST, [newdata], axis=0)
            NEWDATAS = np.append(NEWDATAS, [newdata], axis=0)
            NEWDATAS = np.delete(NEWDATAS, 0, axis=0)
        except urllib.error.HTTPError as e:
            print("HTTP Error:", e.code, e.reason)
        except urllib.error.URLError as e:
            print("URL Error:", e.reason)
    else:
        incdata = request.get_json()
        newdata = [incdata['temp'], incdata['humidity'], incdata['windspeed'], incdata['pressure']]
        if NEWDATAS.shape == (4,): 
            NEWDATAS = NEWDATAS.reshape(1,-1)
        else: pass
        if len(NEWDATAS) < 6:
            NEWDATAS = np.append(NEWDATAS, [newdata], axis=0)
            avg = []
            sm = 0
            for i in range(4):
                for data in NEWDATAS:
                    sm += data[i]
                avg.append(sm)
                sm = 0
            avg = [item/len(NEWDATAS) for item in avg]
            DATALIST = DATALIST[:-1]
            DATALIST = np.append(DATALIST, [avg], axis=0)
        else:
            DATALIST = DATALIST[-99:]
            DATALIST = np.append(DATALIST, [newdata], axis=0)
            NEWDATAS = np.array([newdata])
    np.savetxt('temp1.csv', DATALIST, delimiter=',', fmt='%f')
    np.savetxt('temp2.csv', NEWDATAS, delimiter=',', fmt='%f')
    scaled_data = scaler.fit_transform(DATALIST).reshape(4,100,1)
    with open('weather_type_classifier.pkl', 'rb') as file:
        loaded_type_model = pickle.load(file)
    loaded_model = load_model('weather_forecast_model.keras')
    typelist = ['Breezy', 'Clear', 'Drizzle', 'Dry', 'Foggy', 'Humid', 'Rain', 'Windy']
    predicted_values = loaded_model.predict(scaled_data, verbose=0)
    predicted_values = np.array(predicted_values)
    scnew = scaler.fit_transform(np.append(DATALIST[-99:0], [NEWDATAS[-1]], axis=0))[-1]
    current_label = typelist[loaded_type_model.predict(scnew.reshape(1,-1))[0]]
    predicted_labels = [typelist[loaded_type_model.predict(predicted_values.reshape(1,4))[0]]]
    predicted_values = scaler.inverse_transform(predicted_values.reshape(1,4))
    pred = predicted_values
    predlist = np.array(pred)
    DATALISTCPY = DATALIST
    for i in range(9):
        DATALISTCPY = DATALISTCPY[-99:]
        DATALISTCPY = np.append(DATALISTCPY, pred, axis=0)
        scdata = scaler.fit_transform(DATALISTCPY).reshape(4,100,1)
        pred = loaded_model.predict(scdata, verbose=0)
        pred = np.array(pred)
        predicted_labels.append(typelist[loaded_type_model.predict(pred.reshape(1,4))[0]])
        pred = scaler.inverse_transform(pred.reshape(1,4))
        predlist = np.append(predlist, pred, axis=0)
    predlist = predlist.tolist()
    req = request.get_json()
    hour = g.request_start_time.tm_hour
    minute = g.request_start_time.tm_min
    currtime = convert_24h_to_12h(f"{hour}:{minute}")
    timelabels = []
    for i in range(10):
        if hour < 23:
            hour += 1
        else: 
            hour = 0
        timelabels.append(f"{hour}:00")
    timelabels = [convert_24h_to_12h(item) for item in timelabels]
    predlist = np.round(predlist).astype(int).tolist()
    current_data = np.round(DATALIST[-1]).astype(int).tolist()
    coordinates = f"{req['lat']/1000000}, {req['long']/1000000}"
    location = geolocator.reverse(coordinates)
    locationstr = ""
    if location:
        address_components = location.raw.get('address', {})
        city = address_components.get('city', '')
        state = address_components.get('state', '')
        locationstr = f"{city}, {state}"
    else:
        locationstr = "Unknown Location"
    dms_latitude = decimal_to_dms(req['lat']/1000000, is_latitude=True)
    dms_longitude = decimal_to_dms(req['long']/1000000, is_latitude=False)
    dispdata = [req['humidity'], req['pressure'], req['windspeed'], req['altitude'], truncate(req['lat']/1000000, 4), truncate(req['long']/1000000, 4)]
    currhour = g.request_start_time.tm_hour
    colorstr = " "
    currday = currhour < 18 and currhour > 4
    if currhour > 4 and currhour < 6: colorstr = "from-orange-300 via-blue-950 to-gray-950"
    elif currhour > 6 and currhour < 10: colorstr = "from-yellow-400 via-blue-400 to-blue-800"
    elif currhour > 10 and currhour < 17: colorstr = "from-blue-600 to-blue-400"
    elif currhour > 17 and currhour < 19: colorstr = "from-yellow-600 to-blue-950"
    elif currhour > 19 and currhour < 23: colorstr = "from-slate-800 to-gray-950"
    elif currhour > 0 and currhour < 4: colorstr = "from-slate-800 to-gray-950"
    return predlist, predicted_labels, current_data, current_label, f"{dms_latitude}, {dms_longitude}", locationstr, timelabels, currtime, dispdata, currday, colorstr

@app.before_request
def record_request_time():
    g.request_start_time = time.localtime()

predlist = [[0,0,0,0]]
predlabels = [' ']
currdata = [0,0,0,0]
currlabel = " "
location = " "
timelabels = [0,0,0,0]
locationstr = " "
connected = False
currtime = " "
dispdata = [0,0,0,0,0,0]
day = False
colorstr = " "

@app.route('/', methods=['GET', 'POST'])
def home():
    global predlist, predlabels, currdata, currlabel, location, timelabels, connected, locationstr, currtime, dispdata, day, colorstr
    if request.method == 'POST':
        predlist, predlabels, currdata, currlabel, location, locationstr, timelabels, currtime, dispdata, day, colorstr = dowork(request)
        connected = True
        return {'mssg': 'Request Accepted!'}
    return render_template('home.html', connected=connected, predlist=predlist, predlabels=predlabels, currdata=currdata, currlabel=currlabel, location=location, locationstr=locationstr, timelabels=timelabels, currtime=currtime, dispdata=dispdata, day=day, colorstr=colorstr)

@app.route('/end', methods=['GET', 'POST'])
def homer():
    if request.method == 'POST':
        print(request.get_json())
        return {'mssg': 'So nice to meet you buddy!'}
    return {'err': 'No get requests allowed mate!'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
