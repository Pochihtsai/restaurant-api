import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ─────────────────────────
# 基本設定
# ─────────────────────────
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("環境變數 GOOGLE_API_KEY 未設定")

DEFAULT_LANG = "zh-TW"
DEFAULT_REGION = "TW"


def _json_or_error(resp):
    """
    安全解析上游 JSON；若非 200 一併回傳上游內容，方便排錯。
    回傳 (data, err, http_code)
    """
    try:
        data = resp.json()
    except Exception:
        return None, {"error": "upstream_non_json", "raw": resp.text}, 502
    if resp.status_code != 200:
        return None, {
            "error": "upstream_error",
            "status_code": resp.status_code,
            "response": data
        }, resp.status_code
    return data, None, 200


# ─────────────────────────
# 1) Geocoding：地址 → 座標
# ─────────────────────────
@app.route("/getLocationCoordinates")
def get_location_coordinates():
    address = request.args.get("address")
    if not address:
        return jsonify({"error": "missing address"}), 400

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_API_KEY,
        "language": DEFAULT_LANG,
        "region": DEFAULT_REGION,
    }
    resp = requests.get(url, params=params, timeout=20)
    data, err, code = _json_or_error(resp)
    return jsonify(data if data is not None else err), code


# ─────────────────────────────────────────────────────────────
# 2) Weather：Google Maps Platform Weather（hours/days lookup）
#    Query:
#      lat, lon        必填
#      timesteps       可選：hourly / daily（預設 hourly）
#      languageCode    可選：預設 zh-TW
#      units_system    可選：METRIC / IMPERIAL（預設 METRIC）
# ─────────────────────────────────────────────────────────────
@app.route("/getWeatherByCoordinates")
def get_weather_by_coordinates():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "missing lat/lon"}), 400

    timesteps = request.args.get("timesteps", "hourly").lower()  # hourly / daily
    language = request.args.get("languageCode", DEFAULT_LANG)
    units_system = request.args.get("units_system", "METRIC").upper()  # METRIC / IMPERIAL

    base = "https://weather.googleapis.com/v1/forecast"
    endpoint = f"{base}/days:lookup" if timesteps == "daily" else f"{base}/hours:lookup"

    params = {
        "location.latitude": lat,
        "location.longitude": lon,
        "languageCode": language,
        "units_system": units_system,   # 注意底線寫法
        "key": GOOGLE_API_KEY,
    }

    resp = requests.get(endpoint, params=params, timeout=20)
    try:
        data = resp.json()
    except Exception:
        return jsonify({"error": "upstream_non_json", "raw": resp.text}), 502

    if resp.status_code != 200:
        # 為避免洩漏金鑰，回傳時移除 key
        safe_params = {k: v for k, v in params.items() if k != "key"}
        return jsonify({
            "error": "google_weather_error",
            "status_code": resp.status_code,
            "endpoint": endpoint,
            "params": safe_params,
            "response": data
        }), resp.status_code

    return jsonify(data), 200


# ─────────────────────────
# 3) Places Nearby：附近餐廳
# ─────────────────────────
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
        "language": DEFAULT_LANG,
    }
    resp = requests.get(url, params=params, timeout=20)
    data, err, code = _json_or_error(resp)
    return jsonify(data if data is not None else err), code


# ─────────────────────────
# 4) Places Details：餐廳詳細
# ─────────────────────────
@app.route("/getRestaurantDetails")
def get_restaurant_details():
    place_id = request.args.get("place_id")
    if not place_id:
        return jsonify({"error": "missing place_id"}), 400

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_API_KEY,
        "language": DEFAULT_LANG,
    }
    resp = requests.get(url, params=params, timeout=20)
    data, err, code = _json_or_error(resp)
    return jsonify(data if data is not None else err), code


# ─────────────────────────
# 5) Directions：路線建議
# ─────────────────────────
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
        "language": DEFAULT_LANG,
        "region": DEFAULT_REGION,
    }
    resp = requests.get(url, params=params, timeout=20)
    data, err, code = _json_or_error(resp)
    return jsonify(data if data is not None else err), code


# ─────────────────────────
# 健康檢查
# ─────────────────────────
@app.route("/")
def home():
    return "Smart Restaurant Assistant API is running."


# ─────────────────────────
# 啟動
# ─────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
