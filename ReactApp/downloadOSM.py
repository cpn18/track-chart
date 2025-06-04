import os
import sys
import math
import requests
import time
from tqdm import tqdm

# NH bounding box
# Jon - this is the lat/long bounding box you were talking about.
min_lat, max_lat = 42.7, 45.3
min_lon, max_lon = -72.6, -70.6

# zoom levels to download (8–11)
zoom_levels = range(0, 20)

TILEMAP = {
    "light": {
        "source": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "output": "public/tiles/osm/{style}"
    },
    "dark": {
        "source": "https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
        "output": "public/tiles/osm/{style}"
    },
    "standard": {
        "source": "http://tiles.openrailwaymap.org/{style}/{z}/{x}/{y}.png",
        "output": "public/tiles/orm/{style}"
    }
}

def latlon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return x, y

# avoid 403 forbidden -- need to have a proper user agent
headers = {
    "User-Agent": "PiRail/1.0 (https://gitlab.cs.unh.edu/pirail-2025-capstone/pirail-2025-capstone) Contact: dsb1041"
}

def download_box(style, lat1, lon1, lat2, lon2):
    min_lat = min(lat1, lat2)
    max_lat = max(lat1, lat2)
    min_lon = min(lon1, lon2)
    max_lon = max(lon1, lon2)

    for z in zoom_levels:
        x_start, y_start = latlon_to_tile(max_lat, min_lon, z)
        x_end, y_end = latlon_to_tile(min_lat, max_lon, z)

        for x in tqdm(range(x_start, x_end + 1), desc=f"Zoom {z}"):
            for y in range(y_start, y_end + 1):
                download_tile(style, x, y, z)

def download_point(style, lat, lon):
    for z in zoom_levels:
        x, y = latlon_to_tile(lat, lon, z)
        download_tile(style, x, y, z)

def download_tile(style, x, y, z):


    output_dir = TILEMAP[style]["output"].format(style=style, z=z, x=x, y=y)
    path = os.path.join(output_dir, str(z), str(x))
    filename = os.path.join(path, f"{y}.png")

    if not os.path.exists(filename):
        try:
            url = TILEMAP[style]["source"].format(style=style, z=z, x=x, y=y)
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                os.makedirs(path, exist_ok=True)
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"✅ Saved: {filename}")
                time.sleep(0.01)  # delay to avoid rate limiting
            else:
                # user-agent isn't working, so we get a 403 forbidden error - OSM is mad at us
                print(f"❌ Failed {z}/{x}/{y}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Error {z}/{x}/{y}: {e}")

def download_known(style, filename):
    with open(filename) as infile:
        for line in infile:
            line = line.strip().split()
            if line[1] == "K":
                try:
                    download_point(style, float(line[2]), float(line[3]))
                except ValueError:
                    pass

if __name__ == "__main__":
    if len(sys.argv) == 6:
        download_box(
            sys.argv[1],
            float(sys.argv[2]),
            float(sys.argv[3]),
            float(sys.argv[4]),
            float(sys.argv[5]),
        )
    elif len(sys.argv) == 4:
        download_point(
            sys.argv[1],
            float(sys.argv[2]),
            float(sys.argv[3]),
        )
    elif len(sys.argv) == 3 and sys.argv[2].endswith(".csv"):
        download_known(
            sys.argv[1],
            sys.argv[2]
        )
    else:
        print("USAGE: error")
