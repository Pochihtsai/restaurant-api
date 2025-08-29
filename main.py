import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 環境變數
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")  # 同一把金鑰用於 Geocoding/Places/Weather

# 1️⃣ 取得地理座標（Geocoding）
@app.route("/getLocationCoordinates")
def get_location_coordinates():
    address = request.args.get("address")
    if not address:
        return jsonify({"error": "missing address"}), 400

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_API_KEY,
        "language": "zh-TW",
        "region": "TW",
    }
    r = requests.get(url, params=params, timeout=20)
    return jsonify(r.json()), r.status_code


# 2️⃣ 查詢天氣（Google Maps Platform Weather）
#    參數：
#      lat, lon       必填
#      timesteps      選填：hourly / daily（預設 hourly）
#      languageCode   選填：預設 zh-TW
#      units          選填：metric / imperial（預設 metric）
@app.route("/getWeatherByCoordinates")
def get_weather_by_coordinates():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "missing lat/lon"}), 400

    timesteps = request.args.get("timesteps", "hourly").lower()  # hourly / daily
    language = request.args.get("languageCode", "zh-TW")
    units = request.args.get("units", "metric")                  # metric / imperial

    # ✅ 使用 action-style 端點 + 正確參數名稱
    base = "https://weather.googleapis.com/v1/forecast"
    endpoint = f"{base}/days:lookup" if timesteps == "daily" else f"{base}/hours:lookup"

    params = {
        "location.latitude": lat,
        "location.longitude": lon,
        "languageCode": language,
        "units": units,
        "key": GOOGLE_API_KEY,
    }

    r = requests.get(endpoint, params=params, timeout=20)
    # 嘗試解析 JSON（上游若有錯誤也多半是 JSON 格式）
    try:
        data = r.json()
    except Exception:
        return jsonify({"error": "upstream_non_json", "raw": r.text}), 502

    if r.status_code != 200:
        return jsonify({
            "error": "google_weather_error",
            "status_code": r.status_code,
            "endpoint": endpoint,
            "params": {k: v for k, v in params.items() if k != "key"},
            "response": data
        }), r.status_code

    return jsonify(data), 200


# 3️⃣ 附近餐廳搜尋（Places Nearby）
@app.route("/getNearbyRestaurants")
def get_nearby_restaurants():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "missing lat/lon"}), 400

    keyword = request.args.get("keyword", "")
    radius = request.args.get("radius", 1000)

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "keyword": keyword,
        "key": GOOGLE_API_KEY,
        "language": "zh-TW",
    }
    r = requests.get(url, params=params, timeout=20)
    return jsonify(r.json()), r.status_code


# 4️⃣ 餐廳詳細資料（Places Details）
@app.route("/getRestaurantDetails")
def get_restaurant_details():
    place_id = request.args.get("place_id")
    if not place_id:
        return jsonify({"error": "missing place_id"}), 400

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_API_KEY,
        "language": "zh-TW",
    }
    r = requests.get(url, params=params, timeout=20)
    return jsonify(r.json()), r.status_code


# 5️⃣ 路線建議（Directions）
@app.route("/getTravelAdvice")
def get_travel_advice():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    if not origin or not destination:
        return jsonify({"error": "missing origin/destination"}), 400

    mode = request.args.get("mode", "driving")

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": GOOGLE_API_KEY,
        "language": "zh-TW",
        "region": "TW",
    }
    r = requests.get(url, params=params, timeout=20)
    return jsonify(r.json()), r.status_code


# ✅ 健康檢查
@app.route("/")
def home():
    return "Smart Restaurant Assistant API is running."


# 🔄 啟動伺服器
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
