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
        "User-Agent": "ConiShadowWeatherProxy/1.0 (conishadoww@gmail.com)"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None

def get_condition_text(code):
    conditions = {
        0: "Clear",
        1: "Mostly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Heavy Drizzle",
        56: "Light Freezing Drizzle",
        57: "Heavy Freezing Drizzle",
        61: "Light Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        66: "Light Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Light Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Light Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",
        85: "Light Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Light Hail",
        99: "Thunderstorm with Heavy Hail",
    }
    return conditions.get(code, "Unknown")

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
        return jsonify({"error": "Please provide 'city' or 'lat' and 'lon'"}), 400

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        response = requests.get(url, timeout=5)
        data = response.json()
        weather = data.get("current_weather", {})

        condition_code = weather.get("weathercode")
        condition_text = get_condition_text(condition_code)

        result = {
            "temp_c": weather.get("temperature"),
            "windspeed_kph": round(weather.get("windspeed", 0) * 1.60934, 1),
            "condition_code": condition_code,
            "condition_text": condition_text,
            "time": weather.get("time"),
            "location": city if city else f"{lat},{lon}"
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Failed to fetch weather", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
