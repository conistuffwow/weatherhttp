from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def geocode_city(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "iOS6WeatherProxy/1.0 (your.email@example.com)"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None

@app.route('/weather')
def get_weather():
    city = request.args.get("city", "").strip()
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if city:
        lat, lon = geocode_city(city)
        if lat is None or lon is None:
            return jsonify({"error": f"City '{city}' not found"}), 404
    elif lat and lon:
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({"error": "Invalid latitude or longitude"}), 400
    else:
        return jsonify({"error": "Please provide 'city' or 'lat' and 'lon' parameters"}), 400

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        response = requests.get(url, timeout=5)
        data = response.json()
        weather = data.get("current_weather", {})

        result = {
            "temp_c": weather.get("temperature"),
            "windspeed_kph": round(weather.get("windspeed", 0) * 1.60934, 1),
            "condition_code": weather.get("weathercode"),
            "time": weather.get("time"),
            "location": city if city else f"{lat},{lon}"
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Failed to fetch weather", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
