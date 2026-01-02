import requests

url = "https://raw.githubusercontent.com/TVGarden/tv-garden-channel-list/main/channels/compressed/countries_metadata.json"

r = requests.get(url)

# See readable JSON
print(r.text)

# Or parsed object
data = r.json()
print(data.keys())
