import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

@app.route("/getNearbyRestaurants")
def get_nearby_restaurants():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    keyword = request.args.get("keyword", "")
    radius = request.args.get("radius", 1000)

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "keyword": keyword,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    return jsonify(response.json())

@app.route("/")
def home():
    return "API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
