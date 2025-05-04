import os
import math
import requests
import time
from tqdm import tqdm

# NH bounding box
# Jon - this is the lat/long bounding box you were talking about.
min_lat, max_lat = 42.7, 45.3
min_lon, max_lon = -72.6, -70.6

# zoom levels to download (8–11)
zoom_levels = range(1, 16)

# folder to store tiles
output_dir = "./public/tiles/light"

# OSM tile server
# https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png THIS IS FOR DARK MAPS
tile_url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

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

for z in zoom_levels:
    x_start, y_start = latlon_to_tile(max_lat, min_lon, z)
    x_end, y_end = latlon_to_tile(min_lat, max_lon, z)

    for x in tqdm(range(x_start, x_end + 1), desc=f"Zoom {z}"):
        for y in range(y_start, y_end + 1):
            url = tile_url.format(z=z, x=x, y=y)
            path = os.path.join(output_dir, str(z), str(x))
            os.makedirs(path, exist_ok=True)
            filename = os.path.join(path, f"{y}.png")

            if not os.path.exists(filename):
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        with open(filename, "wb") as f:
                            f.write(response.content)
                        print(f"✅ Saved: {filename}")
                        time.sleep(0.01)  # delay to avoid rate limiting
                    else:
                        # user-agent isn't working, so we get a 403 forbidden error - OSM is mad at us
                        print(f"❌ Failed {z}/{x}/{y}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"❌ Error {z}/{x}/{y}: {e}")
