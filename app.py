# from flask import Flask, render_template, request
# import requests
# import json

# app = Flask(__name__)

# M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"

# # Load country metadata once
# with open("countries_metadata.json", "r", encoding="utf-8") as f:
#     COUNTRIES = json.load(f)

# def parse_m3u(m3u_text):
#     """
#     Simple M3U parser for version 0.0.4
#     """
#     lines = m3u_text.splitlines()
#     channels = []

#     for i in range(len(lines)):
#         line = lines[i]
#         if line.startswith("#EXTINF:"):
#             name = line.split(",")[-1].strip()
#             url = lines[i + 1].strip() if i + 1 < len(lines) else ""
#             # Attempt to get country code from EXTINF attributes
#             country_code = None
#             if 'tvg-country="' in line:
#                 country_code = line.split('tvg-country="')[1].split('"')[0]
#             country = COUNTRIES.get(country_code, {})
#             channels.append({
#                 "name": name,
#                 "url": url,
#                 "country_code": country_code,
#                 "country_name": country.get("country", "Unknown"),
#                 "flag": country.get("flag", "🏳️")
#             })
#     return channels

# @app.route("/")
# def index():
#     r = requests.get(M3U_URL, timeout=15)
#     r.raise_for_status()

#     channels = parse_m3u(r.text)
#     return render_template("index.html", channels=channels)

# @app.route("/player")
# def player():
#     return render_template(
#         "player.html",
#         url=request.args.get("url"),
#         name=request.args.get("name")
#     )

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"

# Load country metadata once
with open("countries_metadata.json", "r", encoding="utf-8") as f:
    COUNTRIES = json.load(f)

def parse_m3u(m3u_text):
    """
    Simple M3U parser for version 0.0.4
    """
    lines = m3u_text.splitlines()
    channels = []

    for i in range(len(lines)):
        line = lines[i]
        if line.startswith("#EXTINF:"):
            name = line.split(",")[-1].strip()
            url = lines[i + 1].strip() if i + 1 < len(lines) else ""

            country_code = None
            if 'tvg-country="' in line:
                country_code = line.split('tvg-country="')[1].split('"')[0]

            country = COUNTRIES.get(country_code, {})

            channels.append({
                "name": name,
                "url": url,
                "country_code": country_code,
                "country_name": country.get("country", "Unknown"),
                "flag": country.get("flag", "🏳️")
            })

    return channels

@app.route("/")
def index():
    r = requests.get(M3U_URL, timeout=15)
    r.raise_for_status()

    channels = parse_m3u(r.text)

    # ❌ Filter blocked channels
    channels = [
        c for c in channels
        if not c["name"].lower().startswith("pluto")
        and "gecko" not in c["name"].lower()
        and "blocked" not in c["name"].lower()
    ]

    # 🔍 Search magic
    q = request.args.get("q", "").lower()
    if q:
        channels = [c for c in channels if q in c["name"].lower()]

    return render_template("index.html", channels=channels)

@app.route("/player")
def player():
    return render_template(
        "player.html",
        url=request.args.get("url"),
        name=request.args.get("name")
    )

if __name__ == "__main__":
    app.run(debug=True)
