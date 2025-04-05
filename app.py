from flask import Flask, render_template, request
import pandas as pd
import sqlite3
import os
from shapely import wkt
from math import radians, cos, sin, sqrt, atan2

app = Flask(__name__)

DB_FILE = "structures.db"
CSV_FILE = "Corporate_Structures_20250312.csv"

def create_database():
    if not os.path.exists(DB_FILE):
        df = pd.read_csv(CSV_FILE)

        def get_centroid_lat(geom):
            try:
                shape = wkt.loads(geom)
                return shape.centroid.y
            except:
                return None

        def get_centroid_lon(geom):
            try:
                shape = wkt.loads(geom)
                return shape.centroid.x
            except:
                return None

        df['centroid_lat'] = df['MULTIPOLYGON'].apply(get_centroid_lat)
        df['centroid_lon'] = df['MULTIPOLYGON'].apply(get_centroid_lon)

        conn = sqlite3.connect(DB_FILE)
        df.to_sql("structures", conn, index=False, if_exists="replace")
        conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))

@app.route("/")
def index():
    create_database()
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM structures WHERE centroid_lat IS NOT NULL AND centroid_lon IS NOT NULL", conn)
    conn.close()

    nearest = None
    if lat is not None and lon is not None:
        df["distance_km"] = df.apply(
            lambda row: haversine(lat, lon, row["centroid_lat"], row["centroid_lon"]), axis=1)
        nearest = df.loc[df["distance_km"].idxmin()].to_dict()

    return render_template("index.html", data=df.to_dict(orient="records"), nearest=nearest, user_coords=(lat, lon))

if __name__ == "__main__":
    app.run(debug=True)
