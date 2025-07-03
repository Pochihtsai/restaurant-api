import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# 環境變數（建議從 Render dashboard 設定）
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")  # 需申請 OpenWeather API 金鑰

# 1️⃣ 取得地理座標
@app.route("/getLocationCoordinates")
def get_location_coordinates():
    address = request.args.get("address")
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    return jsonify(response.json())

# 2️⃣ 查詢天氣
@app.route("/getWeatherByCoordinates")
def get_weather_by_coordinates():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "zh_tw"
    }
    response = requests.get(url, params=params)
    return jsonify(response.json())

# 3️⃣ 附近餐廳搜尋
>>>>>>> 5876667 (更新 main.py：補齊 API 路由)
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
<<<<<<< HEAD

    response = requests.get(url, params=params)
    return jsonify(response.json())

@app.route("/")
def home():
    return "API is running."

=======
    response = requests.get(url, params=params)
    return jsonify(response.json())

# 4️⃣ 餐廳詳細資料
@app.route("/getRestaurantDetails")
def get_restaurant_details():
    place_id = request.args.get("place_id")
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    return jsonify(response.json())

# 5️⃣ 路線建議
@app.route("/getTravelAdvice")
def get_travel_advice():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    mode = request.args.get("mode", "driving")

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    return jsonify(response.json())

# ✅ 頁面確認用
@app.route("/")
def home():
    return "Smart Restaurant Assistant API is running."

# 🔄 啟動伺服器
>>>>>>> 5876667 (更新 main.py：補齊 API 路由)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
