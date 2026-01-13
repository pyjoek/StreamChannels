from flask import Flask, render_template, request, abort
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
M3U_PATH = os.path.join(BASE_DIR, "index.m3u")
COUNTRIES_PATH = os.path.join(BASE_DIR, "countries_metadata.json")


# -----------------------------
# Blocked channels list
# -----------------------------
BLOCKED_CHANNELS = [
    # france
    '00s Replay',
    'France 2 (1080p)', 'France 2 HD (720p)', 'France 3 HD (720p)',
    'France 4 HD (720p)', 'France 5 (1080p)', 'France 5 HD (720p)',
    'France Inter', 'Franceinfo',
    'TV5Monde France Belgique Suisse Monaco (1080p) [Geo-blocked]',

    # italy (sample – keep adding if needed)
    'Pluto TV Anime Italy (720p)',
    'Pluto TV Cinema Italiano Italy (720p)',
    'Rai 1 HD (720p)', 'Rai 2 HD',
    'Rai News 24 HD',

    # german
    'Comedy & Shows Germany (1080p)',
    'Nick Germany (1080p) [Geo-blocked]',
]


# -----------------------------
# Helpers
# -----------------------------
def load_countries():
    if not os.path.exists(COUNTRIES_PATH):
        abort(500, "countries_metadata.json not found")
    with open(COUNTRIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_m3u():
    if not os.path.exists(M3U_PATH):
        abort(500, "index.m3u not found")
    with open(M3U_PATH, "r", encoding="utf-8") as f:
        return f.read()


def parse_m3u(m3u_text, countries):
    lines = m3u_text.splitlines()
    channels = []

    for i in range(len(lines)):
        line = lines[i].strip()

        if line.startswith("#EXTINF:"):
            name = line.split(",", 1)[1].strip() if "," in line else ""
            url = lines[i + 1].strip() if i + 1 < len(lines) else ""

            country_code = None
            country_name = "Unknown"
            flag = "🏳️"

            if 'tvg-country="' in line:
                country_code = line.split('tvg-country="')[1].split('"')[0].lower()

            if country_code and country_code.upper() in countries:
                meta = countries[country_code.upper()]
                country_name = meta.get("country", "Unknown")
                flag = meta.get("flag", "🏳️")

            channels.append({
                "name": name,
                "url": url,
                "country_code": country_code,
                "country_name": country_name,
                "flag": flag
            })

    return channels


# -----------------------------
# Routes
# -----------------------------
@app.route("/channels")
def all_channels():
    q = request.args.get("q", "").lower()

    countries = load_countries()
    m3u_text = load_m3u()
    channels = parse_m3u(m3u_text, countries)

    # ❌ Filter Pluto
    channels = [
        c for c in channels
        if not c["name"].lower().startswith("pluto")
    ]

    # ❌ Filter Gecko
    channels = [
        c for c in channels
        if "gecko" not in c["name"].lower()
    ]

    # ❌ Filter "blocked"
    channels = [
        c for c in channels
        if "blocked" not in c["name"].lower()
    ]

    # ❌ Hard blacklist
    channels = [
        c for c in channels
        if c["name"] not in BLOCKED_CHANNELS
    ]

    # 🔍 Search
    if q:
        channels = [
            c for c in channels
            if q in c["name"].lower()
        ]

    return render_template("channels.html", channels=channels)


@app.route("/show")
def show_channels():
    search = request.args.get("search", "").upper()

    countries = load_countries()
    m3u_text = load_m3u()
    channels = parse_m3u(m3u_text, countries)

    if search:
        channels = [
            c for c in channels
            if search in c["name"].upper()
        ]

    return render_template(
        "show.html",
        channels=channels,
        countries=countries,
        search=search
    )


@app.route("/player")
def player():
    url = request.args.get("url")
    name = request.args.get("name")
    return render_template("watch.html", url=url, name=name)


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
